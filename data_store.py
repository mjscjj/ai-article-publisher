#!/usr/bin/env python3
"""
数据存储模块 - SQLite 持久化
替换原有的 Mock 数据存储
"""

import sqlite3
import json
import os
import time
from datetime import datetime
from pathlib import Path

class DataStore:
    """统一数据存储接口"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = "/root/.openclaw/workspace-writer/ai-article-publisher/data/articles.db"
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """初始化数据库表"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 热点数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hotspots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                source TEXT,
                url TEXT,
                hot_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 文章表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                topic_id INTEGER,
                status TEXT DEFAULT 'draft',
                version INTEGER DEFAULT 1,
                quality_score REAL,
                review_result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES hotspots(id)
            )
        ''')
        
        # 任务表 (用于飞书审核等)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                article_id INTEGER,
                status TEXT DEFAULT 'pending',
                external_id TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id)
            )
        ''')
        
        # 配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configs (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 采集历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                count INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def save_hotspot(self, title, description, source, url, hot_score):
        """保存热点数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO hotspots (title, description, source, url, hot_score) 
               VALUES (?, ?, ?, ?, ?)''',
            (title, description, source, url, hot_score)
        )
        conn.commit()
        conn.close()
        
    def get_hotspots(self, limit=100, source=None):
        """获取热点列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if source:
            cursor.execute(
                'SELECT * FROM hotspots WHERE source = ? ORDER BY hot_score DESC LIMIT ?',
                (source, limit)
            )
        else:
            cursor.execute(
                'SELECT * FROM hotspots ORDER BY hot_score DESC LIMIT ?',
                (limit,)
            )
            
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
        
    def save_article(self, title, content, topic_id, status='draft', quality_score=None):
        """保存文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO articles (title, content, topic_id, status, quality_score) 
               VALUES (?, ?, ?, ?, ?)''',
            (title, content, topic_id, status, quality_score)
        )
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return article_id
        
    def update_article(self, article_id, **kwargs):
        """更新文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [article_id]
        
        cursor.execute(
            f'UPDATE articles SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            values
        )
        conn.commit()
        conn.close()
        
    def get_article(self, article_id):
        """获取文章"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
        
    def get_articles(self, status=None, limit=50):
        """获取文章列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                'SELECT * FROM articles WHERE status = ? ORDER BY updated_at DESC LIMIT ?',
                (status, limit)
            )
        else:
            cursor.execute(
                'SELECT * FROM articles ORDER BY updated_at DESC LIMIT ?',
                (limit,)
            )
            
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
        
    def save_task(self, task_type, article_id, external_id=None):
        """保存任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO tasks (task_type, article_id, external_id) VALUES (?, ?, ?)''',
            (task_type, article_id, external_id)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
        
    def update_task(self, task_id, status, result=None):
        """更新任务状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE tasks SET status = ?, result = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (status, result, task_id)
        )
        conn.commit()
        conn.close()
        
    def get_pending_tasks(self, task_type=None):
        """获取待处理任务"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if task_type:
            cursor.execute(
                'SELECT * FROM tasks WHERE status = ? AND task_type = ? ORDER BY created_at',
                ('pending', task_type)
            )
        else:
            cursor.execute(
                'SELECT * FROM tasks WHERE status = ? ORDER BY created_at',
                ('pending',)
            )
            
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
        
    def save_config(self, key, value):
        """保存配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT OR REPLACE INTO configs (key, value, updated_at) 
               VALUES (?, ?, CURRENT_TIMESTAMP)''',
            (key, json.dumps(value) if isinstance(value, dict) else value)
        )
        conn.commit()
        conn.close()
        
    def get_config(self, key):
        """获取配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM configs WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            try:
                return json.loads(row[0])
            except:
                return row[0]
        return None
        
    def log_collection(self, source, count, status):
        """记录采集历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO collection_history (source, count, status) VALUES (?, ?, ?)''',
            (source, count, status)
        )
        conn.commit()
        conn.close()

# 全局实例
_store = None

def get_store():
    """获取全局存储实例"""
    global _store
    if _store is None:
        _store = DataStore()
    return _store

if __name__ == '__main__':
    # 测试
    store = DataStore()
    
    # 测试保存热点
    store.save_hotspot('测试热点', '这是一个测试', 'weibo', 'https://example.com', 95.0)
    hotspots = store.get_hotspots()
    print(f"热点数量: {len(hotspots)}")
    
    # 测试保存文章
    article_id = store.save_article('测试文章', '# 内容', 1, 'draft', 85.0)
    print(f"文章ID: {article_id}")
    
    # 测试获取文章
    article = store.get_article(article_id)
    print(f"文章标题: {article['title']}")
