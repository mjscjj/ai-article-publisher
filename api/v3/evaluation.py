#!/usr/bin/env python3
"""
V3 工作评价 API - Evaluation API
基于 DeepSeek V3 的智能评价系统

API 列表:
- POST /api/v3/evaluation/evaluate - 评价文章/选题
- GET /api/v3/evaluation/history - 评价历史
- GET /api/v3/evaluation/statistics - 统计数据
- POST /api/v3/evaluation/batch - 批量评价
"""

import os
import sys
from datetime import datetime
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from core.evaluation_service import EvaluationService
from models.evaluation import EvaluationResult, EvaluationHistory


# ============================================
# FastAPI 应用初始化
# ============================================

app = FastAPI(
    title="V3 Evaluation API",
    description="工作评价模块 API - 基于 DeepSeek V3 的智能评价",
    version="3.0.0",
    docs_url="/api/v3/evaluation/docs",
    redoc_url="/api/v3/evaluation/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局服务实例 (使用 DeepSeek V3)
evaluation_service: Optional[EvaluationService] = None


# ============================================
# 请求/响应模型
# ============================================

class EvaluateRequest(BaseModel):
    """评价请求"""
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    type: str = Field("article", description="类型 (article|topic)")
    model: str = Field("v3", description="模型 (free|chat|v3)")
    save: bool = Field(True, description="是否保存")


class BatchEvaluateRequest(BaseModel):
    """批量评价请求"""
    items: List[dict] = Field(..., description="评价项列表")
    type: str = Field("article", description="类型")
    model: str = Field("v3", description="模型")


# ============================================
# 初始化事件
# ============================================

@app.on_event("startup")
async def startup_event():
    """启动时初始化服务"""
    global evaluation_service
    try:
        evaluation_service = EvaluationService(model='v3')  # 使用 DeepSeek V3
        print("[Evaluation API] ✅ 服务初始化成功 (DeepSeek V3)")
    except Exception as e:
        print(f"[Evaluation API] ❌ 服务初始化失败：{e}")
        evaluation_service = None


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理资源"""
    global evaluation_service
    if evaluation_service:
        evaluation_service.close()


# ============================================
# API 路由
# ============================================

@app.post("/evaluate", response_model=dict)
async def evaluate(request: EvaluateRequest):
    """
    评价文章/选题
    
    - **title**: 标题
    - **content**: 内容
    - **type**: 类型 (article|topic)
    - **model**: 模型 (free|chat|v3)
    - **save**: 是否保存
    """
    if not evaluation_service:
        raise HTTPException(status_code=503, detail="评价服务未初始化")
    
    try:
        if request.type == 'topic':
            result = evaluation_service.evaluate_topic(
                request.title,
                request.content,
                save=request.save
            )
        else:
            result = evaluation_service.evaluate_article(
                request.title,
                request.content,
                save=request.save
            )
        
        return {
            "success": True,
            "data": result,
            "message": "评价完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history", response_model=dict)
async def get_history(
    target_type: Optional[str] = Query(None, description="类型 (article|topic)"),
    limit: int = Query(50, description="返回数量")
):
    """获取评价历史"""
    if not evaluation_service:
        raise HTTPException(status_code=503, detail="评价服务未初始化")
    
    try:
        history = evaluation_service.get_evaluation_history(
            target_type=target_type,
            limit=limit
        )
        
        return {
            "success": True,
            "data": history,
            "message": "获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics", response_model=dict)
async def get_statistics(
    days: int = Query(7, description="统计天数")
):
    """获取统计数据"""
    if not evaluation_service:
        raise HTTPException(status_code=503, detail="评价服务未初始化")
    
    try:
        stats = evaluation_service.get_statistics(days=days)
        
        return {
            "success": True,
            "data": stats,
            "message": "获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch", response_model=dict)
async def batch_evaluate(request: BatchEvaluateRequest):
    """批量评价"""
    if not evaluation_service:
        raise HTTPException(status_code=503, detail="评价服务未初始化")
    
    try:
        results = evaluation_service.batch_evaluate(
            request.items,
            eval_type=request.type
        )
        
        return {
            "success": True,
            "data": results,
            "count": len(results),
            "message": f"批量评价完成 ({len(results)} 个)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 健康检查
# ============================================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy" if evaluation_service else "unhealthy",
        "model": "DeepSeek V3",
        "service": "Evaluation Service"
    }


# ============================================
# 主程序
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "evaluation:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
