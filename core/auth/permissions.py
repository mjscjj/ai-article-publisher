#!/usr/bin/env python3
"""
权限管理器 - Permission Manager
负责角色定义、权限控制、资源访问授权

功能:
- 角色定义 (RBAC 模型)
- 权限点管理
- 角色 - 权限映射
- 用户权限检查
- 资源访问控制

权限模型:
- 基于角色的访问控制 (RBAC)
- 权限点粒度控制
- 支持权限继承
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


# ============================================
# 角色枚举
# ============================================

class RoleEnum(str, Enum):
    """系统角色定义"""
    
    ADMIN = "admin"              # 超级管理员
    OPERATOR = "operator"        # 运营人员
    EDITOR = "editor"            # 编辑
    WRITER = "writer"            # 写作者
    VIEWER = "viewer"            # 访客/只读用户
    
    # 角色层级 (数字越小权限越高)
    @property
    def level(self) -> int:
        levels = {
            self.ADMIN: 1,
            self.OPERATOR: 2,
            self.EDITOR: 3,
            self.WRITER: 4,
            self.VIEWER: 5,
        }
        return levels.get(self, 99)
    
    def can_access_role(self, target_role: "RoleEnum") -> bool:
        """判断是否可以访问目标角色的资源"""
        return self.level <= target_role.level


# ============================================
# 权限枚举
# ============================================

class PermissionEnum(str, Enum):
    """
    系统权限点定义
    
    命名规范：{模块}:{操作}:{资源}
    例如：user:read, user:write, article:delete
    """
    
    # ========== 用户管理 ==========
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_ADMIN = "user:admin"  # 用户管理全部权限
    
    # ========== 热点管理 ==========
    HOTNEWS_READ = "hotnews:read"
    HOTNEWS_WRITE = "hotnews:write"
    HOTNEWS_DELETE = "hotnews:delete"
    HOTNEWS_ADMIN = "hotnews:admin"
    
    # ========== 选题管理 ==========
    TOPIC_READ = "topic:read"
    TOPIC_WRITE = "topic:write"
    TOPIC_DELETE = "topic:delete"
    TOPIC_SCORE = "topic:score"  # 评分权限
    TOPIC_ADMIN = "topic:admin"
    
    # ========== 文章管理 ==========
    ARTICLE_READ = "article:read"
    ARTICLE_WRITE = "article:write"
    ARTICLE_DELETE = "article:delete"
    ARTICLE_PUBLISH = "article:publish"  # 发布权限
    ARTICLE_ADMIN = "article:admin"
    
    # ========== 写作工厂 ==========
    WRITING_READ = "writing:read"
    WRITING_GENERATE = "writing:generate"  # 生成文章
    WRITING_EDIT = "writing:edit"
    WRITING_ADMIN = "writing:admin"
    
    # ========== 系统管理 ==========
    SYSTEM_READ = "system:read"
    SYSTEM_CONFIG = "system:config"  # 配置修改
    SYSTEM_ADMIN = "system:admin"
    
    # ========== 订阅管理 ==========
    SUBSCRIPTION_READ = "subscription:read"
    SUBSCRIPTION_WRITE = "subscription:write"
    SUBSCRIPTION_ADMIN = "subscription:admin"
    
    # ========== 数据分析 ==========
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_ADMIN = "analytics:admin"


# ============================================
# 数据模型
# ============================================

@dataclass
class RoleDefinition:
    """角色定义"""
    role: RoleEnum
    name: str
    description: str
    permissions: Set[PermissionEnum] = field(default_factory=set)
    inherit_from: Optional[RoleEnum] = None  # 继承的角色


@dataclass
class PermissionCheckResult:
    """权限检查结果"""
    allowed: bool
    permission: PermissionEnum
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================
# 权限管理器
# ============================================

class PermissionManager:
    """
    权限管理器
    
    实现 RBAC (Role-Based Access Control) 模型:
    - 用户 -> 角色 -> 权限
    - 支持角色继承
    - 支持权限点粒度控制
    """
    
    def __init__(self):
        """初始化权限管理器"""
        # 角色定义
        self._roles: Dict[RoleEnum, RoleDefinition] = {}
        
        # 用户 - 角色映射 (生产环境应从数据库加载)
        self._user_roles: Dict[str, RoleEnum] = {}
        
        # 初始化系统角色
        self._init_system_roles()
    
    def _init_system_roles(self):
        """初始化系统角色和权限"""
        
        # VIEWER: 只读用户
        self._roles[RoleEnum.VIEWER] = RoleDefinition(
            role=RoleEnum.VIEWER,
            name="访客",
            description="只读权限，可浏览公开内容",
            permissions={
                PermissionEnum.USER_READ,
                PermissionEnum.HOTNEWS_READ,
                PermissionEnum.TOPIC_READ,
                PermissionEnum.ARTICLE_READ,
                PermissionEnum.SYSTEM_READ,
                PermissionEnum.ANALYTICS_READ,
                PermissionEnum.SUBSCRIPTION_READ,
            }
        )
        
        # WRITER: 写作者
        self._roles[RoleEnum.WRITER] = RoleDefinition(
            role=RoleEnum.WRITER,
            name="写作者",
            description="可创建和编辑文章",
            permissions={
                PermissionEnum.HOTNEWS_READ,
                PermissionEnum.TOPIC_READ,
                PermissionEnum.TOPIC_WRITE,
                PermissionEnum.ARTICLE_READ,
                PermissionEnum.ARTICLE_WRITE,
                PermissionEnum.WRITING_READ,
                PermissionEnum.WRITING_GENERATE,
                PermissionEnum.WRITING_EDIT,
                PermissionEnum.SUBSCRIPTION_READ,
                PermissionEnum.ANALYTICS_READ,
            },
            inherit_from=RoleEnum.VIEWER
        )
        
        # EDITOR: 编辑
        self._roles[RoleEnum.EDITOR] = RoleDefinition(
            role=RoleEnum.EDITOR,
            name="编辑",
            description="可审核和发布文章",
            permissions={
                PermissionEnum.HOTNEWS_READ,
                PermissionEnum.HOTNEWS_WRITE,
                PermissionEnum.TOPIC_READ,
                PermissionEnum.TOPIC_WRITE,
                PermissionEnum.TOPIC_SCORE,
                PermissionEnum.ARTICLE_READ,
                PermissionEnum.ARTICLE_WRITE,
                PermissionEnum.ARTICLE_PUBLISH,
                PermissionEnum.WRITING_READ,
                PermissionEnum.WRITING_GENERATE,
                PermissionEnum.WRITING_EDIT,
                PermissionEnum.SUBSCRIPTION_READ,
                PermissionEnum.ANALYTICS_READ,
                PermissionEnum.ANALYTICS_EXPORT,
            },
            inherit_from=RoleEnum.WRITER
        )
        
        # OPERATOR: 运营人员
        self._roles[RoleEnum.OPERATOR] = RoleDefinition(
            role=RoleEnum.OPERATOR,
            name="运营人员",
            description="可管理热点、选题、文章",
            permissions={
                PermissionEnum.USER_READ,
                PermissionEnum.HOTNEWS_READ,
                PermissionEnum.HOTNEWS_WRITE,
                PermissionEnum.HOTNEWS_DELETE,
                PermissionEnum.TOPIC_READ,
                PermissionEnum.TOPIC_WRITE,
                PermissionEnum.TOPIC_DELETE,
                PermissionEnum.TOPIC_SCORE,
                PermissionEnum.ARTICLE_READ,
                PermissionEnum.ARTICLE_WRITE,
                PermissionEnum.ARTICLE_DELETE,
                PermissionEnum.ARTICLE_PUBLISH,
                PermissionEnum.WRITING_READ,
                PermissionEnum.WRITING_GENERATE,
                PermissionEnum.WRITING_EDIT,
                PermissionEnum.SUBSCRIPTION_READ,
                PermissionEnum.SUBSCRIPTION_WRITE,
                PermissionEnum.ANALYTICS_READ,
                PermissionEnum.ANALYTICS_EXPORT,
            },
            inherit_from=RoleEnum.EDITOR
        )
        
        # ADMIN: 超级管理员
        self._roles[RoleEnum.ADMIN] = RoleDefinition(
            role=RoleEnum.ADMIN,
            name="超级管理员",
            description="拥有所有权限",
            permissions=set(PermissionEnum),  # 所有权限
        )
        
        # 解析角色继承
        self._resolve_role_inheritance()
    
    def _resolve_role_inheritance(self):
        """解析角色继承关系"""
        for role_def in self._roles.values():
            if role_def.inherit_from:
                parent = self._roles.get(role_def.inherit_from)
                if parent:
                    role_def.permissions.update(parent.permissions)
    
    # ========================================
    # 角色管理
    # ========================================
    
    def get_role(self, role: RoleEnum) -> Optional[RoleDefinition]:
        """获取角色定义"""
        return self._roles.get(role)
    
    def get_all_roles(self) -> List[RoleDefinition]:
        """获取所有角色"""
        return list(self._roles.values())
    
    def get_role_permissions(self, role: RoleEnum) -> Set[PermissionEnum]:
        """获取角色的所有权限"""
        role_def = self._roles.get(role)
        return role_def.permissions if role_def else set()
    
    def has_permission(self, role: RoleEnum, permission: PermissionEnum) -> bool:
        """
        检查角色是否拥有指定权限
        
        Args:
            role: 角色
            permission: 权限点
            
        Returns:
            bool: 是否拥有权限
        """
        role_def = self._roles.get(role)
        if not role_def:
            return False
        
        return permission in role_def.permissions
    
    def has_any_permission(
        self,
        role: RoleEnum,
        permissions: List[PermissionEnum]
    ) -> bool:
        """检查角色是否拥有任一权限"""
        for perm in permissions:
            if self.has_permission(role, perm):
                return True
        return False
    
    def has_all_permissions(
        self,
        role: RoleEnum,
        permissions: List[PermissionEnum]
    ) -> bool:
        """检查角色是否拥有所有权限"""
        for perm in permissions:
            if not self.has_permission(role, perm):
                return False
        return True
    
    # ========================================
    # 用户权限管理
    # ========================================
    
    def assign_role(self, user_id: str, role: RoleEnum) -> bool:
        """
        为用户分配角色
        
        Args:
            user_id: 用户 ID
            role: 角色
            
        Returns:
            bool: 是否成功
        """
        if role not in self._roles:
            return False
        
        self._user_roles[user_id] = role
        return True
    
    def get_user_role(self, user_id: str) -> Optional[RoleEnum]:
        """获取用户角色"""
        return self._user_roles.get(user_id)
    
    def remove_user_role(self, user_id: str) -> bool:
        """移除用户角色"""
        if user_id in self._user_roles:
            del self._user_roles[user_id]
            return True
        return False
    
    def check_user_permission(
        self,
        user_id: str,
        permission: PermissionEnum
    ) -> PermissionCheckResult:
        """
        检查用户权限
        
        Args:
            user_id: 用户 ID
            permission: 权限点
            
        Returns:
            PermissionCheckResult
        """
        role = self._user_roles.get(user_id)
        
        if not role:
            return PermissionCheckResult(
                allowed=False,
                permission=permission,
                reason="用户未分配角色"
            )
        
        if self.has_permission(role, permission):
            return PermissionCheckResult(
                allowed=True,
                permission=permission,
                reason=f"角色 {role.name} 拥有权限 {permission.value}"
            )
        
        return PermissionCheckResult(
            allowed=False,
            permission=permission,
            reason=f"角色 {role.name} 缺少权限 {permission.value}"
        )
    
    def get_user_permissions(self, user_id: str) -> Set[PermissionEnum]:
        """获取用户所有权限"""
        role = self._user_roles.get(user_id)
        if not role:
            return set()
        
        return self.get_role_permissions(role)
    
    # ========================================
    # 权限装饰器
    # ========================================
    
    def require_permission(self, permission: PermissionEnum):
        """
        权限检查装饰器
        
        用法:
        @permission_manager.require_permission(PermissionEnum.USER_WRITE)
        def update_user(user_id, data):
            ...
        """
        def decorator(func):
            def wrapper(user_id: str, *args, **kwargs):
                result = self.check_user_permission(user_id, permission)
                if not result.allowed:
                    raise PermissionError(
                        f"用户 {user_id} 缺少权限 {permission.value}: {result.reason}"
                    )
                return func(user_id, *args, **kwargs)
            
            wrapper.__name__ = func.__name__
            return wrapper
        return decorator
    
    def require_role(self, *roles: RoleEnum):
        """
        角色检查装饰器
        
        用法:
        @permission_manager.require_role(RoleEnum.ADMIN, RoleEnum.OPERATOR)
        def admin_operation():
            ...
        """
        def decorator(func):
            def wrapper(user_id: str, *args, **kwargs):
                user_role = self._user_roles.get(user_id)
                
                if not user_role:
                    raise PermissionError(f"用户 {user_id} 未分配角色")
                
                if user_role not in roles:
                    role_names = ", ".join([r.value for r in roles])
                    raise PermissionError(
                        f"用户 {user_id} 的角色 {user_role.value} 不在允许列表中：{role_names}"
                    )
                
                return func(user_id, *args, **kwargs)
            
            wrapper.__name__ = func.__name__
            return wrapper
        return decorator
    
    def require_min_role(self, min_role: RoleEnum):
        """
        最低角色要求装饰器
        
        用法:
        @permission_manager.require_min_role(RoleEnum.EDITOR)
        def editor_operation():
            ...
        """
        def decorator(func):
            def wrapper(user_id: str, *args, **kwargs):
                user_role = self._user_roles.get(user_id)
                
                if not user_role:
                    raise PermissionError(f"用户 {user_id} 未分配角色")
                
                if user_role.level > min_role.level:
                    raise PermissionError(
                        f"用户 {user_id} 的角色 {user_role.value} 权限不足，"
                        f"最低要求 {min_role.value}"
                    )
                
                return func(user_id, *args, **kwargs)
            
            wrapper.__name__ = func.__name__
            return wrapper
        return decorator
    
    # ========================================
    # 资源访问控制
    # ========================================
    
    def can_access_resource(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str
    ) -> PermissionCheckResult:
        """
        检查用户是否可以访问资源
        
        Args:
            user_id: 用户 ID
            resource_type: 资源类型 (user/hotnews/topic/article/...)
            resource_id: 资源 ID
            action: 操作类型 (read/write/delete/admin)
            
        Returns:
            PermissionCheckResult
        """
        # 构建权限点
        permission_str = f"{resource_type}:{action}"
        
        try:
            permission = PermissionEnum(permission_str)
        except ValueError:
            return PermissionCheckResult(
                allowed=False,
                permission=permission_str,  # type: ignore
                reason=f"未知权限点：{permission_str}"
            )
        
        return self.check_user_permission(user_id, permission)
    
    def can_read(self, user_id: str, resource_type: str) -> bool:
        """检查用户是否可以读取资源"""
        result = self.can_access_resource(user_id, resource_type, "*", "read")
        return result.allowed
    
    def can_write(self, user_id: str, resource_type: str) -> bool:
        """检查用户是否可以写入资源"""
        result = self.can_access_resource(user_id, resource_type, "*", "write")
        return result.allowed
    
    def can_delete(self, user_id: str, resource_type: str) -> bool:
        """检查用户是否可以删除资源"""
        result = self.can_access_resource(user_id, resource_type, "*", "delete")
        return result.allowed


# ============================================
# 异常类
# ============================================

class PermissionError(Exception):
    """权限错误"""
    pass


class RoleNotFoundError(Exception):
    """角色未找到错误"""
    pass


# ============================================
# 单例
# ============================================

_permission_manager_instance: Optional[PermissionManager] = None


def get_permission_manager() -> PermissionManager:
    """获取 PermissionManager 单例"""
    global _permission_manager_instance
    if _permission_manager_instance is None:
        _permission_manager_instance = PermissionManager()
    return _permission_manager_instance
