#!/usr/bin/env python3
"""
【热点数据库 - MySQL 版本】Hot News Database (MySQL)
基于 MySQL 的热点数据存储与管理

数据库连接:
- 主机：43.134.234.4 (localhost)
- 端口：3306
- 数据库：youmind
- 用户：youmind
- 密码：YouMind2026
"""

import os
import sys
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter

# 尝试导入 pymysql
try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("⚠️  pymysql 未安装，请运行：pip install pymysql")

class HotNewsDatabaseMySQL:
    """热点数据库 (MySQL 版本)"""
    
    def __init__(self, 
                 host: str = "43.134.234.4",
                 port: int = 3306,
                 database: str = "youmind",
                 user: str = "youmind",
                 password: str = "YouMind2026"):
        """
        Args:
            host: 数据库主机
            port: 端口
            database: 数据库名
            user: 用户名
            password: 密码
        """
        if not MYSQL_AVAILABLE:
            raise ImportError("pymysql 未安装")
        
        self.config = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        
        self.conn = None
        self._connect()
        self._init_tables()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            self.conn = pymysql.connect(**self.config)
            print(f"[MySQL] ✅ 连接成功：{self.config['host']}:{self.config['port']}/{self.config['database']}")
        except Exception as e:
            print(f"[MySQL] ❌ 连接失败：{e}")
            raise
    
    def _execute(self, query: str, params: tuple = None):
        """执行 SQL 语句"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            self.conn.commit()
            return cursor
        except Exception as e:
            self.conn.rollback()
            print(f"[MySQL] ❌ SQL 错误：{e}")
            raise
        finally:
            cursor.close()
    
    def _fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """查询并返回所有结果"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def _fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """查询并返回单条结果"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def _init_tables(self):
        """初始化数据表"""
        # 1. 热点主表
        self._execute('''
            CREATE TABLE IF NOT EXISTS hot_topics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                content TEXT,
                url VARCHAR(1000),
                source_id INT,
                crawl_date DATE NOT NULL,
                crawl_time DATETIME NOT NULL,
                publish_time DATETIME,
                heat_score DECIMAL(5,2) DEFAULT 0,
                heat_level VARCHAR(20) DEFAULT 'normal',
                category VARCHAR(50),
                tags JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_crawl_date (crawl_date),
                INDEX idx_crawl_time (crawl_time),
                INDEX idx_heat (heat_score),
                INDEX idx_category (category)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # 2. 来源表
        self._execute('''
            CREATE TABLE IF NOT EXISTS hot_sources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                platform VARCHAR(50),
                category VARCHAR(50),
                base_url VARCHAR(500),
                priority INT DEFAULT 5,
                credibility DECIMAL(3,2) DEFAULT 0.5,
                is_active TINYINT DEFAULT 1,
                last_crawl DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_platform (platform),
                INDEX idx_category (category)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # 3. 关键词表
        self._execute('''
            CREATE TABLE IF NOT EXISTS hot_keywords (
                id INT AUTO_INCREMENT PRIMARY KEY,
                topic_id INT NOT NULL,
                keyword VARCHAR(100) NOT NULL,
                weight DECIMAL(5,2) DEFAULT 1.0,
                category VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_topic (topic_id),
                INDEX idx_keyword (keyword),
                FOREIGN KEY (topic_id) REFERENCES hot_topics(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # 4. 统计表
        self._execute('''
            CREATE TABLE IF NOT EXISTS hot_statistics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                stat_date DATE NOT NULL,
                category VARCHAR(50),
                source_id INT,
                total_count INT DEFAULT 0,
                avg_heat_score DECIMAL(5,2) DEFAULT 0,
                max_heat_score DECIMAL(5,2) DEFAULT 0,
                unique_count INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_date_category_source (stat_date, category, source_id),
                INDEX idx_date (stat_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        print(f"[MySQL] ✅ 数据表初始化成功")
    
    # ========== 来源管理 ==========
    
    def add_source(self, name: str, platform: str = None, 
                   category: str = None, base_url: str = None,
                   priority: int = 5, credibility: float = 0.5) -> int:
        """添加数据源"""
        self._execute('''
            INSERT INTO hot_sources (name, platform, category, base_url, priority, credibility)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                platform=VALUES(platform),
                category=VALUES(category),
                priority=VALUES(priority),
                credibility=VALUES(credibility)
        ''', (name, platform, category, base_url, priority, credibility))
        
        result = self._fetch_one('SELECT id FROM hot_sources WHERE name = %s', (name,))
        print(f"[MySQL] ✅ 添加数据源：{name} (ID: {result['id']})")
        return result['id']
    
    def get_sources(self, category: str = None, active_only: bool = True) -> List[Dict]:
        """获取数据源列表"""
        query = 'SELECT * FROM hot_sources'
        params = []
        
        if active_only:
            query += ' WHERE is_active = 1'
        
        if category:
            query += ' AND category = %s' if active_only else ' WHERE category = %s'
            params.append(category)
        
        query += ' ORDER BY priority DESC, credibility DESC'
        
        return self._fetch_all(query, tuple(params))
    
    # ========== 热点存储 ==========
    
    def add_hot_topic(self, title: str, content: str = None,
                     url: str = None, source_name: str = None,
                     crawl_time: datetime = None, publish_time: datetime = None,
                     heat_score: float = None, category: str = None,
                     tags: List[str] = None, keywords: List[str] = None) -> int:
        """添加热点"""
        # 1. 获取或创建来源
        source_id = self._get_or_create_source(source_name)
        
        # 2. 设置默认值
        if crawl_time is None:
            crawl_time = datetime.now()
        if heat_score is None:
            heat_score = self._calculate_heat_score(title, content, source_name)
        
        # 3. 插入数据库
        crawl_date = crawl_time.date() if hasattr(crawl_time, 'date') else crawl_time.date()
        
        self._execute('''
            INSERT INTO hot_topics 
            (title, content, url, source_id, crawl_date, crawl_time, publish_time, 
             heat_score, heat_level, category, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            title, content, url, source_id,
            crawl_date, crawl_time, publish_time,
            heat_score,
            self._get_heat_level(heat_score),
            category,
            json.dumps(tags, ensure_ascii=False) if tags else None
        ))
        
        topic_id = self._fetch_one('SELECT LAST_INSERT_ID() as id')['id']
        
        # 4. 添加关键词
        if keywords:
            self._add_keywords(topic_id, keywords)
        
        print(f"[MySQL] ✅ 添加热点：{title[:30]}... (ID: {topic_id}, 热度：{heat_score})")
        return topic_id
    
    def _get_or_create_source(self, source_name: str) -> int:
        """获取或创建来源"""
        if not source_name:
            return 1
        
        result = self._fetch_one('SELECT id FROM hot_sources WHERE name = %s', (source_name,))
        if result:
            return result['id']
        
        return self.add_source(source_name)
    
    def _calculate_heat_score(self, title: str, content: str = None,
                             source_name: str = None) -> float:
        """计算热度值"""
        score = 50.0
        
        title_len = len(title)
        if 20 <= title_len <= 40:
            score += 10
        elif 10 <= title_len < 20 or 40 < title_len <= 60:
            score += 5
        
        source_credibility = self._get_source_credibility(source_name)
        score += source_credibility * 20
        
        if content:
            content_len = len(content)
            if 100 <= content_len <= 500:
                score += 10
            elif content_len > 500:
                score += 5
        
        hot_keywords = ['突发', '重磅', '最新', '刚刚', '震惊', '曝光']
        if any(kw in title for kw in hot_keywords):
            score += 5
        
        return min(100, max(0, score))
    
    def _get_source_credibility(self, source_name: str) -> float:
        """获取来源可信度"""
        if not source_name:
            return 0.5
        
        result = self._fetch_one('SELECT credibility FROM hot_sources WHERE name = %s', (source_name,))
        return float(result['credibility']) if result else 0.5
    
    def _get_heat_level(self, heat_score: float) -> str:
        """获取热度等级"""
        if heat_score >= 90:
            return 'explosive'
        elif heat_score >= 75:
            return 'hot'
        elif heat_score >= 60:
            return 'warm'
        else:
            return 'normal'
    
    def _add_keywords(self, topic_id: int, keywords: List[str]):
        """添加关键词"""
        for keyword in keywords:
            self._execute('''
                INSERT INTO hot_keywords (topic_id, keyword, weight)
                VALUES (%s, %s, %s)
            ''', (topic_id, keyword, 1.0))
    
    # ========== 热点查询 ==========
    
    def get_hot_topics(self, limit: int = 20, 
                      category: str = None,
                      heat_level: str = None,
                      source_name: str = None,
                      time_range_hours: int = None,
                      crawl_date: str = None) -> List[Dict]:
        """
        获取热点列表
        
        Args:
            limit: 返回数量
            category: 分类过滤
            heat_level: 热度等级
            source_name: 来源过滤
            time_range_hours: 时间范围 (小时)
            crawl_date: 采集日期 (格式：'2026-03-01' 或 'today' 或 'yesterday')
        """
        query = '''
            SELECT t.*, s.name as source_name, s.platform, s.category as source_category
            FROM hot_topics t
            LEFT JOIN hot_sources s ON t.source_id = s.id
            WHERE 1=1
        '''
        params = []
        
        if category:
            query += ' AND (t.category = %s OR s.category = %s)'
            params.extend([category, category])
        
        if heat_level:
            query += ' AND t.heat_level = %s'
            params.append(heat_level)
        
        if source_name:
            query += ' AND s.name = %s'
            params.append(source_name)
        
        if crawl_date:
            if crawl_date == 'today':
                crawl_date = datetime.now().date().isoformat()
            elif crawl_date == 'yesterday':
                crawl_date = (datetime.now() - timedelta(days=1)).date().isoformat()
            query += ' AND t.crawl_date = %s'
            params.append(crawl_date)
        elif time_range_hours:
            time_threshold = datetime.now() - timedelta(hours=time_range_hours)
            query += ' AND t.crawl_time > %s'
            params.append(time_threshold)
        
        query += ' ORDER BY t.heat_score DESC, t.crawl_time DESC'
        query += ' LIMIT %s'
        params.append(limit)
        
        results = self._fetch_all(query, tuple(params))
        
        # 解析 JSON 字段
        for item in results:
            if item.get('tags') and isinstance(item['tags'], str):
                try:
                    item['tags'] = json.loads(item['tags'])
                except:
                    item['tags'] = []
        
        return results
    
    def get_keywords_by_topic(self, topic_id: int) -> List[Dict]:
        """获取热点的关键词"""
        return self._fetch_all('''
            SELECT * FROM hot_keywords 
            WHERE topic_id = %s 
            ORDER BY weight DESC
        ''', (topic_id,))
    
    # ========== 统计分析 ==========
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取统计数据"""
        time_threshold = datetime.now() - timedelta(days=days)
        
        # 总体统计
        overall = self._fetch_one('''
            SELECT 
                COUNT(*) as total_count,
                AVG(heat_score) as avg_heat,
                MAX(heat_score) as max_heat,
                COUNT(DISTINCT keyword_hash) as unique_count
            FROM hot_topics
            WHERE crawl_time > %s
        ''', (time_threshold,))
        
        # 按分类统计
        by_category = self._fetch_all('''
            SELECT category, COUNT(*) as count, AVG(heat_score) as avg_heat
            FROM hot_topics
            WHERE crawl_time > %s AND category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        ''', (time_threshold,))
        
        # 按来源统计
        by_source = self._fetch_all('''
            SELECT s.name, s.platform, COUNT(t.id) as count, AVG(t.heat_score) as avg_heat
            FROM hot_topics t
            LEFT JOIN hot_sources s ON t.source_id = s.id
            WHERE t.crawl_time > %s
            GROUP BY s.name, s.platform
            ORDER BY count DESC
            LIMIT 20
        ''', (time_threshold,))
        
        # 热词统计
        hot_keywords = self._fetch_all('''
            SELECT k.keyword, COUNT(*) as count, AVG(k.weight) as avg_weight
            FROM hot_keywords k
            INNER JOIN hot_topics t ON k.topic_id = t.id
            WHERE t.crawl_time > %s
            GROUP BY k.keyword
            ORDER BY count DESC
            LIMIT 50
        ''', (time_threshold,))
        
        return {
            'overall': overall,
            'by_category': by_category,
            'by_source': by_source,
            'hot_keywords': hot_keywords,
            'time_range': f'{days} days'
        }
    
    # ========== 数据清理 ==========
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """清理旧数据"""
        date_threshold = datetime.now().date() - timedelta(days=days_to_keep)
        
        result = self._execute('DELETE FROM hot_topics WHERE crawl_date < %s', (date_threshold,))
        deleted = result.rowcount
        
        print(f"[MySQL] ✅ 清理完成，删除 {deleted} 条旧热点")
        return deleted
    
    def get_date_range(self) -> Dict[str, str]:
        """获取数据日期范围"""
        result = self._fetch_one('''
            SELECT 
                MIN(crawl_date) as earliest_date,
                MAX(crawl_date) as latest_date,
                COUNT(DISTINCT crawl_date) as date_count
            FROM hot_topics
        ''')
        return result if result else {}
    
    def get_available_dates(self, limit: int = 30) -> List[str]:
        """获取可用的日期列表"""
        results = self._fetch_all('''
            SELECT DISTINCT crawl_date
            FROM hot_topics
            ORDER BY crawl_date DESC
            LIMIT %s
        ''', (limit,))
        return [str(r['crawl_date']) for r in results]
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("[MySQL] ✅ 连接已关闭")


# ========== 便捷函数 ==========

def get_hot_db_mysql() -> HotNewsDatabaseMySQL:
    """获取数据库实例"""
    return HotNewsDatabaseMySQL()


def test_mysql_database():
    """测试数据库"""
    print("\n" + "="*70)
    print("🗄️  热点数据库 MySQL 测试")
    print("="*70 + "\n")
    
    db = get_hot_db_mysql()
    
    # 1. 添加数据源
    print("Step 1: 添加数据源")
    db.add_source("微博热搜", platform="微博", category="综合", priority=10, credibility=0.8)
    db.add_source("知乎热榜", platform="知乎", category="综合", priority=9, credibility=0.85)
    db.add_source("澎湃新闻", platform="澎湃新闻", category="新闻", priority=8, credibility=0.9)
    
    # 2. 添加热点
    print("\nStep 2: 添加热点")
    db.add_hot_topic(
        title="教育部发布 AI+ 教育指导意见，60% 高校已开设相关课程",
        content="教育部近日发布《人工智能 + 教育》指导意见，提出到 2025 年...",
        url="https://example.com/news/123",
        source_name="澎湃新闻",
        category="教育",
        tags=["AI", "教育", "政策"],
        keywords=["教育部", "AI 教育", "高校课程"]
    )
    
    db.add_hot_topic(
        title="AI 程序员失业潮来了？专家：不会用 AI 的才会被淘汰",
        content="近日，某大厂宣布裁员 30%，其中程序员占比最高...",
        url="https://example.com/news/124",
        source_name="知乎热榜",
        category="科技",
        tags=["AI", "就业", "程序员"],
        keywords=["AI", "程序员", "失业", "裁员"]
    )
    
    # 3. 查询热点
    print("\nStep 3: 查询热点")
    topics = db.get_hot_topics(limit=5)
    for i, t in enumerate(topics, 1):
        print(f"  {i}. [{t['heat_level']}] {t['title'][:40]}...")
        print(f"     来源：{t['source_name']} | 热度：{float(t['heat_score']):.1f}")
    
    # 4. 统计
    print("\nStep 4: 统计数据")
    stats = db.get_statistics(days=7)
    print(f"  总热点数：{stats['overall']['total_count']}")
    print(f"  平均热度：{float(stats['overall']['avg_heat']):.1f}")
    print(f"  唯一热点：{stats['overall']['unique_count']}")
    
    db.close()
    
    print("\n" + "="*70)
    print("🎉 MySQL 数据库测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_mysql_database()
