#!/usr/bin/env python3
"""
趋势分析器 - Trend Analyzer
提供数据趋势分析、预测、异常检测等功能
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import math


class TrendAnalyzer:
    """趋势分析器"""
    
    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: 数据库文件路径
        """
        if db_path is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data'
            )
            db_path = os.path.join(data_dir, 'hot_news.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def analyze_heat_trend(self, days: int = 7) -> Dict[str, Any]:
        """
        分析热度趋势
        
        Args:
            days: 分析天数
            
        Returns:
            热度趋势数据
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(days=days)
        
        # 按天统计热度
        cursor.execute('''
            SELECT DATE(crawl_time) as date,
                   COUNT(*) as count,
                   AVG(heat_score) as avg_score,
                   SUM(heat_score) as total_score
            FROM hot_topics
            WHERE crawl_time >= ?
            GROUP BY DATE(crawl_time)
            ORDER BY date
        ''', (since.isoformat(),))
        
        daily_data = []
        for row in cursor.fetchall():
            daily_data.append({
                'date': row['date'],
                'count': row['count'],
                'avg_score': round(row['avg_score'] or 0, 2),
                'total_score': round(row['total_score'] or 0, 2)
            })
        
        # 计算趋势
        trend = self._calculate_trend(daily_data, 'count')
        
        # 预测明天
        prediction = self._predict_next(daily_data, 'count')
        
        return {
            'period_days': days,
            'daily_data': daily_data,
            'trend': trend,
            'prediction': prediction,
            'generated_at': datetime.now().isoformat()
        }
    
    def analyze_category_trend(self, days: int = 7) -> Dict[str, Any]:
        """
        分析分类趋势
        
        Args:
            days: 分析天数
            
        Returns:
            分类趋势数据
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(days=days)
        
        # 按天和分类统计
        cursor.execute('''
            SELECT DATE(crawl_time) as date,
                   category,
                   COUNT(*) as count
            FROM hot_topics
            WHERE crawl_time >= ? AND category IS NOT NULL
            GROUP BY DATE(crawl_time), category
            ORDER BY date, count DESC
        ''', (since.isoformat(),))
        
        category_data = defaultdict(list)
        for row in cursor.fetchall():
            category_data[row['category']].append({
                'date': row['date'],
                'count': row['count']
            })
        
        # 计算每个分类的趋势
        trends = {}
        for category, data in category_data.items():
            trends[category] = self._calculate_trend(data, 'count')
        
        return {
            'period_days': days,
            'by_category': dict(category_data),
            'trends': trends,
            'generated_at': datetime.now().isoformat()
        }
    
    def analyze_source_trend(self, days: int = 7) -> Dict[str, Any]:
        """
        分析来源趋势
        
        Args:
            days: 分析天数
            
        Returns:
            来源趋势数据
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(days=days)
        
        # 按天和来源统计
        cursor.execute('''
            SELECT DATE(t.crawl_time) as date,
                   s.name as source,
                   COUNT(t.id) as count
            FROM hot_topics t
            LEFT JOIN hot_sources s ON t.source_id = s.id
            WHERE t.crawl_time >= ?
            GROUP BY DATE(t.crawl_time), s.name
            ORDER BY date, count DESC
        ''', (since.isoformat(),))
        
        source_data = defaultdict(list)
        for row in cursor.fetchall():
            source_data[row['source'] or 'unknown'].append({
                'date': row['date'],
                'count': row['count']
            })
        
        return {
            'period_days': days,
            'by_source': dict(source_data),
            'generated_at': datetime.now().isoformat()
        }
    
    def detect_anomalies(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        检测异常数据
        
        Args:
            days: 分析天数
            
        Returns:
            异常数据列表
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(days=days)
        
        # 获取每日数据
        cursor.execute('''
            SELECT DATE(crawl_time) as date,
                   COUNT(*) as count,
                   AVG(heat_score) as avg_score
            FROM hot_topics
            WHERE crawl_time >= ?
            GROUP BY DATE(crawl_time)
            ORDER BY date
        ''', (since.isoformat(),))
        
        daily_data = [dict(row) for row in cursor.fetchall()]
        
        if len(daily_data) < 3:
            return []
        
        # 计算平均值和标准差
        counts = [d['count'] for d in daily_data]
        avg = sum(counts) / len(counts)
        std = math.sqrt(sum((x - avg) ** 2 for x in counts) / len(counts))
        
        anomalies = []
        for data in daily_data:
            # Z-score > 2 视为异常
            z_score = (data['count'] - avg) / std if std > 0 else 0
            if abs(z_score) > 2:
                anomalies.append({
                    'date': data['date'],
                    'count': data['count'],
                    'avg_score': data['avg_score'],
                    'z_score': round(z_score, 2),
                    'type': 'spike' if z_score > 0 else 'drop'
                })
        
        return anomalies
    
    def get_keyword_trends(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取关键词趋势
        
        Args:
            days: 分析天数
            limit: 返回数量
            
        Returns:
            关键词趋势列表
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(days=days)
        
        # 统计关键词频率
        cursor.execute('''
            SELECT keyword, COUNT(*) as count,
                   MIN(t.crawl_time) as first_seen,
                   MAX(t.crawl_time) as last_seen
            FROM hot_keywords k
            JOIN hot_topics t ON k.topic_id = t.id
            WHERE t.crawl_time >= ?
            GROUP BY keyword
            ORDER BY count DESC
            LIMIT ?
        ''', (since.isoformat(), limit))
        
        keywords = []
        for row in cursor.fetchall():
            # 计算增长率
            cursor.execute('''
                SELECT DATE(t.crawl_time) as date, COUNT(*) as count
                FROM hot_keywords k
                JOIN hot_topics t ON k.topic_id = t.id
                WHERE k.keyword = ? AND t.crawl_time >= ?
                GROUP BY DATE(t.crawl_time)
            ''', (row['keyword'], since.isoformat()))
            
            daily_counts = [r['count'] for r in cursor.fetchall()]
            growth_rate = self._calculate_growth_rate(daily_counts)
            
            keywords.append({
                'keyword': row['keyword'],
                'total_count': row['count'],
                'first_seen': row['first_seen'],
                'last_seen': row['last_seen'],
                'growth_rate': growth_rate,
                'is_rising': growth_rate > 0
            })
        
        return sorted(keywords, key=lambda x: x['growth_rate'], reverse=True)
    
    def _calculate_trend(self, data: List[Dict], field: str) -> Dict[str, Any]:
        """
        计算趋势
        
        Args:
            data: 数据列表
            field: 字段名
            
        Returns:
            趋势分析结果
        """
        if len(data) < 2:
            return {'direction': 'stable', 'change_rate': 0}
        
        values = [d.get(field, 0) for d in data]
        
        # 简单线性回归
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # 计算变化率
        if values[0] != 0:
            change_rate = (values[-1] - values[0]) / values[0] * 100
        else:
            change_rate = 0
        
        # 判断趋势方向
        if slope > 0.5:
            direction = 'rising'
        elif slope < -0.5:
            direction = 'falling'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'slope': round(slope, 4),
            'change_rate': round(change_rate, 2),
            'start_value': values[0],
            'end_value': values[-1]
        }
    
    def _predict_next(self, data: List[Dict], field: str) -> Optional[float]:
        """
        预测下一个值
        
        Args:
            data: 数据列表
            field: 字段名
            
        Returns:
            预测值
        """
        if len(data) < 2:
            return None
        
        values = [d.get(field, 0) for d in data]
        
        # 简单移动平均预测
        window = min(3, len(values))
        recent_avg = sum(values[-window:]) / window
        
        return round(recent_avg, 2)
    
    def _calculate_growth_rate(self, values: List[int]) -> float:
        """
        计算增长率
        
        Args:
            values: 数值列表
            
        Returns:
            增长率 (百分比)
        """
        if len(values) < 2 or values[0] == 0:
            return 0
        
        return (values[-1] - values[0]) / values[0] * 100
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
