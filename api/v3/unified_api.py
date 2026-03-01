#!/usr/bin/env python3
"""V3 统一 API 服务 - 所有模块整合"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="V3 Unified API",
    description="AI Article Publisher V3 - 统一 API 服务",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入所有模块的 router
from api.v3 import hotnews, topics, evaluation, review_api, coordinator_api, publish, analytics, workflow, auth

# 注册所有路由
app.include_router(hotnews.router, prefix="/api/v3/hotnews", tags=["热点中心"])
app.include_router(topics.router, prefix="/api/v3/topics", tags=["智能选题"])
app.include_router(evaluation.router, prefix="/api/v3/evaluation", tags=["工作评价"])
app.include_router(review_api.router, prefix="/api/v3/review", tags=["工作 Review"])
app.include_router(coordinator_api.router, prefix="/api/v3/coordinator", tags=["项目协调者"])
app.include_router(publish.router, prefix="/api/v3/publish", tags=["自动发布"])
app.include_router(analytics.router, prefix="/api/v3/analytics", tags=["数据看板"])
app.include_router(workflow.router, prefix="/api/v3/workflow", tags=["工作流引擎"])
app.include_router(auth.router, prefix="/api/v3/auth", tags=["用户认证"])

@app.get("/")
async def root():
    return {
        "message": "V3 Unified API",
        "version": "3.0.0",
        "docs": "/docs",
        "modules": [
            "hotnews", "topics", "evaluation", "review",
            "coordinator", "publish", "analytics", "workflow", "auth"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "V3 Unified API",
        "modules": 9,
        "version": "3.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
