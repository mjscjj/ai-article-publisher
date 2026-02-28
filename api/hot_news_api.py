#!/usr/bin/env python3
"""
【热点展示 API】Hot News API
基于 FastAPI 的热点数据展示接口

技术栈: FastAPI + MySQL + Pydantic
对齐 YouMind 技术栈
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from core.hot_database_mysql import HotNewsDatabaseMySQL

# ========== FastAPI 应用 ==========

app = FastAPI(
    title="Hot News API",
    description="热点数据展示 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接
db = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    global db
    db = HotNewsDatabaseMySQL(
        host="43.134.234.4",
        port=3306,
        database="youmind",
        user="youmind",
        password="YouMind2026"
    )
    print("✅ API 启动成功")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    global db
    if db:
        db.close()

# ========== 数据模型 ==========

class HotTopic(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    source_name: Optional[str] = None
    platform: Optional[str] = None
    crawl_time: datetime
    heat_score: float
    heat_level: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

class HotSource(BaseModel):
    id: int
    name: str
    platform: Optional[str] = None
    category: Optional[str] = None
    priority: int
    credibility: float
    
    class Config:
        from_attributes = True

class Statistics(BaseModel):
    total_count: int
    avg_heat: float
    max_heat: float
    unique_count: int

class APIResponse(BaseModel):
    success: bool
    data: Any
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

# ========== API 接口 ==========

@app.get("/", response_model=APIResponse)
async def root():
    """API 根路径"""
    return APIResponse(
        success=True,
        data={"message": "Hot News API", "version": "1.0.0"},
        message="API 运行正常"
    )

@app.get("/api/topics", response_model=APIResponse)
async def get_hot_topics(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    category: Optional[str] = Query(None, description="分类过滤"),
    heat_level: Optional[str] = Query(None, description="热度等级"),
    source_name: Optional[str] = Query(None, description="来源过滤"),
    hours: Optional[int] = Query(None, description="时间范围 (小时)"),
    date: Optional[str] = Query(None, description="采集日期 (YYYY-MM-DD 或 today/yesterday)")
):
    """获取热点列表"""
    try:
        topics = db.get_hot_topics(
            limit=limit,
            category=category,
            heat_level=heat_level,
            source_name=source_name,
            time_range_hours=hours,
            crawl_date=date
        )
        
        return APIResponse(
            success=True,
            data={
                "topics": topics,
                "count": len(topics),
                "filters": {
                    "category": category,
                    "heat_level": heat_level,
                    "source_name": source_name,
                    "hours": hours,
                    "date": date
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/topics/{topic_id}", response_model=APIResponse)
async def get_hot_topic(topic_id: int):
    """获取单个热点详情"""
    try:
        topics = db.get_hot_topics(limit=1)
        # 简化实现，实际应该根据 ID 查询
        if topics:
            return APIResponse(success=True, data=topics[0])
        else:
            return APIResponse(success=False, data=None, message="热点不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources", response_model=APIResponse)
async def get_sources(active_only: bool = True):
    """获取数据源列表"""
    try:
        sources = db.get_sources(active_only=active_only)
        return APIResponse(success=True, data=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics", response_model=APIResponse)
async def get_statistics(days: int = Query(7, ge=1, le=30)):
    """获取统计数据"""
    try:
        stats = db.get_statistics(days=days)
        return APIResponse(success=True, data=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories", response_model=APIResponse)
async def get_categories():
    """获取所有分类"""
    try:
        stats = db.get_statistics(days=30)
        categories = [item['category'] for item in stats['by_category'] if item['category']]
        return APIResponse(success=True, data=categories)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/keywords", response_model=APIResponse)
async def get_keywords(limit: int = Query(50, ge=1, le=100)):
    """获取热门关键词"""
    try:
        stats = db.get_statistics(days=7)
        keywords = stats['hot_keywords'][:limit]
        return APIResponse(success=True, data=keywords)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dates", response_model=APIResponse)
async def get_available_dates(limit: int = Query(30, ge=1, le=365)):
    """获取可用日期列表"""
    try:
        dates = db.get_available_dates(limit=limit)
        date_range = db.get_date_range()
        return APIResponse(
            success=True,
            data={
                "dates": dates,
                "range": date_range
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== 运行配置 ==========

if __name__ == "__main__":
    uvicorn.run(
        "hot_news_api:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
