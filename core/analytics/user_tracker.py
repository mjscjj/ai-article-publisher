#!/usr/bin/env python3
"""
用户行为追踪器 - User Tracker
追踪和记录用户操作行为，支持行为分析和优化建议
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import hashlib


class UserTracker:
    """用户行为追踪器"""
    
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
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'analytics.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()
        
        # 用户行为日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action_type TEXT NOT NULL,
                action_target TEXT,
                action_data TEXT,
                session_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 页面访问表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                page_url TEXT NOT NULL,
                page_title TEXT,
                referrer TEXT,
                duration_seconds INTEGER,
                session_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # API 调用表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                endpoint TEXT NOT NULL,
                method TEXT,
                status_code INTEGER,
                response_time_ms INTEGER,
                request_data TEXT,
                response_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 功能使用表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                feature_name TEXT NOT NULL,
                action TEXT,
                count INTEGER DEFAULT 1,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, feature_name)
            )
        ''')
        
        self.conn.commit()
    
    def track_action(self, user_id: str, action_type: str, 
                     target: str = None, data: Dict = None,
                     session_id: str = None, ip_address: str = None,
                     user_agent: str = None) -> int:
        """
        追踪用户操作
        
        Args:
            user_id: 用户 ID
            action_type: 操作类型 (click/view/export/etc)
            target: 操作目标
            data: 操作数据
            session_id: 会话 ID
            ip_address: IP 地址
            user_agent: 用户代理
            
        Returns:
            记录 ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_actions 
            (user_id, action_type, action_target, action_data, session_id, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            action_type,
            target,
            json.dumps(data) if data else None,
            session_id,
            ip_address,
            user_agent
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def track_page_view(self, user_id: str, page_url: str,
                        page_title: str = None, referrer: str = None,
                        duration: int = None, session_id: str = None) -> int:
        """
        追踪页面访问
        
        Args:
            user_id: 用户 ID
            page_url: 页面 URL
            page_title: 页面标题
            referrer: 来源页面
            duration: 停留时长 (秒)
            session_id: 会话 ID
            
        Returns:
            记录 ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO page_views 
            (user_id, page_url, page_title, referrer, duration_seconds, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, page_url, page_title, referrer, duration, session_id))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def track_api_call(self, user_id: str, endpoint: str,
                       method: str = 'GET', status_code: int = 200,
                       response_time: int = None, request_data: Dict = None,
                       response_data: Dict = None) -> int:
        """
        追踪 API 调用
        
        Args:
            user_id: 用户 ID
            endpoint: API 端点
            method: HTTP 方法
            status_code: 响应状态码
            response_time: 响应时间 (毫秒)
            request_data: 请求数据
            response_data: 响应数据
            
        Returns:
            记录 ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_calls 
            (user_id, endpoint, method, status_code, response_time_ms, request_data, response_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            endpoint,
            method,
            status_code,
            response_time,
            json.dumps(request_data) if request_data else None,
            json.dumps(response_data) if response_data else None
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def track_feature_usage(self, user_id: str, feature_name: str,
                            action: str = 'use') -> int:
        """
        追踪功能使用
        
        Args:
            user_id: 用户 ID
            feature_name: 功能名称
            action: 操作类型
            
        Returns:
            记录 ID
        """
        cursor = self.conn.cursor()
        
        # 使用 INSERT OR REPLACE 更新计数
        cursor.execute('''
            INSERT INTO feature_usage (user_id, feature_name, action, count, last_used)
            VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, feature_name) 
            DO UPDATE SET 
                count = count + 1,
                last_used = CURRENT_TIMESTAMP,
                action = excluded.action
        ''', (user_id, feature_name, action))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_actions(self, user_id: str, hours: int = 24,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取用户操作记录
        
        Args:
            user_id: 用户 ID
            hours: 时间范围 (小时)
            limit: 返回数量
            
        Returns:
            操作记录列表
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT * FROM user_actions
            WHERE user_id = ? AND created_at >= ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, since.isoformat(), limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_action_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取操作统计
        
        Args:
            hours: 时间范围 (小时)
            
        Returns:
            统计数据
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(hours=hours)
        
        # 总操作数
        cursor.execute('''
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT user_id) as unique_users
            FROM user_actions
            WHERE created_at >= ?
        ''', (since.isoformat(),))
        row = cursor.fetchone()
        
        # 按类型统计
        cursor.execute('''
            SELECT action_type, COUNT(*) as count
            FROM user_actions
            WHERE created_at >= ?
            GROUP BY action_type
            ORDER BY count DESC
        ''', (since.isoformat(),))
        by_type = {r['action_type']: r['count'] for r in cursor.fetchall()}
        
        # 按小时统计
        cursor.execute('''
            SELECT strftime('%H', created_at) as hour, COUNT(*) as count
            FROM user_actions
            WHERE created_at >= ?
            GROUP BY hour
            ORDER BY hour
        ''', (since.isoformat(),))
        by_hour = {r['hour']: r['count'] for r in cursor.fetchall()}
        
        return {
            'period_hours': hours,
            'total_actions': row['total'] or 0,
            'unique_users': row['unique_users'] or 0,
            'by_type': by_type,
            'by_hour': by_hour,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_feature_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        获取功能使用统计
        
        Args:
            days: 时间范围 (天)
            
        Returns:
            统计数据
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT feature_name, SUM(count) as total_count,
                   COUNT(DISTINCT user_id) as unique_users,
                   MAX(last_used) as last_used
            FROM feature_usage
            WHERE last_used >= ?
            GROUP BY feature_name
            ORDER BY total_count DESC
        ''', (since.isoformat(),))
        
        features = [dict(row) for row in cursor.fetchall()]
        
        return {
            'period_days': days,
            'features': features,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_api_performance(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取 API 性能统计
        
        Args:
            hours: 时间范围 (小时)
            
        Returns:
            性能数据
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(hours=hours)
        
        # 总体统计
        cursor.execute('''
            SELECT COUNT(*) as total,
                   AVG(response_time_ms) as avg_time,
                   MAX(response_time_ms) as max_time,
                   MIN(response_time_ms) as min_time
            FROM api_calls
            WHERE created_at >= ?
        ''', (since.isoformat(),))
        row = cursor.fetchone()
        
        # 按端点统计
        cursor.execute('''
            SELECT endpoint, 
                   COUNT(*) as count,
                   AVG(response_time_ms) as avg_time,
                   SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as errors
            FROM api_calls
            WHERE created_at >= ?
            GROUP BY endpoint
            ORDER BY count DESC
            LIMIT 20
        ''', (since.isoformat(),))
        by_endpoint = [dict(r) for r in cursor.fetchall()]
        
        # 错误统计
        cursor.execute('''
            SELECT endpoint, status_code, COUNT(*) as count
            FROM api_calls
            WHERE created_at >= ? AND status_code >= 400
            GROUP BY endpoint, status_code
            ORDER BY count DESC
            LIMIT 10
        ''', (since.isoformat(),))
        errors = [dict(r) for r in cursor.fetchall()]
        
        return {
            'period_hours': hours,
            'total_calls': row['total'] or 0,
            'avg_response_time': round(row['avg_time'] or 0, 2),
            'max_response_time': row['max_time'] or 0,
            'min_response_time': row['min_time'] or 0,
            'by_endpoint': by_endpoint,
            'errors': errors,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_popular_pages(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取热门页面
        
        Args:
            days: 时间范围 (天)
            limit: 返回数量
            
        Returns:
            页面列表
        """
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT page_url, page_title,
                   COUNT(*) as views,
                   COUNT(DISTINCT user_id) as unique_visitors,
                   AVG(duration_seconds) as avg_duration
            FROM page_views
            WHERE created_at >= ?
            GROUP BY page_url, page_title
            ORDER BY views DESC
            LIMIT ?
        ''', (since.isoformat(), limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def export_user_report(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        导出用户报告
        
        Args:
            user_id: 用户 ID
            days: 时间范围 (天)
            
        Returns:
            用户报告
        """
        since = datetime.now() - timedelta(days=days)
        
        return {
            'user_id': user_id,
            'period_days': days,
            'actions': self.get_user_actions(user_id, hours=days*24),
            'generated_at': datetime.now().isoformat()
        }
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
