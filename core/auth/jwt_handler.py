#!/usr/bin/env python3
"""
JWT 令牌处理器 - JWT Handler
负责 JWT Token 的生成、验证、刷新

功能:
- 生成 Access Token 和 Refresh Token
- Token 验证与解析
- Token 刷新
- Token 黑名单管理

安全特性:
- HS256 签名算法
- 双 Token 机制 (Access + Refresh)
- Token 过期时间控制
- Token 黑名单支持
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Set
from dataclasses import dataclass
import jwt


# ============================================
# 数据模型
# ============================================

@dataclass
class TokenPair:
    """Token 对 (Access + Refresh)"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600  # Access Token 过期时间 (秒)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
        }


@dataclass
class TokenPayload:
    """Token 负载"""
    user_id: str
    username: str
    email: str
    role: str
    exp: datetime
    iat: datetime
    jti: str  # Token 唯一标识
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "exp": self.exp,
            "iat": self.iat,
            "jti": self.jti,
        }


# ============================================
# JWT 处理器
# ============================================

class JWTHandler:
    """
    JWT 令牌处理器
    
    实现双 Token 机制:
    - Access Token: 短期有效 (默认 1 小时), 用于 API 请求
    - Refresh Token: 长期有效 (默认 7 天), 用于刷新 Access Token
    """
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 7
    ):
        """
        初始化 JWT 处理器
        
        Args:
            secret_key: 签名密钥 (默认从环境变量读取)
            algorithm: 签名算法
            access_token_expire_minutes: Access Token 过期时间 (分钟)
            refresh_token_expire_days: Refresh Token 过期时间 (天)
        """
        # 签名密钥
        self._secret_key = secret_key or os.getenv("JWT_SECRET_KEY")
        if not self._secret_key:
            # 开发环境生成随机密钥
            self._secret_key = secrets.token_urlsafe(32)
            print(f"[WARNING] JWT_SECRET_KEY not set, using random key: {self._secret_key[:8]}...")
        
        self._algorithm = algorithm
        self._access_token_expire = timedelta(minutes=access_token_expire_minutes)
        self._refresh_token_expire = timedelta(days=refresh_token_expire_days)
        
        # Token 黑名单 (生产环境应使用 Redis)
        self._blacklist: Set[str] = set()
    
    # ========================================
    # Token 生成
    # ========================================
    
    def create_access_token(
        self,
        user_id: str,
        username: str,
        email: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        生成 Access Token
        
        Args:
            user_id: 用户 ID
            username: 用户名
            email: 邮箱
            role: 角色
            expires_delta: 自定义过期时间
            
        Returns:
            JWT Access Token
        """
        now = datetime.utcnow()
        expire = now + (expires_delta or self._access_token_expire)
        
        payload = {
            "sub": user_id,  # Subject (用户 ID)
            "username": username,
            "email": email,
            "role": role,
            "exp": expire,
            "iat": now,
            "jti": secrets.token_hex(16),  # 唯一标识
            "type": "access",
        }
        
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
    
    def create_refresh_token(
        self,
        user_id: str,
        username: str,
        email: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        生成 Refresh Token
        
        Args:
            user_id: 用户 ID
            username: 用户名
            email: 邮箱
            role: 角色
            expires_delta: 自定义过期时间
            
        Returns:
            JWT Refresh Token
        """
        now = datetime.utcnow()
        expire = now + (expires_delta or self._refresh_token_expire)
        
        payload = {
            "sub": user_id,
            "username": username,
            "email": email,
            "role": role,
            "exp": expire,
            "iat": now,
            "jti": secrets.token_hex(16),
            "type": "refresh",
        }
        
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
    
    def create_token_pair(
        self,
        user_id: str,
        username: str,
        email: str,
        role: str
    ) -> TokenPair:
        """
        生成 Token 对 (Access + Refresh)
        
        Args:
            user_id: 用户 ID
            username: 用户名
            email: 邮箱
            role: 角色
            
        Returns:
            TokenPair 对象
        """
        access_token = self.create_access_token(user_id, username, email, role)
        refresh_token = self.create_refresh_token(user_id, username, email, role)
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(self._access_token_expire.total_seconds()),
        )
    
    # ========================================
    # Token 验证
    # ========================================
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenPayload]:
        """
        验证 Token
        
        Args:
            token: JWT Token
            token_type: 期望的 Token 类型 (access/refresh)
            
        Returns:
            TokenPayload (验证成功) 或 None (验证失败)
        """
        try:
            # 检查是否在黑名单中
            if token in self._blacklist:
                return None
            
            # 解码 Token
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            
            # 验证 Token 类型
            if payload.get("type") != token_type:
                return None
            
            # 构建 TokenPayload
            return TokenPayload(
                user_id=payload.get("sub"),
                username=payload.get("username"),
                email=payload.get("email"),
                role=payload.get("role"),
                exp=datetime.fromtimestamp(payload.get("exp")),
                iat=datetime.fromtimestamp(payload.get("iat")),
                jti=payload.get("jti"),
            )
        
        except jwt.ExpiredSignatureError:
            # Token 已过期
            return None
        
        except jwt.InvalidTokenError as e:
            # Token 无效
            print(f"[JWT] Invalid token: {e}")
            return None
        
        except Exception as e:
            print(f"[JWT] Verification error: {e}")
            return None
    
    def verify_access_token(self, token: str) -> Optional[TokenPayload]:
        """验证 Access Token"""
        return self.verify_token(token, token_type="access")
    
    def verify_refresh_token(self, token: str) -> Optional[TokenPayload]:
        """验证 Refresh Token"""
        return self.verify_token(token, token_type="refresh")
    
    # ========================================
    # Token 刷新
    # ========================================
    
    def refresh_access_token(self, refresh_token: str) -> Optional[TokenPair]:
        """
        使用 Refresh Token 刷新 Access Token
        
        Args:
            refresh_token: Refresh Token
            
        Returns:
            新的 TokenPair 或 None
        """
        # 验证 Refresh Token
        payload = self.verify_refresh_token(refresh_token)
        if not payload:
            return None
        
        # 生成新的 Token 对
        return self.create_token_pair(
            user_id=payload.user_id,
            username=payload.username,
            email=payload.email,
            role=payload.role,
        )
    
    # ========================================
    # Token 黑名单
    # ========================================
    
    def revoke_token(self, token: str) -> bool:
        """
        将 Token 加入黑名单 (撤销 Token)
        
        Args:
            token: 要撤销的 Token
            
        Returns:
            bool: 是否成功
        """
        try:
            # 验证 Token 有效性
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm], options={"verify_exp": False})
            
            # 加入黑名单
            self._blacklist.add(token)
            
            return True
        
        except Exception as e:
            print(f"[JWT] Revoke token error: {e}")
            return False
    
    def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        撤销用户所有 Token (强制下线)
        
        Args:
            user_id: 用户 ID
            
        Returns:
            撤销的 Token 数量 (仅统计黑名单中已知的)
        """
        # 注意：由于 JWT 无状态，无法直接获取用户所有 Token
        # 生产环境应使用 Redis 存储用户 Token 列表
        # 这里仅作为示例
        
        # 简单策略：不清理黑名单，让 Token 自然过期
        # 或者在验证时检查用户 ID 是否在禁用列表中
        
        return len(self._blacklist)
    
    def cleanup_blacklist(self) -> int:
        """
        清理黑名单中的过期 Token
        
        Returns:
            清理的数量
        """
        now = datetime.utcnow()
        expired_tokens = set()
        
        for token in self._blacklist:
            try:
                payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm], options={"verify_exp": False})
                exp = datetime.fromtimestamp(payload.get("exp", 0))
                
                if exp < now:
                    expired_tokens.add(token)
            
            except Exception:
                expired_tokens.add(token)
        
        self._blacklist -= expired_tokens
        return len(expired_tokens)
    
    # ========================================
    # 工具方法
    # ========================================
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """
        获取 Token 信息 (不验证签名和过期)
        
        Args:
            token: JWT Token
            
        Returns:
            Token 信息字典或 None
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm], options={"verify_exp": False})
            return payload
        except Exception as e:
            print(f"[JWT] Get token info error: {e}")
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        检查 Token 是否过期
        
        Args:
            token: JWT Token
            
        Returns:
            bool: 是否已过期
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return False
        except jwt.ExpiredSignatureError:
            return True
        except Exception:
            return True


# ============================================
# 单例
# ============================================

_jwt_handler_instance: Optional[JWTHandler] = None


def get_jwt_handler(
    secret_key: Optional[str] = None,
    access_token_expire_minutes: int = 60,
    refresh_token_expire_days: int = 7
) -> JWTHandler:
    """获取 JWTHandler 单例"""
    global _jwt_handler_instance
    if _jwt_handler_instance is None:
        _jwt_handler_instance = JWTHandler(
            secret_key=secret_key,
            access_token_expire_minutes=access_token_expire_minutes,
            refresh_token_expire_days=refresh_token_expire_days,
        )
    return _jwt_handler_instance
