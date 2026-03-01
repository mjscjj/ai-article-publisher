#!/usr/bin/env python3
"""
工作评价服务 - Evaluation Service
基于 DeepSeek 的智能评价系统

功能:
- 文章质量评估
- 选题价值评估
- 批量评价
- 评价历史查询
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

from core.deepseek_client import DeepSeekClient


class EvaluationService:
    """
    工作评价服务
    
    提供文章/选题的智能评价功能
    """
    
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', '43.134.234.4'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME', 'youmind'),
        'user': os.getenv('DB_USER', 'youmind'),
        'password': os.getenv('DB_PASSWORD', 'YouMind2026'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    def __init__(self, model: str = 'free'):
        """
        初始化服务
        
        Args:
            model: DeepSeek 模型类型 ('chat' | 'free' | 'v3')
        """
        if not MYSQL_AVAILABLE:
            raise ImportError("pymysql 未安装")
        
        self.client = DeepSeekClient(model=model)
        self.conn = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            self.conn = pymysql.connect(**self.DB_CONFIG)
            print("[EvaluationService] ✅ 数据库连接成功")
        except Exception as e:
            print(f"[EvaluationService] ❌ 数据库连接失败：{e}")
            raise
    
    def evaluate_article(self, title: str, content: str, 
                        save: bool = True) -> Dict[str, Any]:
        """
        评价文章
        
        Args:
            title: 文章标题
            content: 文章内容
            save: 是否保存到数据库
        
        Returns:
            评价结果
        """
        # 调用 DeepSeek 评价
        result = self.client.evaluate_article(title, content, evaluation_type='article')
        
        # 保存到数据库
        if save and 'error' not in result:
            self._save_evaluation('article', '', result)
        
        return result
    
    def evaluate_topic(self, title: str, description: str,
                      save: bool = True) -> Dict[str, Any]:
        """
        评价选题
        
        Args:
            title: 选题标题
            description: 选题描述
            save: 是否保存到数据库
        
        Returns:
            评价结果
        """
        result = self.client.evaluate_article(title, description, evaluation_type='topic')
        
        if save and 'error' not in result:
            self._save_evaluation('topic', '', result)
        
        return result
    
    def _save_evaluation(self, target_type: str, target_id: str, 
                        result: Dict[str, Any]):
        """保存评价记录到数据库"""
        cursor = self.conn.cursor()
        
        sql = """
        INSERT INTO evaluations (
            target_type, target_id, model_used, total_score, grade,
            content_score, structure_score, expression_score,
            viral_score, innovation_score,
            strengths, improvements, recommendation, comment
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        scores = result.get('scores', {})
        
        cursor.execute(sql, (
            target_type,
            target_id,
            result.get('model_used', ''),
            result.get('total_score', 0),
            result.get('grade', 'E'),
            scores.get('content', 0),
            scores.get('structure', 0),
            scores.get('expression', 0),
            scores.get('viral', 0),
            scores.get('innovation', 0),
            json.dumps(result.get('strengths', []), ensure_ascii=False),
            json.dumps(result.get('improvements', []), ensure_ascii=False),
            result.get('recommendation', ''),
            result.get('comment', '')
        ))
        
        self.conn.commit()
        cursor.close()
    
    def get_evaluation_history(self, target_type: str = None,
                              limit: int = 50) -> List[Dict]:
        """
        获取评价历史
        
        Args:
            target_type: 目标类型 ('article' | 'topic')
            limit: 返回数量
        
        Returns:
            评价记录列表
        """
        cursor = self.conn.cursor()
        
        if target_type:
            sql = """
            SELECT * FROM evaluations 
            WHERE target_type = %s 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            cursor.execute(sql, (target_type, limit))
        else:
            sql = """
            SELECT * FROM evaluations 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            cursor.execute(sql, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        
        # 解析 JSON 字段
        for row in results:
            if row.get('strengths'):
                row['strengths'] = json.loads(row['strengths'])
            if row.get('improvements'):
                row['improvements'] = json.loads(row['improvements'])
        
        return results
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        获取评价统计
        
        Args:
            days: 统计天数
        
        Returns:
            统计数据
        """
        cursor = self.conn.cursor()
        
        # 总数
        cursor.execute("""
            SELECT COUNT(*) as total FROM evaluations 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (days,))
        total = cursor.fetchone()['total']
        
        # 平均分
        cursor.execute("""
            SELECT AVG(total_score) as avg_score FROM evaluations 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (days,))
        avg_score = cursor.fetchone()['avg_score'] or 0
        
        # 各等级数量
        cursor.execute("""
            SELECT grade, COUNT(*) as count FROM evaluations 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY grade
        """, (days,))
        grades = {row['grade']: row['count'] for row in cursor.fetchall()}
        
        cursor.close()
        
        return {
            'total': total,
            'avg_score': round(avg_score, 1),
            'grades': grades,
            'period': f'{days}天'
        }
    
    def batch_evaluate(self, items: List[Dict], 
                      eval_type: str = 'article') -> List[Dict]:
        """
        批量评价
        
        Args:
            items: 评价项列表
            eval_type: 评价类型
        
        Returns:
            评价结果列表
        """
        results = []
        for i, item in enumerate(items):
            print(f"评价进度：{i+1}/{len(items)}")
            
            if eval_type == 'article':
                result = self.evaluate_article(
                    item.get('title', ''),
                    item.get('content', ''),
                    save=True
                )
            else:
                result = self.evaluate_topic(
                    item.get('title', ''),
                    item.get('description', ''),
                    save=True
                )
            
            results.append(result)
        
        return results
    
    def close(self):
        """关闭数据库连接"""
        try:
            if self.conn:
                self.conn.close()
                print("[EvaluationService] ✅ 数据库连接已关闭")
        except Exception as e:
            print(f"[EvaluationService] ⚠️ 关闭连接失败：{e}")


# 使用示例
if __name__ == '__main__':
    service = EvaluationService(model='free')
    
    # 测试文章评价
    result = service.evaluate_article(
        title='AI 教育正在改变未来',
        content='人工智能技术的快速发展正在深刻改变教育行业...',
        save=True
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 获取统计
    stats = service.get_statistics(days=7)
    print(f"\n统计：{stats}")
    
    service.close()
