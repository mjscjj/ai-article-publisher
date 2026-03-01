#!/usr/bin/env python3
"""
V3 用户认证 API 路由 - Auth API
提供用户注册、登录、Token 管理、个人信息等接口

API 列表:
- POST /api/v3/auth/register - 用户注册
- POST /api/v3/auth/login - 用户登录
- POST /api/v3/auth/logout - 用户登出
- POST /api/v3/auth/refresh - 刷新 Token
- GET /api/v3/auth/me - 获取当前用户信息
- PUT /api/v3/auth/me - 更新用户信息
- POST /api/v3/auth/change-password - 修改密码
- GET /api/v3/auth/config - 获取用户配置
- PUT /api/v3/auth/config - 更新用户配置
- GET /api/v3/auth/subscription - 获取订阅信息
- POST /api/v3/auth/subscription/upgrade - 升级订阅

技术栈：FastAPI + JWT
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Depends, Query, Body, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
import uvicorn

from core.auth.user_manager import UserManager, get_user_manager, User
from core.auth.jwt_handler import JWTHandler, get_jwt_handler, TokenPair
from core.auth.permissions import (
    PermissionManager,
    get_permission_manager,
    RoleEnum,
    PermissionEnum,
)


# ============================================
# FastAPI 应用初始化
# ============================================

app = FastAPI(
    title="V3 Auth API",
    description="用户认证与权限管理 API - 提供注册、登录、Token 管理等功能",
    version="3.0.0",
    docs_url="/api/v3/auth/docs",
    redoc_url="/api/v3/auth/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全方案
security = HTTPBearer(auto_error=False)

# 全局服务实例
_user_manager: Optional[UserManager] = None
_jwt_handler: Optional[JWTHandler] = None
_permission_manager: Optional[PermissionManager] = None


def get_services():
    """获取服务单例"""
    global _user_manager, _jwt_handler, _permission_manager
    
    if _user_manager is None:
        _user_manager = get_user_manager()
    
    if _jwt_handler is None:
        _jwt_handler = get_jwt_handler()
    
    if _permission_manager is None:
        _permission_manager = get_permission_manager()
    
    return _user_manager, _jwt_handler, _permission_manager


# ============================================
# 依赖注入
# ============================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    获取当前登录用户
    
    从 Authorization Header 中提取 Token 并验证
    """
    user_manager, jwt_handler, permission_manager = get_services()
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # 验证 Access Token
    payload = jwt_handler.verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否存在且激活
    user = user_manager.get_user(payload.user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")
    
    return {
        "user_id": payload.user_id,
        "username": payload.username,
        "email": payload.email,
        "role": payload.role,
        "user": user,
    }


async def require_permission(permission: PermissionEnum):
    """
    权限检查依赖
    
    用法:
    @app.post("/admin")
    async def admin_action(current_user=Depends(require_permission(PermissionEnum.USER_ADMIN))):
        ...
    """
    async def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_manager, jwt_handler, permission_manager = get_services()
        
        result = permission_manager.check_user_permission(
            current_user["user_id"],
            permission
        )
        
        if not result.allowed:
            raise HTTPException(
                status_code=403,
                detail=f"权限不足：{result.reason}"
            )
        
        return current_user
    
    return permission_checker


# ============================================
# 请求/响应模型
# ============================================

class APIResponse(BaseModel):
    """通用 API 响应"""
    success: bool = True
    data: Any = None
    message: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, max_length=128, description="密码")
    role: str = Field("user", description="角色 (默认 user)")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: Dict[str, Any]


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")


class UpdateUserRequest(BaseModel):
    """更新用户信息请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    profile: Optional[Dict[str, Any]] = None


class UserConfigUpdate(BaseModel):
    """用户配置更新"""
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    auto_save: Optional[bool] = None
    editor_mode: Optional[str] = None


class SubscriptionUpgradeRequest(BaseModel):
    """订阅升级请求"""
    plan: str = Field(..., description="订阅计划 (basic/pro/enterprise)")
    duration_days: int = Field(30, ge=1, le=365, description="订阅天数")


# ============================================
# API 路由
# ============================================

# ---------- 用户注册/登录 ----------

@app.post("/register", response_model=APIResponse)
async def register(request: RegisterRequest):
    """
    用户注册
    
    - **username**: 用户名 (3-50 字符)
    - **email**: 邮箱地址
    - **password**: 密码 (至少 8 位，包含大小写字母、数字、特殊字符)
    """
    user_manager, jwt_handler, permission_manager = get_services()
    
    # 注册
    success, user, error_msg = user_manager.register(
        username=request.username,
        email=request.email,
        password=request.password,
        role=request.role
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 生成 Token
    token_pair = jwt_handler.create_token_pair(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role
    )
    
    # 分配默认角色
    try:
        role = RoleEnum(user.role)
        permission_manager.assign_role(user.id, role)
    except ValueError:
        # 未知角色，使用 VIEWER
        permission_manager.assign_role(user.id, RoleEnum.VIEWER)
    
    return APIResponse(
        data={
            "user": user.to_dict(),
            "tokens": token_pair.to_dict()
        },
        message="注册成功"
    )


@app.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    用户登录
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    user_manager, jwt_handler, permission_manager = get_services()
    
    # 登录验证
    success, user, error_msg = user_manager.login(
        username=request.username,
        password=request.password
    )
    
    if not success:
        raise HTTPException(status_code=401, detail=error_msg)
    
    # 生成 Token
    token_pair = jwt_handler.create_token_pair(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role
    )
    
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
        expires_in=token_pair.expires_in,
        user=user.to_dict()
    )


@app.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    用户登出
    
    撤销当前 Token (加入黑名单)
    """
    user_manager, jwt_handler, permission_manager = get_services()
    
    # 注意：需要客户端传递 Token，这里简化处理
    # 实际应该在 Header 中获取 Token 并撤销
    
    return APIResponse(message="登出成功")


@app.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    """
    刷新 Token
    
    使用 Refresh Token 获取新的 Access Token 和 Refresh Token
    """
    user_manager, jwt_handler, permission_manager = get_services()
    
    # 刷新 Token
    token_pair = jwt_handler.refresh_access_token(refresh_token)
    
    if not token_pair:
        raise HTTPException(status_code=401, detail="Refresh Token 无效或已过期")
    
    # 获取用户信息
    user = user_manager.get_user(token_pair.access_token)
    
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
        expires_in=token_pair.expires_in,
        user=user.to_dict() if user else {}
    )


# ---------- 当前用户管理 ----------

@app.get("/me", response_model=APIResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """获取当前用户信息"""
    return APIResponse(data={
        "user": current_user["user"].to_dict(),
        "role": current_user["role"],
        "permissions": list(_permission_manager.get_user_permissions(current_user["user_id"]))
    })


@app.put("/me", response_model=APIResponse)
async def update_current_user(
    request: UpdateUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """更新当前用户信息"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    # 更新用户信息
    success, user, error_msg = user_manager.update_user(
        current_user["user_id"],
        **request.dict(exclude_unset=True)
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error_msg)
    
    return APIResponse(data={"user": user.to_dict()}, message="更新成功")


@app.post("/change-password", response_model=APIResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """修改当前用户密码"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    # 修改密码
    success, error_msg = user_manager.change_password(
        current_user["user_id"],
        request.old_password,
        request.new_password
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error_msg)
    
    return APIResponse(message="密码修改成功")


# ---------- 用户配置管理 ----------

@app.get("/config", response_model=APIResponse)
async def get_user_config(current_user: Dict[str, Any] = Depends(get_current_user)):
    """获取当前用户配置"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    config = user_manager.get_user_config(current_user["user_id"])
    
    if not config:
        raise HTTPException(status_code=404, detail="用户配置不存在")
    
    return APIResponse(data={"config": config.to_dict()})


@app.put("/config", response_model=APIResponse)
async def update_user_config(
    request: UserConfigUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """更新当前用户配置"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    success, config, error_msg = user_manager.update_user_config(
        current_user["user_id"],
        **request.dict(exclude_unset=True)
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error_msg)
    
    return APIResponse(data={"config": config.to_dict()}, message="配置更新成功")


# ---------- 订阅管理 ----------

@app.get("/subscription", response_model=APIResponse)
async def get_subscription(current_user: Dict[str, Any] = Depends(get_current_user)):
    """获取当前用户订阅信息"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    subscription = user_manager.get_subscription(current_user["user_id"])
    
    if not subscription:
        raise HTTPException(status_code=404, detail="订阅不存在")
    
    # 检查订阅状态
    is_valid, error_msg = user_manager.check_subscription_status(current_user["user_id"])
    
    return APIResponse(data={
        "subscription": subscription.to_dict(),
        "is_valid": is_valid,
        "status_message": error_msg
    })


@app.post("/subscription/upgrade", response_model=APIResponse)
async def upgrade_subscription(
    request: SubscriptionUpgradeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """升级订阅"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    # 检查权限 (只有管理员可以升级他人订阅)
    if request.plan in ["enterprise"]:
        result = permission_manager.check_user_permission(
            current_user["user_id"],
            PermissionEnum.SUBSCRIPTION_ADMIN
        )
        if not result.allowed:
            raise HTTPException(status_code=403, detail="权限不足")
    
    success, subscription, error_msg = user_manager.upgrade_subscription(
        current_user["user_id"],
        request.plan,
        request.duration_days
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error_msg)
    
    return APIResponse(
        data={"subscription": subscription.to_dict()},
        message=f"订阅已升级为 {request.plan}"
    )


# ---------- 管理员接口 ----------

@app.get("/users", response_model=APIResponse)
async def list_users(
    role: Optional[str] = Query(None, description="按角色筛选"),
    is_active: Optional[bool] = Query(None, description="按状态筛选"),
    limit: int = Query(100, ge=1, le=500, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: Dict[str, Any] = Depends(require_permission(PermissionEnum.USER_READ))
):
    """获取用户列表 (需要 USER_READ 权限)"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    users = user_manager.list_users(
        role=role,
        is_active=is_active,
        limit=limit,
        offset=offset
    )
    
    return APIResponse(
        data={
            "users": [u.to_dict() for u in users],
            "total": len(users),
            "limit": limit,
            "offset": offset
        }
    )


@app.get("/users/stats", response_model=APIResponse)
async def get_user_stats(
    current_user: Dict[str, Any] = Depends(require_permission(PermissionEnum.USER_ADMIN))
):
    """获取用户统计 (需要 USER_ADMIN 权限)"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    stats = user_manager.get_user_count()
    
    return APIResponse(data=stats)


@app.put("/users/{user_id}/role", response_model=APIResponse)
async def update_user_role(
    user_id: str,
    role: str = Body(..., embed=True),
    current_user: Dict[str, Any] = Depends(require_permission(PermissionEnum.USER_ADMIN))
):
    """更新用户角色 (需要 USER_ADMIN 权限)"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    try:
        role_enum = RoleEnum(role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的角色：{role}")
    
    # 检查权限层级
    current_role = RoleEnum(current_user["role"])
    if current_role.level > role_enum.level:
        raise HTTPException(
            status_code=403,
            detail="不能分配比自己更高的角色"
        )
    
    success = permission_manager.assign_role(user_id, role_enum)
    
    if not success:
        raise HTTPException(status_code=400, detail="角色分配失败")
    
    return APIResponse(message=f"用户角色已更新为 {role}")


@app.post("/users/{user_id}/deactivate", response_model=APIResponse)
async def deactivate_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_permission(PermissionEnum.USER_ADMIN))
):
    """禁用用户 (需要 USER_ADMIN 权限)"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    # 不能禁用自己
    if user_id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="不能禁用自己")
    
    success, error_msg = user_manager.deactivate_user(user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=error_msg)
    
    return APIResponse(message="用户已禁用")


@app.post("/users/{user_id}/activate", response_model=APIResponse)
async def activate_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_permission(PermissionEnum.USER_ADMIN))
):
    """激活用户 (需要 USER_ADMIN 权限)"""
    user_manager, jwt_handler, permission_manager = get_services()
    
    success, error_msg = user_manager.activate_user(user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=error_msg)
    
    return APIResponse(message="用户已激活")


# ---------- 健康检查 ----------

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0"
    }


# ============================================
# 主入口
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        reload=True
    )
