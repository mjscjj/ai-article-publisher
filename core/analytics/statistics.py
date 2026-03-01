#!/usr/bin/env python3
"""
统计服务 - Statistics Service
提供热点、选题、文章、发布等多维度数据统计
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict


class StatisticsService:
    """统计服务"""
    
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
    
    def get_hotspot_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        热点统计
        
        Args:
            hours: 统计时长 (小时)
            
        Returns:
            热点统计数据
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(hours=hours)
        
        # 热点总数
        cursor.execute('''
            SELECT COUNT(*) as total,
                   AVG(heat_score) as avg_score,
                   MAX(heat_score) as max_score
            FROM hot_topics
            WHERE crawl_time >= ?
        ''', (since.isoformat(),))
        row = cursor.fetchone()
        
        # 按等级统计
        cursor.execute('''
            SELECT heat_level, COUNT(*) as count
            FROM hot_topics
            WHERE crawl_time >= ?
            GROUP BY heat_level
        ''', (since.isoformat(),))
        level_stats = {r['heat_level']: r['count'] for r in cursor.fetchall()}
        
        # 按来源统计
        cursor.execute('''
            SELECT s.name, COUNT(t.id) as count
            FROM hot_topics t
            LEFT JOIN hot_sources s ON t.source_id = s.id
            WHERE t.crawl_time >= ?
            GROUP BY s.name
            ORDER BY count DESC
            LIMIT 10
        ''', (since.isoformat(),))
        source_stats = {r['name']: r['count'] for r in cursor.fetchall()}
        
        # 按分类统计
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM hot_topics
            WHERE crawl_time >= ? AND category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        ''', (since.isoformat(),))
        category_stats = {r['category']: r['count'] for r in cursor.fetchall()}
        
        # Top 10 热点
        cursor.execute('''
            SELECT title, heat_score, category, crawl_time
            FROM hot_topics
            WHERE crawl_time >= ?
            ORDER BY heat_score DESC
            LIMIT 10
        ''', (since.isoformat(),))
        top_hotspots = [dict(r) for r in cursor.fetchall()]
        
        return {
            'period_hours': hours,
            'total': row['total'] or 0,
            'avg_heat_score': round(row['avg_score'] or 0, 2),
            'max_heat_score': round(row['max_score'] or 0, 2),
            'by_level': level_stats,
            'by_source': source_stats,
            'by_category': category_stats,
            'top_hotspots': top_hotspots,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_topic_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        选题统计
        
        Returns:
            选题统计数据
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(hours=hours)
        
        # 选题总数
        cursor.execute('''
            SELECT COUNT(*) as total
            FROM topic_discovery
            WHERE created_at >= ?
        ''', (since.isoformat(),))
        row = cursor.fetchone()
        total = row['total'] or 0
        
        # 按状态统计
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM topic_discovery
            WHERE created_at >= ?
            GROUP BY status
        ''', (since.isoformat(),))
        status_stats = {r['status']: r['count'] for r in cursor.fetchall()}
        
        # 按领域统计
        cursor.execute('''
            SELECT domain, COUNT(*) as count
            FROM topic_discovery
            WHERE created_at >= ? AND domain IS NOT NULL
            GROUP BY domain
            ORDER BY count DESC
        ''', (since.isoformat(),))
        domain_stats = {r['domain']: r['count'] for r in cursor.fetchall()}
        
        # 平均质量分
        cursor.execute('''
            SELECT AVG(quality_score) as avg_score,
                   MAX(quality_score) as max_score
            FROM topic_discovery
            WHERE created_at >= ?
        ''', (since.isoformat(),))
        row = cursor.fetchone()
        
        # Top 10 选题
        cursor.execute('''
            SELECT title, domain, quality_score, status
            FROM topic_discovery
            WHERE created_at >= ?
            ORDER BY quality_score DESC
            LIMIT 10
        ''', (since.isoformat(),))
        top_topics = [dict(r) for r in cursor.fetchall()]
        
        return {
            'period_hours': hours,
            'total': total,
            'avg_quality_score': round(row['avg_score'] or 0, 2),
            'max_quality_score': round(row['max_score'] or 0, 2),
            'by_status': status_stats,
            'by_domain': domain_stats,
            'top_topics': top_topics,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_article_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        文章统计
        
        Returns:
            文章统计数据
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(hours=hours)
        
        # 尝试不同的表名
        tables = ['articles', 'generated_articles', 'article_output']
        total = 0
        avg_score = 0
        max_score = 0
        
        for table in tables:
            try:
                cursor.execute(f'''
                    SELECT COUNT(*) as total,
                           AVG(score) as avg_score,
                           MAX(score) as max_score
                    FROM {table}
                    WHERE created_at >= ?
                ''', (since.isoformat(),))
                row = cursor.fetchone()
                if row['total']:
                    total = row['total']
                    avg_score = row['avg_score'] or 0
                    max_score = row['max_score'] or 0
                    break
            except:
                continue
        
        # 按状态统计
        status_stats = {}
        for table in tables:
            try:
                cursor.execute(f'''
                    SELECT status, COUNT(*) as count
                    FROM {table}
                    WHERE created_at >= ?
                    GROUP BY status
                ''', (since.isoformat(),))
                status_stats = {r['status']: r['count'] for r in cursor.fetchall()}
                break
            except:
                continue
        
        return {
            'period_hours': hours,
            'total': total,
            'avg_score': round(avg_score, 2),
            'max_score': round(max_score, 2),
            'by_status': status_stats,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_publish_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        发布统计
        
        Returns:
            发布统计数据
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(hours=hours)
        
        # 发布总数
        cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(view_count) as total_views,
                   SUM(like_count) as total_likes,
                   SUM(share_count) as total_shares
            FROM article_publish
            WHERE publish_time >= ?
        ''', (since.isoformat(),))
        row = cursor.fetchone()
        
        # 按平台统计
        cursor.execute('''
            SELECT platform, COUNT(*) as count,
                   SUM(view_count) as views
            FROM article_publish
            WHERE publish_time >= ?
            GROUP BY platform
            ORDER BY count DESC
        ''', (since.isoformat(),))
        platform_stats = [dict(r) for r in cursor.fetchall()]
        
        # 按时段统计 (按小时)
        cursor.execute('''
            SELECT strftime('%H', publish_time) as hour, COUNT(*) as count
            FROM article_publish
            WHERE publish_time >= ?
            GROUP BY hour
            ORDER BY hour
        ''', (since.isoformat(),))
        hourly_stats = {r['hour']: r['count'] for r in cursor.fetchall()}
        
        return {
            'period_hours': hours,
            'total_published': row['total'] or 0,
            'total_views': row['total_views'] or 0,
            'total_likes': row['total_likes'] or 0,
            'total_shares': row['total_shares'] or 0,
            'by_platform': platform_stats,
            'by_hour': hourly_stats,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        """
        实时统计 (最近 1 小时)
        
        Returns:
            实时统计数据
        """
        return {
            'hotspots': self.get_hotspot_stats(hours=1),
            'topics': self.get_topic_stats(hours=1),
            'articles': self.get_article_stats(hours=1),
            'publish': self.get_publish_stats(hours=1),
            'generated_at': datetime.now().isoformat()
        }
    
    def export_report(self, hours: int = 24, format: str = 'json') -> Dict[str, Any]:
        """
        导出报表
        
        Args:
            hours: 统计时长
            format: 导出格式
            
        Returns:
            完整报表数据
        """
        report = {
            'report_type': 'analytics_export',
            'period_hours': hours,
            'generated_at': datetime.now().isoformat(),
            'hotspot_stats': self.get_hotspot_stats(hours),
            'topic_stats': self.get_topic_stats(hours),
            'article_stats': self.get_article_stats(hours),
            'publish_stats': self.get_publish_stats(hours)
        }
        
        return report
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
