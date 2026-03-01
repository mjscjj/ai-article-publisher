#!/usr/bin/env python3
"""
V3 工作 Review API - Work Review API
基于 DeepSeek V3 的全面工作评价系统

API 列表:
- POST /api/v3/review/comprehensive - 全面 Review
- POST /api/v3/review/code - 代码 Review
- POST /api/v3/review/docs - 文档 Review
- POST /api/v3/review/progress - 进度 Review
- POST /api/v3/review/tests - 测试 Review
- POST /api/v3/review/improvement-plan - 生成改进计划
- GET /api/v3/review/history - Review 历史
"""

import os
import sys
from datetime import datetime
from typing import Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from core.work_review_system import WorkReviewSystem


# ============================================
# FastAPI 应用初始化
# ============================================

router = APIRouter()

# 全局 Review 系统实例
review_system: Optional[WorkReviewSystem] = None


# ============================================
# 请求模型
# ============================================

class CodeReviewRequest(BaseModel):
    """代码 Review 请求"""
    file_paths: Optional[List[str]] = Field(None, description="文件路径列表")
    model: str = Field("v3", description="模型类型")


class DocReviewRequest(BaseModel):
    """文档 Review 请求"""
    doc_paths: Optional[List[str]] = Field(None, description="文档路径列表")
    model: str = Field("v3", description="模型类型")


class ProgressReviewRequest(BaseModel):
    """进度 Review 请求"""
    days: int = Field(7, description="评价最近 N 天")
    model: str = Field("v3", description="模型类型")


class TestReviewRequest(BaseModel):
    """测试 Review 请求"""
    test_paths: Optional[List[str]] = Field(None, description="测试文件路径")
    model: str = Field("v3", description="模型类型")


class ImprovementPlanRequest(BaseModel):
    """改进计划请求"""
    review_result: dict = Field(..., description="Review 结果")


# ============================================
# 初始化事件
# ============================================

@router.on_event("startup")
async def startup_event():
    """启动时初始化"""
    global review_system
    review_system = WorkReviewSystem(model='v3')
    print("[Review API] ✅ 服务初始化成功 (DeepSeek V3)")


@router.on_event("shutdown")
async def shutdown_event():
    """关闭时清理"""
    global review_system
    if review_system:
        print("[Review API] ✅ 服务已关闭")


# ============================================
# API 路由
# ============================================

@router.post("/comprehensive", response_model=dict)
async def comprehensive_review(model: str = "v3"):
    """
    全面综合评价
    
    包括：代码 + 文档 + 进度 + 测试
    """
    if not review_system:
        raise HTTPException(status_code=503, detail="Review 服务未初始化")
    
    try:
        result = review_system.comprehensive_review()
        return {
            "success": True,
            "data": result,
            "message": "全面 Review 完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code", response_model=dict)
async def review_code(request: CodeReviewRequest):
    """代码质量 Review"""
    if not review_system:
        raise HTTPException(status_code=503, detail="Review 服务未初始化")
    
    try:
        result = review_system.review_code(request.file_paths)
        return {
            "success": True,
            "data": result,
            "message": "代码 Review 完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/docs", response_model=dict)
async def review_docs(request: DocReviewRequest):
    """文档质量 Review"""
    if not review_system:
        raise HTTPException(status_code=503, detail="Review 服务未初始化")
    
    try:
        result = review_system.review_documentation(request.doc_paths)
        return {
            "success": True,
            "data": result,
            "message": "文档 Review 完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress", response_model=dict)
async def review_progress(request: ProgressReviewRequest):
    """项目进度 Review"""
    if not review_system:
        raise HTTPException(status_code=503, detail="Review 服务未初始化")
    
    try:
        result = review_system.review_progress(days=request.days)
        return {
            "success": True,
            "data": result,
            "message": f"{request.days}天进度 Review 完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tests", response_model=dict)
async def review_tests(request: TestReviewRequest):
    """测试覆盖 Review"""
    if not review_system:
        raise HTTPException(status_code=503, detail="Review 服务未初始化")
    
    try:
        result = review_system.review_tests(request.test_paths)
        return {
            "success": True,
            "data": result,
            "message": "测试 Review 完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improvement-plan", response_model=dict)
async def generate_improvement_plan(request: ImprovementPlanRequest):
    """生成改进计划"""
    if not review_system:
        raise HTTPException(status_code=503, detail="Review 服务未初始化")
    
    try:
        plan = review_system.generate_improvement_plan(request.review_result)
        return {
            "success": True,
            "data": plan,
            "message": "改进计划生成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=dict)
async def get_review_history(limit: int = Query(10, description="返回数量")):
    """获取 Review 历史"""
    if not review_system:
        raise HTTPException(status_code=503, detail="Review 服务未初始化")
    
    try:
        history = review_system.review_results[-limit:]
        return {
            "success": True,
            "data": history,
            "count": len(history),
            "message": "获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-report", response_model=dict)
async def save_report(output_path: Optional[str] = None):
    """保存 Review 报告"""
    if not review_system:
        raise HTTPException(status_code=503, detail="Review 服务未初始化")
    
    try:
        path = review_system.save_review_report(output_path)
        return {
            "success": True,
            "path": str(path),
            "message": "报告已保存"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 健康检查
# ============================================

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy" if review_system else "unhealthy",
        "model": "DeepSeek V3",
        "service": "Work Review System"
    }


# ============================================
# 定时 Review 任务
# ============================================

@router.post("/schedule-daily-review", response_model=dict)
async def schedule_daily_review():
    """
    调度每日 Review (可配合 cron 使用)
    
    每天自动执行全面 Review
    """
    if not review_system:
        raise HTTPException(status_code=503, detail="Review 服务未初始化")
    
    try:
        # 执行 Review
        result = review_system.comprehensive_review()
        
        # 生成改进计划
        plan = review_system.generate_improvement_plan(result)
        
        # 保存报告
        report_path = review_system.save_review_report()
        
        return {
            "success": True,
            "score": result['total_score'],
            "grade": result['grade'],
            "improvement_plan": plan,
            "report_path": str(report_path),
            "message": "每日 Review 完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 主程序
# ============================================

