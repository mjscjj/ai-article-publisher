#!/usr/bin/env python3
"""V3 智能选题 API 路由 - Topics API"""

import os
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException, Query, Body, Path
from pydantic import BaseModel, Field

from models.topic import Topic, TopicScore, Industry, Angle, TopicComparison, GenerateRequest
from core.topic_service import TopicService

router = APIRouter()
topic_service = None

def init_service():
    global topic_service
    if topic_service is None:
        topic_service = TopicService()
    return topic_service

class APIResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

class TopicListResponse(BaseModel):
    success: bool = True
    data: List[Topic] = Field(default_factory=list)
    total: int = 0
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

class CompareResponse(BaseModel):
    success: bool = True
    data: Optional[TopicComparison] = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

class ScoreResponse(BaseModel):
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

class GenerateRequestModel(BaseModel):
    industry: str = Field(..., description="行业")
    angles: List[str] = Field(default_factory=list, description="角度列表")
    count: int = Field(10, description="生成数量", ge=1, le=50)
    hotnews_ids: Optional[List[str]] = Field(None, description="关联热点 ID 列表")

@router.post("/generate", response_model=APIResponse)
async def generate_topics(request: GenerateRequestModel):
    init_service()
    try:
        service = init_service()
        topics = service.generate_batch(industry=request.industry, angles=request.angles, count=request.count, hotnews_ids=request.hotnews_ids)
        return APIResponse(success=True, data=[t.to_dict() for t in topics], message=f"生成 {len(topics)} 个选题")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=TopicListResponse)
async def get_topics(
    status: Optional[str] = Query(None, description="状态筛选"),
    industry: Optional[str] = Query(None, description="行业筛选"),
    min_score: float = Query(0, description="最低分数", ge=0),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100)
):
    init_service()
    try:
        service = init_service()
        topics = service.get_topics(status=status, industry=industry, min_score=min_score, page=page, page_size=page_size)
        return TopicListResponse(success=True, data=[t.to_dict() for t in topics], total=len(topics))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{topic_id}", response_model=APIResponse)
async def get_topic(topic_id: str = Path(..., description="选题 ID")):
    init_service()
    try:
        service = init_service()
        topic = service.get_topic_by_id(topic_id)
        if not topic:
            return APIResponse(success=False, data=None, message="选题不存在")
        return APIResponse(success=True, data=topic.to_dict(), message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{topic_id}/score", response_model=ScoreResponse)
async def rescore_topic(topic_id: str = Path(..., description="选题 ID")):
    init_service()
    try:
        service = init_service()
        score = service.evaluate_topic(topic_id)
        return ScoreResponse(success=True, data=score.to_dict() if score else None, message="重新评分完成")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare", response_model=CompareResponse)
async def compare_topics(ids: str = Query(..., description="选题 ID 列表，逗号分隔")):
    init_service()
    try:
        service = init_service()
        topic_ids = ids.split(",")
        comparison = service.compare_topics(topic_ids)
        return CompareResponse(success=True, data=comparison.to_dict() if comparison else None, message="对比完成")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/industries", response_model=APIResponse)
async def get_industries():
    init_service()
    try:
        service = init_service()
        industries = service.get_industries()
        return APIResponse(success=True, data=[ind.to_dict() for ind in industries], message=f"获取 {len(industries)} 个行业")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/angles", response_model=APIResponse)
async def get_angles():
    init_service()
    try:
        service = init_service()
        angles = service.get_angles()
        return APIResponse(success=True, data=[a.to_dict() for a in angles], message=f"获取 {len(angles)} 个角度")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "V3 Topics API", "version": "3.0.0"}
