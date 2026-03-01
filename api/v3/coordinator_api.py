#!/usr/bin/env python3
"""
V3 项目协调者 API - Project Coordinator API
基于 DeepSeek V3 的智能决策系统

API 列表:
- POST /api/v3/coordinator/daily-standup - 每日站会
- POST /api/v3/coordinator/decide - 做出决策
- POST /api/v3/coordinator/evaluate - 评价改进
- POST /api/v3/coordinator/emergency - 紧急模式
- GET /api/v3/coordinator/status - 项目状态
- GET /api/v3/coordinator/decisions - 决策历史
"""

import os
import sys
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from core.project_coordinator import ProjectCoordinator


# ============================================
# FastAPI 应用
# ============================================

router = APIRouter()

coordinator: Optional[ProjectCoordinator] = None


# ============================================
# 请求模型
# ============================================

class DecisionRequest(BaseModel):
    """决策请求"""
    context: dict = Field(..., description="决策上下文")
    model: str = Field("v3", description="模型类型")


class EmergencyRequest(BaseModel):
    """紧急请求"""
    issue: str = Field(..., description="问题描述")
    model: str = Field("v3", description="模型类型")


# ============================================
# 初始化
# ============================================

@router.on_event("startup")
async def startup():
    global coordinator
    coordinator = ProjectCoordinator(model='v3')
    print("[Coordinator API] ✅ 服务初始化成功")


# ============================================
# API 路由
# ============================================

@router.post("/daily-standup", response_model=dict)
async def daily_standup():
    """
    每日站会
    
    自动评估项目状态并生成今日决策
    """
    if not coordinator:
        raise HTTPException(status_code=503, detail="服务未初始化")
    
    try:
        standup = coordinator.daily_standup()
        return {
            "success": True,
            "data": standup,
            "message": "每日站会完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decide", response_model=dict)
async def make_decision(request: DecisionRequest):
    """
    做出决策
    
    基于给定上下文做出 Go/No-Go/Pivot 决策
    """
    if not coordinator:
        raise HTTPException(status_code=503, detail="服务未初始化")
    
    try:
        decision = coordinator.make_decision(request.context)
        return {
            "success": True,
            "data": decision,
            "message": "决策完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", response_model=dict)
async def evaluate_and_improve():
    """
    评价并改进
    
    全面评价当前工作并生成改进计划
    """
    if not coordinator:
        raise HTTPException(status_code=503, detail="服务未初始化")
    
    try:
        result = coordinator.evaluate_and_improve()
        return {
            "success": True,
            "data": result,
            "message": "评价完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency", response_model=dict)
async def emergency_mode(request: EmergencyRequest):
    """
    紧急模式
    
    处理突发问题
    """
    if not coordinator:
        raise HTTPException(status_code=503, detail="服务未初始化")
    
    try:
        result = coordinator.emergency_mode(request.issue)
        return {
            "success": True,
            "data": result,
            "message": "紧急处理完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=dict)
async def get_status(days: int = Query(7, description="天数")):
    """获取项目状态"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="服务未初始化")
    
    try:
        report_path = coordinator.generate_status_report(days)
        return {
            "success": True,
            "report_path": report_path,
            "message": "状态报告已生成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/decisions", response_model=dict)
async def get_decisions(limit: int = Query(10, description="返回数量")):
    """获取决策历史"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="服务未初始化")
    
    try:
        decisions = coordinator.decisions_log[-limit:]
        return {
            "success": True,
            "data": decisions,
            "count": len(decisions),
            "message": "获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-decisions", response_model=dict)
async def save_decisions():
    """保存决策日志"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="服务未初始化")
    
    try:
        coordinator.save_decisions_log()
        return {
            "success": True,
            "message": "决策日志已保存"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 健康检查
# ============================================

@router.get("/health")
async def health():
    return {
        "status": "healthy" if coordinator else "unhealthy",
        "model": "DeepSeek V3",
        "role": "Project Coordinator"
    }


# ============================================
# 主程序
# ============================================

