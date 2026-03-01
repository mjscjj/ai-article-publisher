#!/usr/bin/env python3
"""
用户管理器 - User Manager
负责用户注册、登录、密码验证、用户信息管理

功能:
- 用户注册 (密码哈希存储)
- 用户登录验证
- 密码重置
- 用户信息管理
- 用户状态管理 (激活/禁用)

安全特性:
- bcrypt 密码哈希 (cost factor=12)
- 密码强度验证
- 防止重名注册
- 敏感信息隔离
"""

import os
import re
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import bcrypt


# ============================================
# 数据模型
# ============================================

@dataclass
class User:
    """用户数据模型"""
    id: str
    username: str
    email: str
    password_hash: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    profile: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 (不包含密码)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "profile": self.profile or {},
        }


@dataclass
class UserConfig:
    """用户配置模型"""
    user_id: str
    theme: str = "light"
    language: str = "zh-CN"
    timezone: str = "Asia/Shanghai"
    notifications_enabled: bool = True
    auto_save: bool = True
    editor_mode: str = "markdown"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Subscription:
    """订阅模型"""
    user_id: str
    plan: str  # free, basic, pro, enterprise
    status: str  # active, expired, cancelled
    start_date: datetime
    end_date: datetime
    features: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "plan": self.plan,
            "status": self.status,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "features": self.features,
        }


# ============================================
# 用户管理器
# ============================================

class UserManager:
    """
    用户管理器
    
    使用内存存储 (生产环境应替换为数据库)
    提供用户 CRUD 操作和认证功能
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        初始化用户管理器
        
        Args:
            db_url: 数据库连接 URL (可选，默认使用内存存储)
        """
        # 内存存储 (生产环境使用 MySQL/PostgreSQL)
        self._users: Dict[str, User] = {}
        self._user_configs: Dict[str, UserConfig] = {}
        self._subscriptions: Dict[str, Subscription] = {}
        
        # 用户名/邮箱索引
        self._username_index: Dict[str, str] = {}
        self._email_index: Dict[str, str] = {}
        
        # 密码哈希配置
        self._bcrypt_cost = 12
        
        # 初始化默认管理员账户
        self._init_default_admin()
    
    def _init_default_admin(self):
        """初始化默认管理员账户"""
        admin_id = "admin_001"
        if admin_id not in self._users:
            admin_user = User(
                id=admin_id,
                username="admin",
                email="admin@youmind.com",
                password_hash=self._hash_password("admin123"),
                role="admin",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            self._users[admin_id] = admin_user
            self._username_index["admin"] = admin_id
            self._email_index["admin@youmind.com"] = admin_id
    
    # ========================================
    # 密码管理
    # ========================================
    
    def _hash_password(self, password: str) -> str:
        """
        哈希密码 (bcrypt)
        
        Args:
            password: 明文密码
            
        Returns:
            bcrypt 哈希字符串
        """
        salt = bcrypt.gensalt(rounds=self._bcrypt_cost)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            password_hash: bcrypt 哈希
            
        Returns:
            bool: 密码是否匹配
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        验证密码强度
        
        要求:
        - 至少 8 个字符
        - 包含大小写字母
        - 包含数字
        - 包含特殊字符
        
        Args:
            password: 待验证密码
            
        Returns:
            (是否有效, 错误信息)
        """
        if len(password) < 8:
            return False, "密码长度至少 8 位"
        
        if not re.search(r'[A-Z]', password):
            return False, "密码必须包含大写字母"
        
        if not re.search(r'[a-z]', password):
            return False, "密码必须包含小写字母"
        
        if not re.search(r'\d', password):
            return False, "密码必须包含数字"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "密码必须包含特殊字符 (!@#$%^&*...)"
        
        return True, ""
    
    # ========================================
    # 用户注册/登录
    # ========================================
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "user"
    ) -> tuple[bool, Optional[User], str]:
        """
        用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            role: 角色 (默认 user)
            
        Returns:
            (成功标志, 用户对象, 错误信息)
        """
        # 验证密码强度
        is_valid, error_msg = self.validate_password_strength(password)
        if not is_valid:
            return False, None, error_msg
        
        # 检查用户名是否已存在
        if username in self._username_index:
            return False, None, "用户名已存在"
        
        # 检查邮箱是否已存在
        if email in self._email_index:
            return False, None, "邮箱已被注册"
        
        # 生成用户 ID
        user_id = f"user_{secrets.token_hex(8)}"
        
        # 创建用户
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=self._hash_password(password),
            role=role,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        # 存储用户
        self._users[user_id] = user
        self._username_index[username] = user_id
        self._email_index[email] = user_id
        
        # 初始化用户配置
        self._user_configs[user_id] = UserConfig(user_id=user_id)
        
        # 初始化免费订阅 (永久有效)
        self._subscriptions[user_id] = Subscription(
            user_id=user_id,
            plan="free",
            status="active",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=365 * 10),  # 10 年有效
            features=["basic_writing", "daily_hotnews"],
        )
        
        return True, user, ""
    
    def login(self, username: str, password: str) -> tuple[bool, Optional[User], str]:
        """
        用户登录
        
        Args:
            username: 用户名或邮箱
            password: 密码
            
        Returns:
            (成功标志, 用户对象, 错误信息)
        """
        # 查找用户
        user_id = self._username_index.get(username) or self._email_index.get(username)
        
        if not user_id:
            return False, None, "用户不存在"
        
        user = self._users.get(user_id)
        if not user:
            return False, None, "用户不存在"
        
        # 检查账户状态
        if not user.is_active:
            return False, None, "账户已被禁用"
        
        # 验证密码
        if not self._verify_password(password, user.password_hash):
            return False, None, "密码错误"
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        user.updated_at = datetime.now()
        
        return True, user, ""
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户信息"""
        return self._users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        user_id = self._username_index.get(username)
        return self._users.get(user_id) if user_id else None
    
    def update_user(self, user_id: str, **kwargs) -> tuple[bool, Optional[User], str]:
        """
        更新用户信息
        
        Args:
            user_id: 用户 ID
            **kwargs: 要更新的字段
            
        Returns:
            (成功标志, 用户对象, 错误信息)
        """
        user = self._users.get(user_id)
        if not user:
            return False, None, "用户不存在"
        
        # 不允许直接修改密码和 ID
        forbidden_fields = {"id", "password_hash", "created_at"}
        for field in forbidden_fields:
            kwargs.pop(field, None)
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.now()
        
        return True, user, ""
    
    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> tuple[bool, str]:
        """
        修改密码
        
        Args:
            user_id: 用户 ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            (成功标志, 错误信息)
        """
        user = self._users.get(user_id)
        if not user:
            return False, "用户不存在"
        
        # 验证旧密码
        if not self._verify_password(old_password, user.password_hash):
            return False, "旧密码错误"
        
        # 验证新密码强度
        is_valid, error_msg = self.validate_password_strength(new_password)
        if not is_valid:
            return False, error_msg
        
        # 更新密码
        user.password_hash = self._hash_password(new_password)
        user.updated_at = datetime.now()
        
        return True, ""
    
    def deactivate_user(self, user_id: str) -> tuple[bool, str]:
        """禁用用户"""
        user = self._users.get(user_id)
        if not user:
            return False, "用户不存在"
        
        user.is_active = False
        user.updated_at = datetime.now()
        
        return True, ""
    
    def activate_user(self, user_id: str) -> tuple[bool, str]:
        """激活用户"""
        user = self._users.get(user_id)
        if not user:
            return False, "用户不存在"
        
        user.is_active = True
        user.updated_at = datetime.now()
        
        return True, ""
    
    # ========================================
    # 用户配置管理
    # ========================================
    
    def get_user_config(self, user_id: str) -> Optional[UserConfig]:
        """获取用户配置"""
        return self._user_configs.get(user_id)
    
    def update_user_config(
        self,
        user_id: str,
        **kwargs
    ) -> tuple[bool, Optional[UserConfig], str]:
        """
        更新用户配置
        
        Args:
            user_id: 用户 ID
            **kwargs: 配置项
            
        Returns:
            (成功标志, 配置对象, 错误信息)
        """
        config = self._user_configs.get(user_id)
        if not config:
            return False, None, "用户配置不存在"
        
        # 更新配置
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return True, config, ""
    
    # ========================================
    # 订阅管理
    # ========================================
    
    def get_subscription(self, user_id: str) -> Optional[Subscription]:
        """获取用户订阅"""
        return self._subscriptions.get(user_id)
    
    def upgrade_subscription(
        self,
        user_id: str,
        plan: str,
        duration_days: int = 30
    ) -> tuple[bool, Optional[Subscription], str]:
        """
        升级订阅
        
        Args:
            user_id: 用户 ID
            plan: 订阅计划 (basic/pro/enterprise)
            duration_days: 订阅天数
            
        Returns:
            (成功标志, 订阅对象, 错误信息)
        """
        subscription = self._subscriptions.get(user_id)
        if not subscription:
            return False, None, "用户订阅不存在"
        
        # 定义订阅计划特性
        plan_features = {
            "basic": ["basic_writing", "daily_hotnews", "weekly_topics"],
            "pro": ["basic_writing", "daily_hotnews", "weekly_topics", 
                   "ai_writing", "advanced_analytics", "priority_support"],
            "enterprise": ["basic_writing", "daily_hotnews", "weekly_topics",
                          "ai_writing", "advanced_analytics", "priority_support",
                          "custom_models", "api_access", "team_collaboration"],
        }
        
        features = plan_features.get(plan, [])
        if not features:
            return False, None, f"无效的订阅计划：{plan}"
        
        # 更新订阅
        subscription.plan = plan
        subscription.status = "active"
        subscription.end_date = datetime.now() + timedelta(days=duration_days)
        subscription.features = features
        
        return True, subscription, ""
    
    def cancel_subscription(self, user_id: str) -> tuple[bool, str]:
        """取消订阅"""
        subscription = self._subscriptions.get(user_id)
        if not subscription:
            return False, "用户订阅不存在"
        
        subscription.status = "cancelled"
        
        return True, ""
    
    def check_subscription_status(self, user_id: str) -> tuple[bool, str]:
        """
        检查订阅状态
        
        Returns:
            (是否有效, 错误信息)
        """
        subscription = self._subscriptions.get(user_id)
        if not subscription:
            return False, "订阅不存在"
        
        if subscription.status != "active":
            return False, f"订阅状态：{subscription.status}"
        
        if subscription.end_date < datetime.now():
            subscription.status = "expired"
            return False, "订阅已过期"
        
        return True, ""
    
    # ========================================
    # 用户列表与统计
    # ========================================
    
    def list_users(
        self,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[User]:
        """
        获取用户列表
        
        Args:
            role: 按角色筛选
            is_active: 按状态筛选
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            用户列表
        """
        users = list(self._users.values())
        
        # 筛选
        if role is not None:
            users = [u for u in users if u.role == role]
        
        if is_active is not None:
            users = [u for u in users if u.is_active == is_active]
        
        # 分页
        return users[offset:offset + limit]
    
    def get_user_count(self) -> Dict[str, int]:
        """获取用户统计"""
        total = len(self._users)
        active = sum(1 for u in self._users.values() if u.is_active)
        by_role = {}
        
        for user in self._users.values():
            by_role[user.role] = by_role.get(user.role, 0) + 1
        
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "by_role": by_role,
        }


# ============================================
# 单例
# ============================================

_user_manager_instance: Optional[UserManager] = None


def get_user_manager(db_url: Optional[str] = None) -> UserManager:
    """获取 UserManager 单例"""
    global _user_manager_instance
    if _user_manager_instance is None:
        _user_manager_instance = UserManager(db_url)
    return _user_manager_instance
