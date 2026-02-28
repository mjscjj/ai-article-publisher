#!/usr/bin/env python3
"""
V3 热点中心 API 路由 - HotNews API
V3 热点中心模块的 RESTful API 接口

API 列表:
- GET /api/v3/hotnews - 热点列表 (支持筛选)
- GET /api/v3/hotnews/:id - 热点详情
- GET /api/v3/hotnews/:id/trend - 热度趋势
- POST /api/v3/hotnews/subscribe - 订阅热点
- GET /api/v3/hotnews/search - 搜索热点

技术栈：FastAPI + Pydantic
"""

import os
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from models.hotnews import HotNews, Subscription, TrendData, PaginatedResponse
from core.hotnews_service import HotNewsService


# ============================================
# FastAPI 应用初始化
# ============================================

app = FastAPI(
    title="V3 HotNews API",
    description="热点中心模块 API - 提供热点查询、订阅、搜索等功能",
    version="3.0.0",
    docs_url="/api/v3/docs",
    redoc_url="/api/v3/redoc"
)

# CORS 配置 (允许跨域访问)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局服务实例
hotnews_service: Optional[HotNewsService] = None


# ============================================
# 请求/响应模型
# ============================================

class SubscribeRequest(BaseModel):
    """订阅请求模型"""
    keyword: str = Field(..., description="订阅关键词", max_length=100)
    platform: Optional[str] = Field(None, description="订阅平台", max_length=50)
    category: Optional[str] = Field(None, description="订阅分类", max_length=50)
    notify_enabled: bool = Field(True, description="是否启用通知")


class APIResponse(BaseModel):
    """通用 API 响应模型"""
    success: bool = True
    data: Any = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)


class HotNewsListResponse(BaseModel):
    """热点列表响应"""
    success: bool = True
    data: PaginatedResponse
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)


class HotNewsDetailResponse(BaseModel):
    """热点详情响应"""
    success: bool = True
    data: Optional[HotNews] = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)


class TrendResponse(BaseModel):
    """趋势数据响应"""
    success: bool = True
    data: Optional[TrendData] = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)


class SubscribeResponse(BaseModel):
    """订阅响应"""
    success: bool = True
    data: Optional[Subscription] = None
    message: str = "订阅成功"
    timestamp: datetime = Field(default_factory=datetime.now)


class SearchResponse(BaseModel):
    """搜索响应"""
    success: bool = True
    data: List[HotNews] = Field(default_factory=list)
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================
# 生命周期管理
# ============================================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global hotnews_service
    try:
        hotnews_service = HotNewsService()
        print("✅ V3 HotNews API 启动成功")
    except Exception as e:
        print(f"❌ API 启动失败：{e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    global hotnews_service
    if hotnews_service:
        hotnews_service.close()
        print("✅ V3 HotNews API 已关闭")


# ============================================
# API 路由：热点列表
# ============================================

@app.get("/api/v3/hotnews", response_model=HotNewsListResponse)
async def get_hotnews_list(
    platform: Optional[str] = Query(None, description="平台筛选 (微博/知乎/B 站等)"),
    category: Optional[str] = Query(None, description="分类筛选 (科技/教育/财经等)"),
    time_range: str = Query("24h", description="时间范围 (1h/6h/24h/7d)"),
    min_heat: int = Query(0, description="最低热度值", ge=0),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(50, description="每页数量", ge=1, le=100)
):
    """
    获取热点列表
    
    支持多维度筛选:
    - **platform**: 按平台筛选 (微博/知乎/B 站/抖音等)
    - **category**: 按分类筛选 (科技/教育/财经/娱乐等)
    - **time_range**: 时间范围 (1h/6h/24h/7d)
    - **min_heat**: 最低热度值
    - **keyword**: 关键词过滤
    
    返回分页结果
    """
    if not hotnews_service:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    try:
        result = hotnews_service.get_hotlist(
            platform=platform,
            category=category,
            time_range=time_range,
            min_heat=min_heat,
            keyword=keyword,
            page=page,
            page_size=page_size
        )
        
        return HotNewsListResponse(
            success=True,
            data=result,
            message=f"获取成功，共 {result.total} 条记录"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API 路由：热点详情
# ============================================

@app.get("/api/v3/hotnews/{item_id}", response_model=HotNewsDetailResponse)
async def get_hotnews_detail(item_id: str):
    """
    获取热点详情
    
    - **item_id**: 热点唯一标识
    """
    if not hotnews_service:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    try:
        hotnews = hotnews_service.get_by_id(item_id)
        
        if not hotnews:
            return HotNewsDetailResponse(
                success=False,
                data=None,
                message="热点不存在"
            )
        
        return HotNewsDetailResponse(
            success=True,
            data=hotnews,
            message="获取成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API 路由：热度趋势
# ============================================

@app.get("/api/v3/hotnews/{item_id}/trend", response_model=TrendResponse)
async def get_hotnews_trend(
    item_id: str,
    hours: int = Query(24, description="时间范围 (小时)", ge=1, le=168)
):
    """
    获取热点的热度趋势
    
    - **item_id**: 热点唯一标识
    - **hours**: 时间范围 (默认 24 小时，最大 168 小时/7 天)
    """
    if not hotnews_service:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    try:
        trend = hotnews_service.get_trend(item_id, hours=hours)
        
        if not trend:
            return TrendResponse(
                success=False,
                data=None,
                message="热点不存在或无趋势数据"
            )
        
        return TrendResponse(
            success=True,
            data=trend,
            message="获取成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API 路由：订阅热点
# ============================================

@app.post("/api/v3/hotnews/subscribe", response_model=SubscribeResponse)
async def subscribe_hotnews(request: SubscribeRequest):
    """
    订阅热点
    
    请求体:
    - **keyword**: 订阅关键词 (必填)
    - **platform**: 订阅平台 (可选)
    - **category**: 订阅分类 (可选)
    - **notify_enabled**: 是否启用通知 (默认 True)
    """
    if not hotnews_service:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    try:
        # 临时使用测试用户 ID
        user_id = "test_user_001"
        
        subscription = hotnews_service.subscribe(
            keyword=request.keyword,
            user_id=user_id,
            platform=request.platform,
            category=request.category,
            notify_enabled=request.notify_enabled
        )
        
        return SubscribeResponse(
            success=True,
            data=subscription,
            message=f"成功订阅关键词：{request.keyword}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API 路由：搜索热点
# ============================================

@app.get("/api/v3/hotnews/search", response_model=SearchResponse)
async def search_hotnews(
    q: str = Query(..., description="搜索关键词", min_length=1),
    platform: Optional[str] = Query(None, description="平台筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    time_range: str = Query("24h", description="时间范围 (1h/6h/24h/7d)"),
    limit: int = Query(50, description="返回数量限制", ge=1, le=100)
):
    """
    搜索热点 (全文检索)
    
    - **q**: 搜索关键词 (必填)
    - **platform**: 平台筛选 (可选)
    - **category**: 分类筛选 (可选)
    - **time_range**: 时间范围 (可选)
    - **limit**: 返回数量限制 (可选)
    """
    if not hotnews_service:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    try:
        results = hotnews_service.search(
            query=q,
            platform=platform,
            category=category,
            time_range=time_range,
            limit=limit
        )
        
        return SearchResponse(
            success=True,
            data=results,
            message=f"搜索到 {len(results)} 条结果"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API 路由：用户订阅列表
# ============================================

@app.get("/api/v3/hotnews/subscriptions", response_model=APIResponse)
async def get_subscriptions(user_id: str = Query("test_user_001", description="用户 ID")):
    """
    获取用户的订阅列表
    
    - **user_id**: 用户 ID (临时使用测试用户)
    """
    if not hotnews_service:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    try:
        subscriptions = hotnews_service.get_subscriptions(user_id)
        
        return APIResponse(
            success=True,
            data=subscriptions,
            message=f"获取到 {len(subscriptions)} 条订阅"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API 路由：取消订阅
# ============================================

@app.delete("/api/v3/hotnews/subscribe/{keyword}", response_model=APIResponse)
async def unsubscribe_hotnews(
    keyword: str,
    user_id: str = Query("test_user_001", description="用户 ID")
):
    """
    取消订阅
    
    - **keyword**: 订阅关键词
    - **user_id**: 用户 ID
    """
    if not hotnews_service:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    try:
        success = hotnews_service.unsubscribe(user_id, keyword)
        
        if success:
            return APIResponse(
                success=True,
                data={"keyword": keyword},
                message=f"已取消订阅：{keyword}"
            )
        else:
            return APIResponse(
                success=False,
                data=None,
                message="订阅不存在或取消失败"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API 路由：统计信息
# ============================================

@app.get("/api/v3/hotnews/statistics", response_model=APIResponse)
async def get_statistics(days: int = Query(7, description="统计天数", ge=1, le=30)):
    """
    获取统计信息
    
    - **days**: 统计天数 (默认 7 天)
    """
    if not hotnews_service:
        raise HTTPException(status_code=500, detail="服务未初始化")
    
    try:
        stats = hotnews_service.get_statistics(days=days)
        
        return APIResponse(
            success=True,
            data=stats,
            message="获取成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 健康检查
# ============================================

@app.get("/api/v3/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "V3 HotNews API",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }


# ============================================
# 运行配置
# ============================================

if __name__ == "__main__":
    print("🚀 启动 V3 HotNews API...")
    uvicorn.run(
        "hotnews:app",
        host="0.0.0.0",
        port=8081,  # 使用 8081 端口，避免与现有 API 冲突
        reload=True
    )
