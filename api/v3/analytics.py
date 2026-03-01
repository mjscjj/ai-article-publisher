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

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.analytics.statistics import StatisticsService
from core.analytics.trend_analyzer import TrendAnalyzer
from core.analytics.user_tracker import UserTracker


# ============================================
# FastAPI 应用初始化
# ============================================

router = APIRouter()

# 初始化服务
_stats_service: Optional[StatisticsService] = None
_trend_analyzer: Optional[TrendAnalyzer] = None
_user_tracker: Optional[UserTracker] = None


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


# ============================================
# 请求/响应模型
# ============================================

class APIResponse(BaseModel):
    """通用 API 响应"""
    success: bool = True
    data: Any = None
    message: str = "success"


# ============================================
# 统计接口
# ============================================

@router.get("/statistics/hotspots", response_model=APIResponse)
async def get_hotspot_statistics(hours: int = Query(24, description="统计时长")):
    """获取热点统计"""
    try:
        service = get_stats_service()
        data = service.get_hotspot_stats(hours=hours)
        
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/topics", response_model=APIResponse)
async def get_topic_statistics(hours: int = Query(24, description="统计时长")):
    """获取选题统计"""
    try:
        service = get_stats_service()
        data = service.get_topic_stats(hours=hours)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/articles", response_model=APIResponse)
async def get_article_statistics(hours: int = Query(24, description="统计时长")):
    """获取文章统计"""
    try:
        service = get_stats_service()
        data = service.get_article_stats(hours=hours)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/publish", response_model=APIResponse)
async def get_publish_statistics(hours: int = Query(24, description="统计时长")):
    """获取发布统计"""
    try:
        service = get_stats_service()
        data = service.get_publish_stats(hours=hours)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/realtime", response_model=APIResponse)
async def get_realtime_statistics():
    """获取实时统计 (最近 1 小时)"""
    try:
        service = get_stats_service()
        data = service.get_realtime_stats()
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 趋势分析接口
# ============================================

@router.get("/trends/heat", response_model=APIResponse)
async def get_heat_trend(days: int = Query(7, description="分析天数")):
    """获取热度趋势"""
    try:
        analyzer = get_trend_analyzer()
        data = analyzer.analyze_heat_trend(days=days)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/category", response_model=APIResponse)
async def get_category_trend(days: int = Query(7, description="分析天数")):
    """获取分类趋势"""
    try:
        analyzer = get_trend_analyzer()
        data = analyzer.analyze_category_trend(days=days)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/keywords", response_model=APIResponse)
async def get_keyword_trends(
    days: int = Query(7, description="分析天数"),
    limit: int = Query(20, description="返回数量")
):
    """获取关键词趋势"""
    try:
        analyzer = get_trend_analyzer()
        data = analyzer.get_keyword_trends(days=days, limit=limit)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/anomalies", response_model=APIResponse)
async def detect_anomalies(days: int = Query(7, description="分析天数")):
    """检测异常数据"""
    try:
        analyzer = get_trend_analyzer()
        data = analyzer.detect_anomalies(days=days)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 用户行为接口
# ============================================

@router.get("/user/actions", response_model=APIResponse)
async def get_user_actions(
    user_id: str = Query(..., description="用户 ID"),
    hours: int = Query(24, description="时间范围"),
    limit: int = Query(100, description="返回数量")
):
    """获取用户操作记录"""
    try:
        tracker = get_user_tracker()
        data = tracker.get_user_actions(user_id, hours=hours, limit=limit)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/stats", response_model=APIResponse)
async def get_user_stats(hours: int = Query(24, description="时间范围")):
    """获取用户统计"""
    try:
        tracker = get_user_tracker()
        data = tracker.get_action_stats(hours=hours)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/features", response_model=APIResponse)
async def get_feature_usage(days: int = Query(7, description="时间范围")):
    """获取功能使用统计"""
    try:
        tracker = get_user_tracker()
        data = tracker.get_feature_usage_stats(days=days)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/performance", response_model=APIResponse)
async def get_api_performance(hours: int = Query(24, description="时间范围")):
    """获取 API 性能统计"""
    try:
        tracker = get_user_tracker()
        data = tracker.get_api_performance(hours=hours)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/pages/popular", response_model=APIResponse)
async def get_popular_pages(
    days: int = Query(7, description="时间范围"),
    limit: int = Query(20, description="返回数量")
):
    """获取热门页面"""
    try:
        tracker = get_user_tracker()
        data = tracker.get_popular_pages(days=days, limit=limit)
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 追踪接口
# ============================================

class TrackActionRequest(BaseModel):
    """追踪操作请求"""
    user_id: str
    action_type: str
    target: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@router.post("/track/action", response_model=APIResponse)
async def track_action(request: TrackActionRequest):
    """追踪用户操作"""
    try:
        tracker = get_user_tracker()
        record_id = tracker.track_action(
            user_id=request.user_id,
            action_type=request.action_type,
            target=request.target,
            data=request.data,
            session_id=request.session_id,
            ip_address=request.ip_address,
            user_agent=request.user_agent
        )
        return APIResponse(data={"record_id": record_id}, message="追踪成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TrackPageViewRequest(BaseModel):
    """追踪页面访问请求"""
    user_id: str
    page_url: str
    page_title: Optional[str] = None
    duration: Optional[int] = None
    session_id: Optional[str] = None


@router.post("/track/pageview", response_model=APIResponse)
async def track_pageview(request: TrackPageViewRequest):
    """追踪页面访问"""
    try:
        tracker = get_user_tracker()
        record_id = tracker.track_page_view(
            user_id=request.user_id,
            page_url=request.page_url,
            page_title=request.page_title,
            duration=request.duration,
            session_id=request.session_id
        )
        return APIResponse(data={"record_id": record_id}, message="追踪成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TrackFeatureRequest(BaseModel):
    """追踪功能使用请求"""
    user_id: str
    feature_name: str
    action: str = "use"


@router.post("/track/feature", response_model=APIResponse)
async def track_feature(request: TrackFeatureRequest):
    """追踪功能使用"""
    try:
        tracker = get_user_tracker()
        record_id = tracker.track_feature_usage(
            user_id=request.user_id,
            feature_name=request.feature_name,
            action=request.action
        )
        return APIResponse(data={"record_id": record_id}, message="追踪成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 导出接口
# ============================================

@router.get("/export/report", response_model=APIResponse)
async def export_report(
    hours: int = Query(24, description="统计时长"),
    format_type: str = Query("json", description="导出格式")
):
    """导出分析报告"""
    try:
        service = get_stats_service()
        report = service.export_report(hours=hours)
        return APIResponse(data=report, message="导出成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/user", response_model=APIResponse)
async def export_user_report(
    user_id: str = Query(..., description="用户 ID"),
    days: int = Query(7, description="时间范围")
):
    """导出用户报告"""
    try:
        tracker = get_user_tracker()
        report = tracker.export_user_report(user_id, days=days)
        return APIResponse(data=report, message="导出成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 仪表盘数据接口
# ============================================

@router.get("/dashboard", response_model=APIResponse)
async def get_dashboard_data(hours: int = Query(24, description="统计时长")):
    """获取仪表盘完整数据"""
    try:
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
        
        return APIResponse(data=data, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 健康检查
# ============================================

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "Analytics Service",
        "version": "3.0.0"
    }


# ============================================
# 主入口
# ============================================

