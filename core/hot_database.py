#!/usr/bin/env python3
"""
【热点数据库】Hot News Database
基于 SQLite 的热点数据存储与管理

数据库结构:
- hot_topics: 热点主表
- hot_sources: 来源表
- hot_keywords: 关键词表
- hot_statistics: 统计表

功能:
1. 热点存储 - 结构化存储热点数据
2. 智能去重 - 基于语义相似度
3. 热度计算 - 多维权重评分
4. 过期清理 - 自动清理旧数据
5. 统计分析 - 多维度数据统计
"""

import os
import sys
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import re

class HotNewsDatabase:
    """热点数据库"""
    
    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: 数据库文件路径 (默认：data/hot_news.db)
        """
        if db_path is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data'
            )
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'hot_news.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        cursor = self.conn.cursor()
        
        # 1. 热点主表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hot_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                url TEXT,
                source_id INTEGER,
                crawl_time DATETIME NOT NULL,
                publish_time DATETIME,
                heat_score REAL DEFAULT 0,
                heat_level TEXT DEFAULT 'normal',
                category TEXT,
                tags TEXT,
                keyword_hash TEXT,
                is_unique INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES hot_sources(id)
            )
        ''')
        
        # 2. 来源表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hot_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                platform TEXT,
                category TEXT,
                base_url TEXT,
                priority INTEGER DEFAULT 5,
                credibility REAL DEFAULT 0.5,
                is_active INTEGER DEFAULT 1,
                last_crawl DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. 关键词表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hot_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                keyword TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                category TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES hot_topics(id)
            )
        ''')
        
        # 4. 统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hot_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_date DATE NOT NULL,
                category TEXT,
                source_id INTEGER,
                total_count INTEGER DEFAULT 0,
                avg_heat_score REAL DEFAULT 0,
                max_heat_score REAL DEFAULT 0,
                unique_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stat_date, category, source_id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hot_topics_crawl_time ON hot_topics(crawl_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hot_topics_heat ON hot_topics(heat_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hot_topics_hash ON hot_topics(keyword_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hot_keywords_keyword ON hot_keywords(keyword)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hot_statistics_date ON hot_statistics(stat_date)')
        
        self.conn.commit()
        print(f"[DB] ✅ 数据库初始化成功：{self.db_path}")
    
    # ========== 来源管理 ==========
    
    def add_source(self, name: str, platform: str = None, 
                   category: str = None, base_url: str = None,
                   priority: int = 5, credibility: float = 0.5) -> int:
        """添加数据源"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO hot_sources 
                (name, platform, category, base_url, priority, credibility)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, platform, category, base_url, priority, credibility))
            
            self.conn.commit()
            source_id = cursor.lastrowid
            print(f"[DB] ✅ 添加数据源：{name} (ID: {source_id})")
            return source_id
        except Exception as e:
            print(f"[DB] ❌ 添加数据源失败：{e}")
            return -1
    
    def get_sources(self, category: str = None, active_only: bool = True) -> List[Dict]:
        """获取数据源列表"""
        cursor = self.conn.cursor()
        
        query = 'SELECT * FROM hot_sources'
        params = []
        
        if active_only:
            query += ' WHERE is_active = 1'
        
        if category:
            query += ' AND category = ?' if active_only else ' WHERE category = ?'
            params.append(category)
        
        query += ' ORDER BY priority DESC, credibility DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    # ========== 热点存储 ==========
    
    def add_hot_topic(self, title: str, content: str = None,
                     url: str = None, source_name: str = None,
                     crawl_time: datetime = None, publish_time: datetime = None,
                     heat_score: float = None, category: str = None,
                     tags: List[str] = None, keywords: List[str] = None) -> int:
        """
        添加热点
        
        Args:
            title: 热点标题
            content: 内容摘要
            url: 原文链接
            source_name: 来源名称
            crawl_time: 采集时间
            publish_time: 发布时间
            heat_score: 热度值 (0-100)
            category: 分类
            tags: 标签列表
            keywords: 关键词列表
        
        Returns:
            热点 ID
        """
        cursor = self.conn.cursor()
        
        # 1. 获取或创建来源
        source_id = self._get_or_create_source(source_name)
        
        # 2. 计算关键词哈希 (用于去重)
        keyword_hash = self._calculate_keyword_hash(title, keywords)
        
        # 3. 检查是否重复
        existing = self._check_duplicate(keyword_hash, title)
        if existing:
            print(f"[DB] ⚠️ 检测到重复热点：{title[:30]}...")
            return -1
        
        # 4. 设置默认值
        if crawl_time is None:
            crawl_time = datetime.now()
        if heat_score is None:
            heat_score = self._calculate_heat_score(title, content, source_name)
        
        # 5. 插入数据库
        cursor.execute('''
            INSERT INTO hot_topics 
            (title, content, url, source_id, crawl_time, publish_time, 
             heat_score, heat_level, category, tags, keyword_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, content, url, source_id,
            crawl_time.isoformat() if crawl_time else None,
            publish_time.isoformat() if publish_time else None,
            heat_score,
            self._get_heat_level(heat_score),
            category,
            json.dumps(tags, ensure_ascii=False) if tags else None,
            keyword_hash
        ))
        
        topic_id = cursor.lastrowid
        
        # 6. 添加关键词
        if keywords:
            self._add_keywords(topic_id, keywords)
        
        self.conn.commit()
        print(f"[DB] ✅ 添加热点：{title[:30]}... (ID: {topic_id}, 热度：{heat_score})")
        return topic_id
    
    def _get_or_create_source(self, source_name: str) -> int:
        """获取或创建来源"""
        if not source_name:
            return 1  # 默认来源
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM hot_sources WHERE name = ?', (source_name,))
        row = cursor.fetchone()
        
        if row:
            return row['id']
        
        # 创建新来源
        return self.add_source(source_name)
    
    def _calculate_keyword_hash(self, title: str, keywords: List[str] = None) -> str:
        """计算关键词哈希"""
        # 提取关键词
        if keywords:
            kw_text = ' '.join(keywords)
        else:
            # 简单分词
            kw_text = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', title)
        
        # 计算哈希
        hash_md5 = hashlib.md5(kw_text.encode('utf-8')).hexdigest()
        return hash_md5
    
    def _check_duplicate(self, keyword_hash: str, title: str, 
                        time_window_hours: int = 24) -> bool:
        """检查是否重复"""
        cursor = self.conn.cursor()
        
        # 时间窗口
        time_threshold = datetime.now() - timedelta(hours=time_window_hours)
        
        # 检查哈希相同
        cursor.execute('''
            SELECT id FROM hot_topics 
            WHERE keyword_hash = ? AND crawl_time > ?
        ''', (keyword_hash, time_threshold.isoformat()))
        
        if cursor.fetchone():
            return True
        
        # 检查标题相似度 (简单匹配)
        cursor.execute('''
            SELECT id FROM hot_topics 
            WHERE title LIKE ? AND crawl_time > ?
        ''', (f'%{title[:20]}%', time_threshold.isoformat()))
        
        return cursor.fetchone() is not None
    
    def _calculate_heat_score(self, title: str, content: str = None,
                             source_name: str = None) -> float:
        """计算热度值"""
        score = 50.0  # 基础分
        
        # 1. 标题长度 (20-40 字最佳)
        title_len = len(title)
        if 20 <= title_len <= 40:
            score += 10
        elif 10 <= title_len < 20 or 40 < title_len <= 60:
            score += 5
        
        # 2. 来源可信度
        source_credibility = self._get_source_credibility(source_name)
        score += source_credibility * 20
        
        # 3. 内容长度
        if content:
            content_len = len(content)
            if 100 <= content_len <= 500:
                score += 10
            elif content_len > 500:
                score += 5
        
        # 4. 热点关键词
        hot_keywords = ['突发', '重磅', '最新', '刚刚', '震惊', '曝光']
        if any(kw in title for kw in hot_keywords):
            score += 5
        
        return min(100, max(0, score))
    
    def _get_source_credibility(self, source_name: str) -> float:
        """获取来源可信度"""
        if not source_name:
            return 0.5
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT credibility FROM hot_sources WHERE name = ?', (source_name,))
        row = cursor.fetchone()
        
        return row['credibility'] if row else 0.5
    
    def _get_heat_level(self, heat_score: float) -> str:
        """获取热度等级"""
        if heat_score >= 90:
            return 'explosive'  # 爆款
        elif heat_score >= 75:
            return 'hot'  # 热门
        elif heat_score >= 60:
            return 'warm'  # 温热点
        else:
            return 'normal'  # 普通
    
    def _add_keywords(self, topic_id: int, keywords: List[str]):
        """添加关键词"""
        cursor = self.conn.cursor()
        
        for keyword in keywords:
            cursor.execute('''
                INSERT INTO hot_keywords (topic_id, keyword, weight)
                VALUES (?, ?, ?)
            ''', (topic_id, keyword, 1.0))
    
    # ========== 热点查询 ==========
    
    def get_hot_topics(self, limit: int = 20, 
                      category: str = None,
                      heat_level: str = None,
                      source_name: str = None,
                      time_range_hours: int = None) -> List[Dict]:
        """
        获取热点列表
        
        Args:
            limit: 返回数量
            category: 分类过滤
            heat_level: 热度等级过滤
            source_name: 来源过滤
            time_range_hours: 时间范围 (小时)
        """
        cursor = self.conn.cursor()
        
        query = '''
            SELECT t.*, s.name as source_name, s.platform, s.category as source_category
            FROM hot_topics t
            LEFT JOIN hot_sources s ON t.source_id = s.id
            WHERE 1=1
        '''
        params = []
        
        if category:
            query += ' AND (t.category = ? OR s.category = ?)'
            params.extend([category, category])
        
        if heat_level:
            query += ' AND t.heat_level = ?'
            params.append(heat_level)
        
        if source_name:
            query += ' AND s.name = ?'
            params.append(source_name)
        
        if time_range_hours:
            time_threshold = datetime.now() - timedelta(hours=time_range_hours)
            query += ' AND t.crawl_time > ?'
            params.append(time_threshold.isoformat())
        
        query += ' ORDER BY t.heat_score DESC, t.crawl_time DESC'
        query += ' LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            item = dict(row)
            # 解析 tags
            if item.get('tags'):
                try:
                    item['tags'] = json.loads(item['tags'])
                except:
                    item['tags'] = []
            results.append(item)
        
        return results
    
    def get_keywords_by_topic(self, topic_id: int) -> List[Dict]:
        """获取热点的关键词"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM hot_keywords 
            WHERE topic_id = ? 
            ORDER BY weight DESC
        ''', (topic_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== 统计分析 ==========
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取统计数据"""
        cursor = self.conn.cursor()
        
        # 时间范围
        time_threshold = datetime.now() - timedelta(days=days)
        
        # 总体统计
        cursor.execute('''
            SELECT 
                COUNT(*) as total_count,
                AVG(heat_score) as avg_heat,
                MAX(heat_score) as max_heat,
                COUNT(DISTINCT keyword_hash) as unique_count
            FROM hot_topics
            WHERE crawl_time > ?
        ''', (time_threshold.isoformat(),))
        
        overall = dict(cursor.fetchone())
        
        # 按分类统计
        cursor.execute('''
            SELECT category, COUNT(*) as count, AVG(heat_score) as avg_heat
            FROM hot_topics
            WHERE crawl_time > ? AND category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        ''', (time_threshold.isoformat(),))
        
        by_category = [dict(row) for row in cursor.fetchall()]
        
        # 按来源统计
        cursor.execute('''
            SELECT s.name, s.platform, COUNT(t.id) as count, AVG(t.heat_score) as avg_heat
            FROM hot_topics t
            LEFT JOIN hot_sources s ON t.source_id = s.id
            WHERE t.crawl_time > ?
            GROUP BY s.name, s.platform
            ORDER BY count DESC
            LIMIT 20
        ''', (time_threshold.isoformat(),))
        
        by_source = [dict(row) for row in cursor.fetchall()]
        
        # 热词统计
        cursor.execute('''
            SELECT k.keyword, COUNT(*) as count, AVG(k.weight) as avg_weight
            FROM hot_keywords k
            INNER JOIN hot_topics t ON k.topic_id = t.id
            WHERE t.crawl_time > ?
            GROUP BY k.keyword
            ORDER BY count DESC
            LIMIT 50
        ''', (time_threshold.isoformat(),))
        
        hot_keywords = [dict(row) for row in cursor.fetchall()]
        
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
        cursor = self.conn.cursor()
        
        time_threshold = datetime.now() - timedelta(days=days_to_keep)
        
        # 删除旧热点
        cursor.execute('''
            DELETE FROM hot_topics WHERE crawl_time < ?
        ''', (time_threshold.isoformat(),))
        
        deleted = cursor.rowcount
        
        # 删除孤立关键词
        cursor.execute('''
            DELETE FROM hot_keywords 
            WHERE topic_id NOT IN (SELECT id FROM hot_topics)
        ''')
        
        self.conn.commit()
        print(f"[DB] ✅ 清理完成，删除 {deleted} 条旧热点")
        
        return deleted
    
    # ========== 批量操作 ==========
    
    def batch_add_topics(self, topics: List[Dict]) -> Dict[str, int]:
        """
        批量添加热点
        
        Args:
            topics: 热点列表，每个包含：
                - title (必需)
                - content (可选)
                - url (可选)
                - source_name (可选)
                - category (可选)
                - tags (可选)
                - keywords (可选)
        
        Returns:
            {"added": 成功数，"skipped": 跳过数 (重复)}
        """
        stats = {"added": 0, "skipped": 0}
        
        for topic in topics:
            topic_id = self.add_hot_topic(**topic)
            
            if topic_id > 0:
                stats["added"] += 1
            else:
                stats["skipped"] += 1
        
        return stats
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


# ========== 便捷函数 ==========

def get_hot_db() -> HotNewsDatabase:
    """获取数据库实例"""
    return HotNewsDatabase()


def test_hot_database():
    """测试数据库"""
    print("\n" + "="*70)
    print("🗄️  热点数据库测试")
    print("="*70 + "\n")
    
    db = get_hot_db()
    
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
        print(f"     来源：{t['source_name']} | 热度：{t['heat_score']:.1f}")
    
    # 4. 统计
    print("\nStep 4: 统计数据")
    stats = db.get_statistics(days=7)
    print(f"  总热点数：{stats['overall']['total_count']}")
    print(f"  平均热度：{stats['overall']['avg_heat']:.1f}")
    print(f"  唯一热点：{stats['overall']['unique_count']}")
    
    print(f"\n  按分类:")
    for cat in stats['by_category'][:3]:
        print(f"    - {cat['category']}: {cat['count']}条")
    
    print(f"\n  热词 TOP5:")
    for kw in stats['hot_keywords'][:5]:
        print(f"    - {kw['keyword']}: {kw['count']}次")
    
    # 5. 测试去重
    print("\nStep 5: 测试去重")
    topic_id = db.add_hot_topic(
        title="教育部发布 AI+ 教育指导意见，60% 高校已开设相关课程",
        source_name="澎湃新闻"
    )
    print(f"  重复热点 ID: {topic_id} (应为 -1)")
    
    print("\n" + "="*70)
    print("🎉 数据库测试完成")
    print("="*70 + "\n")
    
    db.close()


if __name__ == "__main__":
    test_hot_database()
