#!/usr/bin/env python3
"""
V3 智能选题 API 路由 - Topics API
V3 智能选题模块的 RESTful API 接口

API 列表:
- POST /api/v3/topics/generate - 批量生成选题
- GET /api/v3/topics - 获取选题列表
- GET /api/v3/topics/:id - 选题详情
- POST /api/v3/topics/:id/score - 重新评分
- GET /api/v3/topics/compare - 选题对比
- GET /api/v3/topics/industries - 行业列表
- GET /api/v3/topics/angles - 角度列表

技术栈：FastAPI + Pydantic
"""

import os
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Query, Body, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from models.topic import Topic, TopicScore, Industry, Angle, TopicComparison, GenerateRequest


# ============================================
# FastAPI 应用初始化
# ============================================

app = FastAPI(
    title="V3 Topics API",
    description="智能选题模块 API - 提供选题生成、评分、对比等功能",
    version="3.0.0",
    docs_url="/api/v3/topics/docs",
    redoc_url="/api/v3/topics/redoc"
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
topic_service = None


def get_topic_service():
    """获取 TopicService 单例"""
    global topic_service
    if topic_service is None:
        from core.topic_service import TopicService
        topic_service = TopicService()
    return topic_service


# ============================================
# 请求/响应模型
# ============================================

class APIResponse(BaseModel):
    """通用 API 响应模型"""
    success: bool = True
    data: Any = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)


class TopicListResponse(BaseModel):
    """选题列表响应"""
    success: bool = True
    data: List[Topic] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    timestamp: datetime = Field(default_factory=datetime.now)


class GenerateTopicsRequest(BaseModel):
    """生成选题请求"""
    industries: List[str] = Field(..., description="行业列表", example=["教育", "科技"])
    angles: List[str] = Field(..., description="角度列表", example=["深度分析", "数据解读"])
    hotnews_ids: Optional[List[str]] = Field(None, description="基于热点 ID 列表")
    count: int = Field(20, ge=1, le=100, description="生成数量")
    min_score: float = Field(60.0, ge=0, le=100, description="最低评分要求")


class ScoreResponse(BaseModel):
    """评分响应"""
    success: bool = True
    data: TopicScore = None
    timestamp: datetime = Field(default_factory=datetime.now)


class CompareResponse(BaseModel):
    """对比响应"""
    success: bool = True
    data: TopicComparison = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================
# API 路由
# ============================================

@app.post("/api/v3/topics/generate", response_model=APIResponse, tags=["选题生成"])
async def generate_topics(request: GenerateTopicsRequest):
    """
    批量生成选题
    
    支持多行业、多角度组合生成，自动进行 5 维智能评分
    
    **请求示例:**
    ```json
    {
        "industries": ["教育", "科技"],
        "angles": ["深度分析", "数据解读"],
        "hotnews_ids": ["weibo_12345", "zhihu_67890"],
        "count": 20,
        "min_score": 60.0
    }
    ```
    """
    try:
        service = get_topic_service()
        
        topics = service.generate_topics(
            industries=request.industries,
            angles=request.angles,
            hotnews_ids=request.hotnews_ids,
            count=request.count,
            min_score=request.min_score
        )
        
        # 保存到数据库
        for topic in topics:
            service.save_topic(topic)
        
        return APIResponse(
            success=True,
            data={
                "topics": [t.to_dict() for t in topics],
                "count": len(topics),
                "avg_score": sum(t.score_total or 0 for t in topics) / max(len(topics), 1)
            },
            message=f"成功生成 {len(topics)} 个选题"
        )
    
    except Exception as e:
        print(f"[API] ❌ 生成选题失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/topics", response_model=TopicListResponse, tags=["选题查询"])
async def get_topics(
    industry: Optional[str] = Query(None, description="行业筛选"),
    angle: Optional[str] = Query(None, description="角度筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    min_score: Optional[float] = Query(None, description="最低评分"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取选题列表
    
    支持按行业、角度、状态、评分筛选，支持分页
    """
    try:
        service = get_topic_service()
        
        topics, total = service.get_topic_list(
            industry=industry,
            angle=angle,
            status=status,
            min_score=min_score,
            page=page,
            page_size=page_size
        )
        
        return TopicListResponse(
            success=True,
            data=[t.to_dict() for t in topics],
            total=total,
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        print(f"[API] ❌ 获取选题列表失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/topics/{topic_id}", response_model=APIResponse, tags=["选题查询"])
async def get_topic(topic_id: str = Path(..., description="选题 ID")):
    """
    获取选题详情
    
    包含完整的选题信息和 5 维评分详情
    """
    try:
        service = get_topic_service()
        
        topic = service.get_topic_by_id(topic_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail=f"选题 {topic_id} 不存在")
        
        return APIResponse(
            success=True,
            data=topic.to_dict(),
            message="获取成功"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] ❌ 获取选题详情失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v3/topics/{topic_id}/score", response_model=ScoreResponse, tags=["选题评分"])
async def rescore_topic(topic_id: str = Path(..., description="选题 ID")):
    """
    重新评分选题
    
    对已有选题进行 5 维智能评分更新
    """
    try:
        service = get_topic_service()
        
        topic = service.get_topic_by_id(topic_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail=f"选题 {topic_id} 不存在")
        
        # 重新评分
        score = service.score_topic(topic)
        
        # 更新评分
        topic.score = score
        topic.score_total = score.total
        topic.grade = score.grade
        service.save_topic(topic)
        
        return ScoreResponse(
            success=True,
            data=score.to_dict(),
            timestamp=datetime.now()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] ❌ 重新评分失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/topics/compare", response_model=CompareResponse, tags=["选题对比"])
async def compare_topics(
    ids: str = Query(..., description="选题 ID 列表，逗号分隔", example="topic_001,topic_002,topic_003")
):
    """
    选题对比分析
    
    对比多个选题的评分、维度，给出推荐建议
    
    **请求示例:**
    ```
    GET /api/v3/topics/compare?ids=topic_001,topic_002,topic_003
    ```
    """
    try:
        service = get_topic_service()
        
        topic_ids = [id.strip() for id in ids.split(",") if id.strip()]
        
        if not topic_ids:
            raise HTTPException(status_code=400, detail="请提供至少一个选题 ID")
        
        comparison = service.compare_topics(topic_ids)
        
        return CompareResponse(
            success=True,
            data={
                "topics": [t.to_dict() for t in comparison.topics],
                "comparison": comparison.comparison,
                "recommendation": comparison.recommendation
            },
            timestamp=datetime.now()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] ❌ 选题对比失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/topics/industries", response_model=APIResponse, tags=["配置管理"])
async def get_industries():
    """
    获取行业列表
    
    返回所有启用的行业配置
    """
    try:
        service = get_topic_service()
        
        industries = service.get_industries()
        
        return APIResponse(
            success=True,
            data=[ind.to_dict() for ind in industries],
            message=f"获取 {len(industries)} 个行业"
        )
    
    except Exception as e:
        print(f"[API] ❌ 获取行业列表失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v3/topics/angles", response_model=APIResponse, tags=["配置管理"])
async def get_angles():
    """
    获取角度列表
    
    返回所有启用的角度配置
    """
    try:
        service = get_topic_service()
        
        angles = service.get_angles()
        
        return APIResponse(
            success=True,
            data=[angle.to_dict() for angle in angles],
            message=f"获取 {len(angles)} 个角度"
        )
    
    except Exception as e:
        print(f"[API] ❌ 获取角度列表失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 健康检查
# ============================================

@app.get("/api/v3/topics/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "V3 Topics API",
        "timestamp": datetime.now().isoformat()
    }


# ============================================
# 主程序
# ============================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎯 V3 智能选题 API 服务")
    print("="*70)
    print("\n启动服务：http://localhost:8002")
    print("API 文档：http://localhost:8002/api/v3/topics/docs")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
