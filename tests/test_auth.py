#!/usr/bin/env python3
"""
用户认证系统测试 - Auth System Tests
测试用户管理、JWT 认证、权限控制等功能

测试覆盖:
- 用户注册/登录
- 密码哈希与验证
- JWT Token 生成与验证
- 权限检查
- 订阅管理

运行方式:
python -m pytest tests/test_auth.py -v
"""

import os
import sys
import pytest
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auth.user_manager import UserManager, User, UserConfig, Subscription
from core.auth.jwt_handler import JWTHandler, TokenPair
from core.auth.permissions import (
    PermissionManager,
    RoleEnum,
    PermissionEnum,
    PermissionError,
)


# ============================================
# 测试夹具
# ============================================

@pytest.fixture
def user_manager():
    """创建 UserManager 实例"""
    return UserManager()


@pytest.fixture
def jwt_handler():
    """创建 JWTHandler 实例"""
    return JWTHandler(secret_key="test_secret_key_for_testing_only")


@pytest.fixture
def permission_manager():
    """创建 PermissionManager 实例"""
    return PermissionManager()


@pytest.fixture
def registered_user(user_manager):
    """创建一个已注册的用户"""
    success, user, error = user_manager.register(
        username="testuser",
        email="test@example.com",
        password="Test1234!"
    )
    assert success
    return user


# ============================================
# 用户管理器测试
# ============================================

class TestUserManager:
    """UserManager 测试类"""
    
    def test_init_default_admin(self, user_manager):
        """测试初始化时创建默认管理员"""
        admin = user_manager.get_user_by_username("admin")
        assert admin is not None
        assert admin.role == "admin"
        assert admin.is_active is True
    
    def test_register_success(self, user_manager):
        """测试成功注册"""
        success, user, error = user_manager.register(
            username="newuser",
            email="new@example.com",
            password="SecurePass123!"
        )
        
        assert success is True
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.role == "user"
        assert user.is_active is True
        assert error == ""
    
    def test_register_duplicate_username(self, user_manager, registered_user):
        """测试重复用户名注册失败"""
        success, user, error = user_manager.register(
            username="testuser",
            email="another@example.com",
            password="SecurePass123!"
        )
        
        assert success is False
        assert user is None
        assert "用户名已存在" in error
    
    def test_register_duplicate_email(self, user_manager, registered_user):
        """测试重复邮箱注册失败"""
        success, user, error = user_manager.register(
            username="anotheruser",
            email="test@example.com",
            password="SecurePass123!"
        )
        
        assert success is False
        assert user is None
        assert "邮箱已被注册" in error
    
    def test_register_weak_password(self, user_manager):
        """测试弱密码注册失败"""
        weak_passwords = [
            "123456",  # 太短
            "abcdefgh",  # 无大写
            "ABCDEFGH",  # 无小写
            "Abcdefgh",  # 无数字
            "Abc12345",  # 无特殊字符
        ]
        
        for password in weak_passwords:
            success, user, error = user_manager.register(
                username=f"user_{password}",
                email=f"{password}@example.com",
                password=password
            )
            
            assert success is False
            assert user is None
    
    def test_login_success(self, user_manager, registered_user):
        """测试成功登录"""
        success, user, error = user_manager.login(
            username="testuser",
            password="Test1234!"
        )
        
        assert success is True
        assert user is not None
        assert user.username == "testuser"
        assert error == ""
    
    def test_login_wrong_password(self, user_manager, registered_user):
        """测试错误密码登录失败"""
        success, user, error = user_manager.login(
            username="testuser",
            password="WrongPassword123!"
        )
        
        assert success is False
        assert user is None
        assert "密码错误" in error
    
    def test_login_nonexistent_user(self, user_manager):
        """测试不存在的用户登录失败"""
        success, user, error = user_manager.login(
            username="nonexistent",
            password="Password123!"
        )
        
        assert success is False
        assert user is None
        assert "用户不存在" in error
    
    def test_login_inactive_user(self, user_manager, registered_user):
        """测试被禁用用户登录失败"""
        # 禁用用户
        user_manager.deactivate_user(registered_user.id)
        
        # 尝试登录
        success, user, error = user_manager.login(
            username="testuser",
            password="Test1234!"
        )
        
        assert success is False
        assert user is None
        assert "账户已被禁用" in error
    
    def test_change_password_success(self, user_manager, registered_user):
        """测试成功修改密码"""
        success, error = user_manager.change_password(
            user_id=registered_user.id,
            old_password="Test1234!",
            new_password="NewSecure456!"
        )
        
        assert success is True
        assert error == ""
        
        # 验证新密码可以登录
        success, user, error = user_manager.login(
            username="testuser",
            password="NewSecure456!"
        )
        
        assert success is True
    
    def test_change_password_wrong_old(self, user_manager, registered_user):
        """测试旧密码错误时修改失败"""
        success, error = user_manager.change_password(
            user_id=registered_user.id,
            old_password="WrongOldPass!",
            new_password="NewSecure456!"
        )
        
        assert success is False
        assert "旧密码错误" in error
    
    def test_get_user_config(self, user_manager, registered_user):
        """测试获取用户配置"""
        config = user_manager.get_user_config(registered_user.id)
        
        assert config is not None
        assert config.user_id == registered_user.id
        assert config.theme == "light"
        assert config.language == "zh-CN"
    
    def test_update_user_config(self, user_manager, registered_user):
        """测试更新用户配置"""
        success, config, error = user_manager.update_user_config(
            registered_user.id,
            theme="dark",
            language="en-US",
            timezone="America/New_York"
        )
        
        assert success is True
        assert config.theme == "dark"
        assert config.language == "en-US"
        assert config.timezone == "America/New_York"
    
    def test_subscription_upgrade(self, user_manager, registered_user):
        """测试订阅升级"""
        success, subscription, error = user_manager.upgrade_subscription(
            registered_user.id,
            plan="pro",
            duration_days=90
        )
        
        assert success is True
        assert subscription.plan == "pro"
        assert subscription.status == "active"
        assert "ai_writing" in subscription.features
    
    def test_check_subscription_status_active(self, user_manager, registered_user):
        """测试检查活跃订阅状态"""
        # 先升级订阅
        user_manager.upgrade_subscription(registered_user.id, plan="pro", duration_days=30)
        
        is_valid, error = user_manager.check_subscription_status(registered_user.id)
        
        assert is_valid is True
    
    def test_user_to_dict_no_password(self, user_manager, registered_user):
        """测试用户转字典不包含密码"""
        user_dict = registered_user.to_dict()
        
        assert "password_hash" not in user_dict
        assert "id" in user_dict
        assert "username" in user_dict
        assert "email" in user_dict


# ============================================
# JWT 处理器测试
# ============================================

class TestJWTHandler:
    """JWTHandler 测试类"""
    
    def test_create_access_token(self, jwt_handler):
        """测试生成 Access Token"""
        token = jwt_handler.create_access_token(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        assert token is not None
        assert len(token) > 0
    
    def test_create_refresh_token(self, jwt_handler):
        """测试生成 Refresh Token"""
        token = jwt_handler.create_refresh_token(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        assert token is not None
        assert len(token) > 0
    
    def test_create_token_pair(self, jwt_handler):
        """测试生成 Token 对"""
        token_pair = jwt_handler.create_token_pair(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        assert isinstance(token_pair, TokenPair)
        assert token_pair.access_token is not None
        assert token_pair.refresh_token is not None
        assert token_pair.token_type == "Bearer"
        assert token_pair.expires_in == 3600
    
    def test_verify_access_token_success(self, jwt_handler):
        """测试验证 Access Token 成功"""
        token = jwt_handler.create_access_token(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        payload = jwt_handler.verify_access_token(token)
        
        assert payload is not None
        assert payload.user_id == "user_123"
        assert payload.username == "testuser"
        assert payload.email == "test@example.com"
        assert payload.role == "user"
    
    def test_verify_refresh_token_success(self, jwt_handler):
        """测试验证 Refresh Token 成功"""
        token = jwt_handler.create_refresh_token(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        payload = jwt_handler.verify_refresh_token(token)
        
        assert payload is not None
        assert payload.user_id == "user_123"
    
    def test_verify_token_wrong_type(self, jwt_handler):
        """测试验证 Token 类型错误"""
        access_token = jwt_handler.create_access_token(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        # 用验证 refresh token 的方法验证 access token
        payload = jwt_handler.verify_refresh_token(access_token)
        
        assert payload is None
    
    def test_verify_invalid_token(self, jwt_handler):
        """测试验证无效 Token"""
        payload = jwt_handler.verify_access_token("invalid.token.here")
        
        assert payload is None
    
    def test_verify_tampered_token(self, jwt_handler):
        """测试验证被篡改的 Token"""
        token = jwt_handler.create_access_token(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        # 篡改 Token
        parts = token.split(".")
        tampered_token = parts[0] + "." + "tampered" + "." + parts[2]
        
        payload = jwt_handler.verify_access_token(tampered_token)
        
        assert payload is None
    
    def test_refresh_access_token(self, jwt_handler):
        """测试刷新 Access Token"""
        # 生成 Token 对
        token_pair = jwt_handler.create_token_pair(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        # 刷新 Token
        new_token_pair = jwt_handler.refresh_access_token(token_pair.refresh_token)
        
        assert new_token_pair is not None
        assert new_token_pair.access_token != token_pair.access_token
        assert new_token_pair.refresh_token != token_pair.refresh_token
    
    def test_revoke_token(self, jwt_handler):
        """测试撤销 Token"""
        token = jwt_handler.create_access_token(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        # 验证 Token 有效
        payload = jwt_handler.verify_access_token(token)
        assert payload is not None
        
        # 撤销 Token
        success = jwt_handler.revoke_token(token)
        assert success is True
        
        # 验证 Token 已失效
        payload = jwt_handler.verify_access_token(token)
        assert payload is None
    
    def test_token_expiration(self, jwt_handler):
        """测试 Token 过期"""
        # 生成一个立即过期的 Token
        token = jwt_handler.create_access_token(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            role="user",
            expires_delta=timedelta(seconds=-1)
        )
        
        # 验证已过期
        is_expired = jwt_handler.is_token_expired(token)
        assert is_expired is True
        
        payload = jwt_handler.verify_access_token(token)
        assert payload is None


# ============================================
# 权限管理器测试
# ============================================

class TestPermissionManager:
    """PermissionManager 测试类"""
    
    def test_init_system_roles(self, permission_manager):
        """测试初始化系统角色"""
        roles = permission_manager.get_all_roles()
        
        assert len(roles) == 5  # admin, operator, editor, writer, viewer
        
        role_names = [r.role.value for r in roles]
        assert "admin" in role_names
        assert "viewer" in role_names
    
    def test_role_permissions(self, permission_manager):
        """测试角色权限"""
        # Admin 应该有所有权限
        admin_perms = permission_manager.get_role_permissions(RoleEnum.ADMIN)
        assert len(admin_perms) > 0
        
        # Viewer 权限较少
        viewer_perms = permission_manager.get_role_permissions(RoleEnum.VIEWER)
        assert len(viewer_perms) < len(admin_perms)
    
    def test_has_permission_admin(self, permission_manager):
        """测试 Admin 拥有所有权限"""
        for perm in PermissionEnum:
            assert permission_manager.has_permission(RoleEnum.ADMIN, perm) is True
    
    def test_has_permission_viewer(self, permission_manager):
        """测试 Viewer 只有只读权限"""
        # Viewer 应该有读取权限
        assert permission_manager.has_permission(RoleEnum.VIEWER, PermissionEnum.USER_READ) is True
        assert permission_manager.has_permission(RoleEnum.VIEWER, PermissionEnum.HOTNEWS_READ) is True
        
        # Viewer 不应该有写入权限
        assert permission_manager.has_permission(RoleEnum.VIEWER, PermissionEnum.USER_WRITE) is False
        assert permission_manager.has_permission(RoleEnum.VIEWER, PermissionEnum.ARTICLE_WRITE) is False
    
    def test_role_level(self, permission_manager):
        """测试角色层级"""
        assert RoleEnum.ADMIN.level == 1
        assert RoleEnum.OPERATOR.level == 2
        assert RoleEnum.EDITOR.level == 3
        assert RoleEnum.WRITER.level == 4
        assert RoleEnum.VIEWER.level == 5
    
    def test_role_access_check(self, permission_manager):
        """测试角色访问检查"""
        # Admin 可以访问所有角色
        assert RoleEnum.ADMIN.can_access_role(RoleEnum.VIEWER) is True
        assert RoleEnum.ADMIN.can_access_role(RoleEnum.OPERATOR) is True
        
        # Viewer 不能访问更高权限角色
        assert RoleEnum.VIEWER.can_access_role(RoleEnum.ADMIN) is False
        assert RoleEnum.VIEWER.can_access_role(RoleEnum.OPERATOR) is False
    
    def test_assign_user_role(self, permission_manager):
        """测试分配用户角色"""
        success = permission_manager.assign_role("user_123", RoleEnum.WRITER)
        
        assert success is True
        assert permission_manager.get_user_role("user_123") == RoleEnum.WRITER
    
    def test_check_user_permission(self, permission_manager):
        """测试检查用户权限"""
        # 分配角色
        permission_manager.assign_role("user_123", RoleEnum.WRITER)
        
        # 检查权限
        result = permission_manager.check_user_permission(
            "user_123",
            PermissionEnum.ARTICLE_WRITE
        )
        
        assert result.allowed is True
        assert result.permission == PermissionEnum.ARTICLE_WRITE
        
        # 检查没有的权限
        result = permission_manager.check_user_permission(
            "user_123",
            PermissionEnum.USER_ADMIN
        )
        
        assert result.allowed is False
    
    def test_get_user_permissions(self, permission_manager):
        """测试获取用户所有权限"""
        permission_manager.assign_role("user_123", RoleEnum.EDITOR)
        
        permissions = permission_manager.get_user_permissions("user_123")
        
        assert len(permissions) > 0
        assert PermissionEnum.ARTICLE_PUBLISH in permissions
    
    def test_require_permission_decorator(self, permission_manager):
        """测试权限装饰器"""
        @permission_manager.require_permission(PermissionEnum.USER_ADMIN)
        def admin_action(user_id):
            return "Admin action performed"
        
        # 分配 Admin 角色
        permission_manager.assign_role("admin_user", RoleEnum.ADMIN)
        
        # Admin 可以执行
        result = admin_action("admin_user")
        assert result == "Admin action performed"
        
        # 分配 Viewer 角色
        permission_manager.assign_role("viewer_user", RoleEnum.VIEWER)
        
        # Viewer 不能执行
        with pytest.raises(PermissionError):
            admin_action("viewer_user")
    
    def test_require_role_decorator(self, permission_manager):
        """测试角色装饰器"""
        @permission_manager.require_role(RoleEnum.ADMIN, RoleEnum.OPERATOR)
        def admin_operation(user_id):
            return "Admin operation"
        
        # Admin 可以执行
        permission_manager.assign_role("admin_user", RoleEnum.ADMIN)
        result = admin_operation("admin_user")
        assert result == "Admin operation"
        
        # Viewer 不能执行
        permission_manager.assign_role("viewer_user", RoleEnum.VIEWER)
        with pytest.raises(PermissionError):
            admin_operation("viewer_user")
    
    def test_require_min_role_decorator(self, permission_manager):
        """测试最低角色要求装饰器"""
        @permission_manager.require_min_role(RoleEnum.EDITOR)
        def editor_action(user_id):
            return "Editor action"
        
        # Editor 可以执行
        permission_manager.assign_role("editor_user", RoleEnum.EDITOR)
        result = editor_action("editor_user")
        assert result == "Editor action"
        
        # Admin 也可以执行 (更高级别)
        permission_manager.assign_role("admin_user", RoleEnum.ADMIN)
        result = editor_action("admin_user")
        assert result == "Editor action"
        
        # Writer 不能执行 (更低级别)
        permission_manager.assign_role("writer_user", RoleEnum.WRITER)
        with pytest.raises(PermissionError):
            editor_action("writer_user")
    
    def test_can_access_resource(self, permission_manager):
        """测试资源访问控制"""
        permission_manager.assign_role("user_123", RoleEnum.WRITER)
        
        # Writer 可以读取文章
        result = permission_manager.can_access_resource(
            "user_123",
            "article",
            "article_001",
            "read"
        )
        assert result.allowed is True
        
        # Writer 不能删除文章
        result = permission_manager.can_access_resource(
            "user_123",
            "article",
            "article_001",
            "delete"
        )
        assert result.allowed is False
    
    def test_user_without_role(self, permission_manager):
        """测试未分配角色的用户"""
        result = permission_manager.check_user_permission(
            "unknown_user",
            PermissionEnum.USER_READ
        )
        
        assert result.allowed is False
        assert "未分配角色" in result.reason


# ============================================
# 集成测试
# ============================================

class TestIntegration:
    """集成测试"""
    
    def test_full_auth_flow(self, user_manager, jwt_handler, permission_manager):
        """测试完整的认证流程"""
        # 1. 注册
        success, user, error = user_manager.register(
            username="integration_test",
            email="integration@test.com",
            password="Integration123!"
        )
        assert success is True
        
        # 2. 分配角色
        permission_manager.assign_role(user.id, RoleEnum.EDITOR)
        
        # 3. 登录
        success, user, error = user_manager.login(
            username="integration_test",
            password="Integration123!"
        )
        assert success is True
        
        # 4. 生成 Token
        token_pair = jwt_handler.create_token_pair(
            user_id=user.id,
            username=user.username,
            email=user.email,
            role=user.role
        )
        
        # 5. 验证 Token
        payload = jwt_handler.verify_access_token(token_pair.access_token)
        assert payload is not None
        assert payload.user_id == user.id
        
        # 6. 检查权限
        result = permission_manager.check_user_permission(
            user.id,
            PermissionEnum.ARTICLE_PUBLISH
        )
        assert result.allowed is True
    
    def test_subscription_features(self, user_manager, registered_user):
        """测试订阅功能"""
        # 免费订阅
        sub = user_manager.get_subscription(registered_user.id)
        assert sub.plan == "free"
        assert "basic_writing" in sub.features
        
        # 升级到 Pro
        success, sub, error = user_manager.upgrade_subscription(
            registered_user.id,
            plan="pro",
            duration_days=30
        )
        assert success is True
        assert sub.plan == "pro"
        assert "ai_writing" in sub.features
        assert "advanced_analytics" in sub.features
        
        # 检查订阅状态
        is_valid, error = user_manager.check_subscription_status(registered_user.id)
        assert is_valid is True


# ============================================
# 运行测试
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
