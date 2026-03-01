#!/usr/bin/env python3
"""
数据分析 API - Analytics API V3
提供数据统计、趋势分析、用户行为等接口
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, Response

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.analytics.statistics import StatisticsService
from core.analytics.trend_analyzer import TrendAnalyzer
from core.analytics.user_tracker import UserTracker

# 创建 Blueprint
analytics_bp = Blueprint('analytics_v3', __name__, url_prefix='/api/v3/analytics')

# 初始化服务
_stats_service = None
_trend_analyzer = None
_user_tracker = None


def get_stats_service() -> StatisticsService:
    """获取统计服务单例"""
    global _stats_service
    if _stats_service is None:
        _stats_service = StatisticsService()
    return _stats_service


def get_trend_analyzer() -> TrendAnalyzer:
    """获取趋势分析器单例"""
    global _trend_analyzer
    if _trend_analyzer is None:
        _trend_analyzer = TrendAnalyzer()
    return _trend_analyzer


def get_user_tracker() -> UserTracker:
    """获取用户追踪器单例"""
    global _user_tracker
    if _user_tracker is None:
        _user_tracker = UserTracker()
    return _user_tracker


# ============== 统计接口 ==============

@analytics_bp.route('/statistics/hotspots', methods=['GET'])
def get_hotspot_statistics():
    """
    获取热点统计
    
    Query Params:
        hours: 统计时长 (默认 24)
    """
    try:
        hours = int(request.args.get('hours', 24))
        service = get_stats_service()
        data = service.get_hotspot_stats(hours=hours)
        
        # 追踪 API 调用
        tracker = get_user_tracker()
        tracker.track_api_call(
            user_id=request.args.get('user_id', 'anonymous'),
            endpoint='/api/v3/analytics/statistics/hotspots',
            response_time=0
        )
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/statistics/topics', methods=['GET'])
def get_topic_statistics():
    """
    获取选题统计
    
    Query Params:
        hours: 统计时长 (默认 24)
    """
    try:
        hours = int(request.args.get('hours', 24))
        service = get_stats_service()
        data = service.get_topic_stats(hours=hours)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/statistics/articles', methods=['GET'])
def get_article_statistics():
    """
    获取文章统计
    
    Query Params:
        hours: 统计时长 (默认 24)
    """
    try:
        hours = int(request.args.get('hours', 24))
        service = get_stats_service()
        data = service.get_article_stats(hours=hours)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/statistics/publish', methods=['GET'])
def get_publish_statistics():
    """
    获取发布统计
    
    Query Params:
        hours: 统计时长 (默认 24)
    """
    try:
        hours = int(request.args.get('hours', 24))
        service = get_stats_service()
        data = service.get_publish_stats(hours=hours)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/statistics/realtime', methods=['GET'])
def get_realtime_statistics():
    """
    获取实时统计 (最近 1 小时)
    """
    try:
        service = get_stats_service()
        data = service.get_realtime_stats()
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============== 趋势分析接口 ==============

@analytics_bp.route('/trends/heat', methods=['GET'])
def get_heat_trend():
    """
    获取热度趋势
    
    Query Params:
        days: 分析天数 (默认 7)
    """
    try:
        days = int(request.args.get('days', 7))
        analyzer = get_trend_analyzer()
        data = analyzer.analyze_heat_trend(days=days)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/trends/category', methods=['GET'])
def get_category_trend():
    """
    获取分类趋势
    
    Query Params:
        days: 分析天数 (默认 7)
    """
    try:
        days = int(request.args.get('days', 7))
        analyzer = get_trend_analyzer()
        data = analyzer.analyze_category_trend(days=days)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/trends/keywords', methods=['GET'])
def get_keyword_trends():
    """
    获取关键词趋势
    
    Query Params:
        days: 分析天数 (默认 7)
        limit: 返回数量 (默认 20)
    """
    try:
        days = int(request.args.get('days', 7))
        limit = int(request.args.get('limit', 20))
        analyzer = get_trend_analyzer()
        data = analyzer.get_keyword_trends(days=days, limit=limit)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/trends/anomalies', methods=['GET'])
def detect_anomalies():
    """
    检测异常数据
    
    Query Params:
        days: 分析天数 (默认 7)
    """
    try:
        days = int(request.args.get('days', 7))
        analyzer = get_trend_analyzer()
        data = analyzer.detect_anomalies(days=days)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============== 用户行为接口 ==============

@analytics_bp.route('/user/actions', methods=['GET'])
def get_user_actions():
    """
    获取用户操作记录
    
    Query Params:
        user_id: 用户 ID
        hours: 时间范围 (默认 24)
        limit: 返回数量 (默认 100)
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        hours = int(request.args.get('hours', 24))
        limit = int(request.args.get('limit', 100))
        
        tracker = get_user_tracker()
        data = tracker.get_user_actions(user_id, hours=hours, limit=limit)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/user/stats', methods=['GET'])
def get_user_stats():
    """
    获取用户统计
    
    Query Params:
        hours: 时间范围 (默认 24)
    """
    try:
        hours = int(request.args.get('hours', 24))
        tracker = get_user_tracker()
        data = tracker.get_action_stats(hours=hours)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/user/features', methods=['GET'])
def get_feature_usage():
    """
    获取功能使用统计
    
    Query Params:
        days: 时间范围 (默认 7)
    """
    try:
        days = int(request.args.get('days', 7))
        tracker = get_user_tracker()
        data = tracker.get_feature_usage_stats(days=days)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/user/performance', methods=['GET'])
def get_api_performance():
    """
    获取 API 性能统计
    
    Query Params:
        hours: 时间范围 (默认 24)
    """
    try:
        hours = int(request.args.get('hours', 24))
        tracker = get_user_tracker()
        data = tracker.get_api_performance(hours=hours)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/user/pages/popular', methods=['GET'])
def get_popular_pages():
    """
    获取热门页面
    
    Query Params:
        days: 时间范围 (默认 7)
        limit: 返回数量 (默认 20)
    """
    try:
        days = int(request.args.get('days', 7))
        limit = int(request.args.get('limit', 20))
        tracker = get_user_tracker()
        data = tracker.get_popular_pages(days=days, limit=limit)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============== 追踪接口 ==============

@analytics_bp.route('/track/action', methods=['POST'])
def track_action():
    """
    追踪用户操作
    
    Body:
        user_id: 用户 ID
        action_type: 操作类型
        target: 操作目标 (可选)
        data: 操作数据 (可选)
        session_id: 会话 ID (可选)
    """
    try:
        data = request.get_json()
        
        required = ['user_id', 'action_type']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        tracker = get_user_tracker()
        record_id = tracker.track_action(
            user_id=data['user_id'],
            action_type=data['action_type'],
            target=data.get('target'),
            data=data.get('data'),
            session_id=data.get('session_id'),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent')
        )
        
        return jsonify({
            'success': True,
            'record_id': record_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/track/pageview', methods=['POST'])
def track_pageview():
    """
    追踪页面访问
    
    Body:
        user_id: 用户 ID
        page_url: 页面 URL
        page_title: 页面标题 (可选)
        duration: 停留时长 (可选)
        session_id: 会话 ID (可选)
    """
    try:
        data = request.get_json()
        
        required = ['user_id', 'page_url']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        tracker = get_user_tracker()
        record_id = tracker.track_page_view(
            user_id=data['user_id'],
            page_url=data['page_url'],
            page_title=data.get('page_title'),
            duration=data.get('duration'),
            session_id=data.get('session_id')
        )
        
        return jsonify({
            'success': True,
            'record_id': record_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/track/feature', methods=['POST'])
def track_feature():
    """
    追踪功能使用
    
    Body:
        user_id: 用户 ID
        feature_name: 功能名称
        action: 操作类型 (可选)
    """
    try:
        data = request.get_json()
        
        required = ['user_id', 'feature_name']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        tracker = get_user_tracker()
        record_id = tracker.track_feature_usage(
            user_id=data['user_id'],
            feature_name=data['feature_name'],
            action=data.get('action', 'use')
        )
        
        return jsonify({
            'success': True,
            'record_id': record_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============== 导出接口 ==============

@analytics_bp.route('/export/report', methods=['GET'])
def export_report():
    """
    导出分析报告
    
    Query Params:
        hours: 统计时长 (默认 24)
        format: 导出格式 (json/csv, 默认 json)
    """
    try:
        hours = int(request.args.get('hours', 24))
        format_type = request.args.get('format', 'json')
        
        service = get_stats_service()
        report = service.export_report(hours=hours)
        
        if format_type == 'csv':
            # TODO: 实现 CSV 导出
            return jsonify({
                'success': False,
                'error': 'CSV export not implemented yet'
            }), 501
        
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/export/user', methods=['GET'])
def export_user_report():
    """
    导出用户报告
    
    Query Params:
        user_id: 用户 ID
        days: 时间范围 (默认 7)
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        days = int(request.args.get('days', 7))
        
        tracker = get_user_tracker()
        report = tracker.export_user_report(user_id, days=days)
        
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============== 仪表盘数据接口 ==============

@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """
    获取仪表盘完整数据
    
    Query Params:
        hours: 统计时长 (默认 24)
    """
    try:
        hours = int(request.args.get('hours', 24))
        
        stats_service = get_stats_service()
        trend_analyzer = get_trend_analyzer()
        user_tracker = get_user_tracker()
        
        data = {
            'realtime_stats': stats_service.get_realtime_stats(),
            'heat_trend': trend_analyzer.analyze_heat_trend(days=7),
            'category_trend': trend_analyzer.analyze_category_trend(days=7),
            'keyword_trends': trend_analyzer.get_keyword_trends(days=7, limit=10),
            'anomalies': trend_analyzer.detect_anomalies(days=7),
            'user_stats': user_tracker.get_action_stats(hours=hours),
            'feature_usage': user_tracker.get_feature_usage_stats(days=7),
            'api_performance': user_tracker.get_api_performance(hours=hours),
            'popular_pages': user_tracker.get_popular_pages(days=7, limit=10)
        }
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 注册 Blueprint
def create_analytics_routes(app=None):
    """创建分析路由"""
    return analytics_bp


if __name__ == '__main__':
    # 测试
    from flask import Flask
    test_app = Flask(__name__)
    test_app.register_blueprint(analytics_bp)
    
    with test_app.test_client() as client:
        # 测试热点统计
        response = client.get('/api/v3/analytics/statistics/hotspots?hours=24')
        print("Hotspot Stats:", response.get_json())
