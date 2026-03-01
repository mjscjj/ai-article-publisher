#!/usr/bin/env python3
"""
数据分析模块测试 - Analytics Module Tests
测试统计、趋势分析、用户行为追踪等功能
"""

import os
import sys
import unittest
import tempfile
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.analytics.statistics import StatisticsService
from core.analytics.trend_analyzer import TrendAnalyzer
from core.analytics.user_tracker import UserTracker


class TestStatisticsService(unittest.TestCase):
    """统计服务测试"""
    
    def setUp(self):
        """设置测试数据库"""
        # 创建临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # 初始化数据库
        self.db_path = self.temp_db.name
        self._init_test_db()
        
        # 初始化服务
        self.stats_service = StatisticsService(db_path=self.db_path)
    
    def _init_test_db(self):
        """初始化测试数据库表和数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建热点表
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
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建来源表
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
        
        # 创建选题表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topic_discovery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                domain TEXT,
                quality_score REAL,
                status TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建发布表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_publish (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                share_count INTEGER DEFAULT 0,
                publish_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入测试数据
        now = datetime.now()
        
        # 插入来源
        sources = [
            ('微博', 'weibo', 'social', 'https://weibo.com'),
            ('知乎', 'zhihu', 'qa', 'https://zhihu.com'),
            ('抖音', 'douyin', 'video', 'https://douyin.com')
        ]
        cursor.executemany(
            'INSERT INTO hot_sources (name, platform, category, base_url) VALUES (?, ?, ?, ?)',
            sources
        )
        
        # 插入热点数据 (最近 24 小时)
        hot_topics = []
        for i in range(50):
            crawl_time = (now - timedelta(hours=i)).isoformat()
            heat_score = 100 - i * 2
            heat_level = 'high' if heat_score > 80 else 'normal' if heat_score > 50 else 'low'
            category = '科技' if i % 3 == 0 else '娱乐' if i % 3 == 1 else '体育'
            
            hot_topics.append((
                f'测试热点 {i+1}',
                f'内容 {i+1}',
                f'http://example.com/{i+1}',
                (i % 3) + 1,
                crawl_time,
                crawl_time,
                heat_score,
                heat_level,
                category
            ))
        
        cursor.executemany('''
            INSERT INTO hot_topics 
            (title, content, url, source_id, crawl_time, publish_time, heat_score, heat_level, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', hot_topics)
        
        # 插入选题数据
        topics = [
            ('AI 技术发展', '科技', 95.5, 'approved'),
            ('教育改革', '教育', 88.0, 'pending'),
            ('医疗创新', '医疗', 92.3, 'approved'),
            ('环保政策', '社会', 75.0, 'rejected')
        ]
        cursor.executemany('''
            INSERT INTO topic_discovery (title, domain, quality_score, status)
            VALUES (?, ?, ?, ?)
        ''', topics)
        
        # 插入发布数据
        publishes = [
            ('wechat', 1000, 100, 50),
            ('weibo', 5000, 500, 200),
            ('zhihu', 2000, 200, 80)
        ]
        cursor.executemany('''
            INSERT INTO article_publish (platform, view_count, like_count, share_count)
            VALUES (?, ?, ?, ?)
        ''', publishes)
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """清理测试数据库"""
        self.stats_service.close()
        os.unlink(self.db_path)
    
    def test_get_hotspot_stats(self):
        """测试热点统计"""
        stats = self.stats_service.get_hotspot_stats(hours=24)
        
        self.assertIn('total', stats)
        self.assertIn('avg_heat_score', stats)
        self.assertIn('max_heat_score', stats)
        self.assertIn('by_level', stats)
        self.assertIn('by_source', stats)
        self.assertIn('by_category', stats)
        self.assertIn('top_hotspots', stats)
        
        self.assertGreater(stats['total'], 0)
        self.assertGreater(stats['avg_heat_score'], 0)
        self.assertEqual(len(stats['top_hotspots']), 10)
    
    def test_get_topic_stats(self):
        """测试选题统计"""
        stats = self.stats_service.get_topic_stats(hours=24)
        
        self.assertIn('total', stats)
        self.assertIn('avg_quality_score', stats)
        self.assertIn('by_status', stats)
        self.assertIn('by_domain', stats)
        
        self.assertGreater(stats['total'], 0)
    
    def test_get_publish_stats(self):
        """测试发布统计"""
        stats = self.stats_service.get_publish_stats(hours=24)
        
        self.assertIn('total_published', stats)
        self.assertIn('total_views', stats)
        self.assertIn('total_likes', stats)
        self.assertIn('total_shares', stats)
        self.assertIn('by_platform', stats)
        
        self.assertGreater(stats['total_published'], 0)
    
    def test_get_realtime_stats(self):
        """测试实时统计"""
        stats = self.stats_service.get_realtime_stats()
        
        self.assertIn('hotspots', stats)
        self.assertIn('topics', stats)
        self.assertIn('articles', stats)
        self.assertIn('publish', stats)
    
    def test_export_report(self):
        """测试导出报表"""
        report = self.stats_service.export_report(hours=24)
        
        self.assertIn('report_type', report)
        self.assertIn('period_hours', report)
        self.assertIn('generated_at', report)
        self.assertIn('hotspot_stats', report)
        self.assertIn('topic_stats', report)
        self.assertIn('article_stats', report)
        self.assertIn('publish_stats', report)


class TestTrendAnalyzer(unittest.TestCase):
    """趋势分析器测试"""
    
    def setUp(self):
        """设置测试数据库"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db_path = self.temp_db.name
        self._init_test_db()
        
        self.trend_analyzer = TrendAnalyzer(db_path=self.db_path)
    
    def _init_test_db(self):
        """初始化测试数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建热点表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hot_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                crawl_time DATETIME NOT NULL,
                heat_score REAL DEFAULT 0,
                category TEXT,
                source_id INTEGER
            )
        ''')
        
        # 创建来源表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hot_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        ''')
        
        # 创建关键词表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hot_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                keyword TEXT,
                crawl_time DATETIME
            )
        ''')
        
        # 插入测试数据
        now = datetime.now()
        
        # 插入 7 天的数据
        for day in range(7):
            date = (now - timedelta(days=day)).strftime('%Y-%m-%d')
            for hour in range(24):
                crawl_time = (now - timedelta(days=day, hours=hour)).isoformat()
                heat_score = 50 + day * 10 + hour
                
                cursor.execute('''
                    INSERT INTO hot_topics (title, crawl_time, heat_score, category, source_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (f'热点 {day}-{hour}', crawl_time, heat_score, 
                      '科技' if day % 2 == 0 else '娱乐', (day % 3) + 1))
        
        # 插入来源
        cursor.executemany(
            'INSERT INTO hot_sources (name) VALUES (?)',
            [('微博',), ('知乎',), ('抖音',)]
        )
        
        # 插入关键词
        keywords = ['AI', '科技', '创新', '发展', '未来']
        for i, keyword in enumerate(keywords):
            for day in range(7):
                crawl_time = (now - timedelta(days=day)).isoformat()
                topic_id = day + 1
                cursor.execute('''
                    INSERT INTO hot_keywords (topic_id, keyword, crawl_time)
                    VALUES (?, ?, ?)
                ''', (topic_id, keyword, crawl_time))
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """清理测试数据库"""
        self.trend_analyzer.close()
        os.unlink(self.db_path)
    
    def test_analyze_heat_trend(self):
        """测试热度趋势分析"""
        trend = self.trend_analyzer.analyze_heat_trend(days=7)
        
        self.assertIn('period_days', trend)
        self.assertIn('daily_data', trend)
        self.assertIn('trend', trend)
        self.assertIn('prediction', trend)
        
        self.assertEqual(trend['period_days'], 7)
        self.assertGreater(len(trend['daily_data']), 0)
        self.assertIn('direction', trend['trend'])
    
    def test_analyze_category_trend(self):
        """测试分类趋势分析"""
        trend = self.trend_analyzer.analyze_category_trend(days=7)
        
        self.assertIn('period_days', trend)
        self.assertIn('by_category', trend)
        self.assertIn('trends', trend)
    
    def test_detect_anomalies(self):
        """测试异常检测"""
        anomalies = self.trend_analyzer.detect_anomalies(days=7)
        
        self.assertIsInstance(anomalies, list)
        
        if anomalies:
            anomaly = anomalies[0]
            self.assertIn('date', anomaly)
            self.assertIn('count', anomaly)
            self.assertIn('z_score', anomaly)
            self.assertIn('type', anomaly)
    
    def test_get_keyword_trends(self):
        """测试关键词趋势"""
        keywords = self.trend_analyzer.get_keyword_trends(days=7, limit=10)
        
        self.assertIsInstance(keywords, list)
        self.assertLessEqual(len(keywords), 10)
        
        if keywords:
            keyword = keywords[0]
            self.assertIn('keyword', keyword)
            self.assertIn('total_count', keyword)
            self.assertIn('growth_rate', keyword)


class TestUserTracker(unittest.TestCase):
    """用户行为追踪器测试"""
    
    def setUp(self):
        """设置测试数据库"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db_path = self.temp_db.name
        self.user_tracker = UserTracker(db_path=self.db_path)
    
    def tearDown(self):
        """清理测试数据库"""
        self.user_tracker.close()
        os.unlink(self.db_path)
    
    def test_track_action(self):
        """测试追踪用户操作"""
        record_id = self.user_tracker.track_action(
            user_id='user_001',
            action_type='click',
            target='button_export',
            data={'page': 'dashboard'},
            session_id='session_123'
        )
        
        self.assertGreater(record_id, 0)
    
    def test_track_page_view(self):
        """测试追踪页面访问"""
        record_id = self.user_tracker.track_page_view(
            user_id='user_001',
            page_url='/dashboard',
            page_title='数据看板',
            duration=120,
            session_id='session_123'
        )
        
        self.assertGreater(record_id, 0)
    
    def test_track_api_call(self):
        """测试追踪 API 调用"""
        record_id = self.user_tracker.track_api_call(
            user_id='user_001',
            endpoint='/api/v3/analytics/statistics',
            method='GET',
            status_code=200,
            response_time=150
        )
        
        self.assertGreater(record_id, 0)
    
    def test_track_feature_usage(self):
        """测试追踪功能使用"""
        record_id = self.user_tracker.track_feature_usage(
            user_id='user_001',
            feature_name='export_report',
            action='use'
        )
        
        self.assertGreater(record_id, 0)
    
    def test_get_user_actions(self):
        """测试获取用户操作记录"""
        # 先添加一些数据
        self.user_tracker.track_action('user_001', 'click', 'button1')
        self.user_tracker.track_action('user_001', 'view', 'page1')
        
        actions = self.user_tracker.get_user_actions('user_001', hours=24)
        
        self.assertIsInstance(actions, list)
        self.assertGreater(len(actions), 0)
    
    def test_get_action_stats(self):
        """测试获取操作统计"""
        # 添加测试数据
        for i in range(10):
            self.user_tracker.track_action(f'user_{i}', 'click', f'button_{i}')
        
        stats = self.user_tracker.get_action_stats(hours=24)
        
        self.assertIn('total_actions', stats)
        self.assertIn('unique_users', stats)
        self.assertIn('by_type', stats)
        
        self.assertGreater(stats['total_actions'], 0)
    
    def test_get_feature_usage_stats(self):
        """测试获取功能使用统计"""
        # 添加测试数据
        self.user_tracker.track_feature_usage('user_001', 'feature_a')
        self.user_tracker.track_feature_usage('user_001', 'feature_a')
        self.user_tracker.track_feature_usage('user_002', 'feature_b')
        
        stats = self.user_tracker.get_feature_usage_stats(days=7)
        
        self.assertIn('features', stats)
        self.assertGreater(len(stats['features']), 0)
    
    def test_get_api_performance(self):
        """测试获取 API 性能统计"""
        # 添加测试数据
        for i in range(20):
            self.user_tracker.track_api_call(
                user_id='user_001',
                endpoint=f'/api/test/{i % 5}',
                response_time=100 + i * 10,
                status_code=200 if i % 10 != 0 else 500
            )
        
        perf = self.user_tracker.get_api_performance(hours=24)
        
        self.assertIn('total_calls', perf)
        self.assertIn('avg_response_time', perf)
        self.assertIn('by_endpoint', perf)
        self.assertIn('errors', perf)
        
        self.assertGreater(perf['total_calls'], 0)
    
    def test_get_popular_pages(self):
        """测试获取热门页面"""
        # 添加测试数据
        for i in range(10):
            self.user_tracker.track_page_view(
                user_id=f'user_{i % 3}',
                page_url='/dashboard' if i < 5 else '/settings',
                duration=60 + i * 10
            )
        
        pages = self.user_tracker.get_popular_pages(days=7)
        
        self.assertIsInstance(pages, list)
        self.assertGreater(len(pages), 0)


class TestAnalyticsIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # 初始化数据库表
        self._init_test_db()
        
        # 初始化所有服务
        self.stats_service = StatisticsService(db_path=self.db_path)
        self.trend_analyzer = TrendAnalyzer(db_path=self.db_path)
        self.user_tracker = UserTracker(db_path=self.db_path)
    
    def _init_test_db(self):
        """初始化测试数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建热点表 (完整结构)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hot_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
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
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建来源表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hot_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        ''')
        
        # 创建选题表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topic_discovery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                domain TEXT,
                quality_score REAL,
                status TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建发布表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_publish (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                share_count INTEGER DEFAULT 0,
                publish_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入一些测试数据
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO hot_topics (title, crawl_time, heat_score, heat_level, category)
            VALUES (?, ?, ?, ?, ?)
        ''', ('测试热点', now, 85.0, 'high', '科技'))
        
        cursor.execute('''
            INSERT INTO topic_discovery (title, domain, quality_score, status)
            VALUES (?, ?, ?, ?)
        ''', ('测试选题', '科技', 90.0, 'approved'))
        
        cursor.execute('''
            INSERT INTO article_publish (platform, view_count, like_count, share_count)
            VALUES (?, ?, ?, ?)
        ''', ('wechat', 100, 10, 5))
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """清理测试环境"""
        self.stats_service.close()
        self.trend_analyzer.close()
        self.user_tracker.close()
        os.unlink(self.db_path)
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 追踪用户操作
        self.user_tracker.track_action('user_001', 'view', 'dashboard')
        self.user_tracker.track_feature_usage('user_001', 'analytics_view')
        
        # 2. 获取统计
        stats = self.stats_service.get_realtime_stats()
        self.assertIsNotNone(stats)
        
        # 3. 获取趋势
        trend = self.trend_analyzer.analyze_heat_trend(days=7)
        self.assertIsNotNone(trend)
        
        # 4. 获取用户统计
        user_stats = self.user_tracker.get_action_stats(hours=24)
        self.assertIsNotNone(user_stats)
        
        # 5. 导出报表
        report = self.stats_service.export_report(hours=24)
        self.assertIn('report_type', report)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
