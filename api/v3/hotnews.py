#!/usr/bin/env python3
"""V3 热点中心 API 路由 - HotNews API"""

import os
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from models.hotnews import HotNews, Subscription, TrendData, PaginatedResponse
from core.hotnews_service import HotNewsService

router = APIRouter()

hotnews_service: Optional[HotNewsService] = None

def init_service():
    global hotnews_service
    if hotnews_service is None:
        hotnews_service = HotNewsService()

class SubscribeRequest(BaseModel):
    keyword: str = Field(..., description="订阅关键词", max_length=100)
    platform: Optional[str] = Field(None, description="订阅平台", max_length=50)
    category: Optional[str] = Field(None, description="订阅分类", max_length=50)
    notify_enabled: bool = Field(True, description="是否启用通知")

class APIResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

class HotNewsListResponse(BaseModel):
    success: bool = True
    data: PaginatedResponse
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

class HotNewsDetailResponse(BaseModel):
    success: bool = True
    data: Optional[HotNews] = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

class TrendResponse(BaseModel):
    success: bool = True
    data: Optional[TrendData] = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

class SubscribeResponse(BaseModel):
    success: bool = True
    data: Optional[Subscription] = None
    message: str = "订阅成功"
    timestamp: datetime = Field(default_factory=datetime.now)

class SearchResponse(BaseModel):
    success: bool = True
    data: List[HotNews] = Field(default_factory=list)
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

@router.get("/search", response_model=SearchResponse)
async def search_hotnews(
    q: str = Query(..., description="搜索关键词", min_length=1),
    platform: Optional[str] = Query(None, description="平台筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    time_range: str = Query("24h", description="时间范围 (1h/6h/24h/7d)"),
    limit: int = Query(50, description="返回数量限制", ge=1, le=100)
):
    init_service()
    try:
        results = hotnews_service.search(query=q, platform=platform, category=category, time_range=time_range, limit=limit)
        return SearchResponse(success=True, data=results, message=f"搜索到 {len(results)} 条结果")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscribe", response_model=SubscribeResponse)
async def subscribe_hotnews(request: SubscribeRequest):
    init_service()
    try:
        user_id = "test_user_001"
        subscription = hotnews_service.subscribe(keyword=request.keyword, user_id=user_id, platform=request.platform, category=request.category, notify_enabled=request.notify_enabled)
        return SubscribeResponse(success=True, data=subscription, message=f"成功订阅关键词：{request.keyword}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscriptions", response_model=APIResponse)
async def get_subscriptions(user_id: str = Query("test_user_001", description="用户 ID")):
    init_service()
    try:
        subscriptions = hotnews_service.get_subscriptions(user_id)
        return APIResponse(success=True, data=subscriptions, message=f"获取到 {len(subscriptions)} 条订阅")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/subscribe/{keyword}", response_model=APIResponse)
async def unsubscribe_hotnews(keyword: str, user_id: str = Query("test_user_001", description="用户 ID")):
    init_service()
    try:
        success = hotnews_service.unsubscribe(user_id, keyword)
        if success:
            return APIResponse(success=True, data={"keyword": keyword}, message=f"已取消订阅：{keyword}")
        else:
            return APIResponse(success=False, data=None, message="订阅不存在或取消失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=APIResponse)
async def get_statistics(days: int = Query(7, description="统计天数", ge=1, le=30)):
    init_service()
    try:
        stats = hotnews_service.get_statistics(days=days)
        return APIResponse(success=True, data=stats, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=HotNewsListResponse)
async def get_hotnews_list(
    platform: Optional[str] = Query(None, description="平台筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    time_range: str = Query("24h", description="时间范围 (1h/6h/24h/7d)"),
    min_heat: int = Query(0, description="最低热度值", ge=0),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(50, description="每页数量", ge=1, le=100)
):
    init_service()
    try:
        result = hotnews_service.get_hotlist(platform=platform, category=category, time_range=time_range, min_heat=min_heat, keyword=keyword, page=page, page_size=page_size)
        return HotNewsListResponse(success=True, data=result, message=f"获取成功，共 {result.total} 条记录")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_id}", response_model=HotNewsDetailResponse)
async def get_hotnews_detail(item_id: str):
    init_service()
    try:
        hotnews = hotnews_service.get_by_id(item_id)
        if not hotnews:
            return HotNewsDetailResponse(success=False, data=None, message="热点不存在")
        return HotNewsDetailResponse(success=True, data=hotnews, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_id}/trend", response_model=TrendResponse)
async def get_hotnews_trend(item_id: str, hours: int = Query(24, description="时间范围 (小时)", ge=1, le=168)):
    init_service()
    try:
        trend = hotnews_service.get_trend(item_id, hours=hours)
        if not trend:
            return TrendResponse(success=False, data=None, message="热点不存在或无趋势数据")
        return TrendResponse(success=True, data=trend, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    init_service()
    return {"status": "healthy", "service": "V3 HotNews API", "version": "3.0.0"}


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "HotNews Center", "version": "3.0.0"}
