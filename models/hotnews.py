#!/usr/bin/env python3
"""
热点数据模型 - HotNews Models
V3 热点中心模块数据模型定义

包含:
- HotNews: 热点主表模型
- Subscription: 订阅表模型

数据库: MySQL (youmind 数据库)
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


# ============================================
# 热点主表模型
# ============================================

class HotNews(BaseModel):
    """
    热点数据模型
    
    对应数据库表：hotnews
    
    字段说明:
    - id: 热点唯一标识 (使用平台_原始 ID 组合)
    - title: 热点标题
    - content: 热点内容/描述
    - platform: 来源平台 (微博/知乎/B 站等)
    - category: 分类 (科技/教育/财经/娱乐等)
    - heat_count: 热度数值 (阅读量/点赞数等)
    - heat_level: 热度等级 (🔥100 万+/🔥50 万+/🔥10 万+)
    - source_url: 原始链接
    - publish_time: 发布时间
    - crawl_time: 采集时间
    - trend_data: 24 小时热度趋势 (JSON)
    - extra_data: 扩展数据 (JSON)
    """
    
    id: str = Field(..., description="热点唯一标识")
    title: str = Field(..., max_length=500, description="热点标题")
    content: Optional[str] = Field(None, description="热点内容/描述")
    platform: Optional[str] = Field(None, max_length=50, description="来源平台")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    heat_count: int = Field(0, description="热度数值")
    heat_level: str = Field("normal", description="热度等级")
    source_url: Optional[str] = Field(None, max_length=500, description="原始链接")
    publish_time: Optional[datetime] = Field(None, description="发布时间")
    crawl_time: datetime = Field(default_factory=datetime.now, description="采集时间")
    trend_data: Optional[Any] = Field(None, description="24 小时热度趋势")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="扩展数据")
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "id": "weibo_12345",
                "title": "某热点新闻事件",
                "content": "事件详细描述...",
                "platform": "微博",
                "category": "社会",
                "heat_count": 1500000,
                "heat_level": "🔥100 万+",
                "source_url": "https://weibo.com/xxx",
                "publish_time": "2026-03-01T10:00:00",
                "crawl_time": "2026-03-01T10:05:00",
                "trend_data": {"hours": [...], "heat_values": [...]},
                "extra_data": {"comments": 5000, "shares": 3000}
            }
        }
    
    @classmethod
    def calculate_heat_level(cls, heat_count: int) -> str:
        """根据热度数值计算热度等级"""
        if heat_count >= 1000000:
            return "🔥100 万+"
        elif heat_count >= 500000:
            return "🔥50 万+"
        elif heat_count >= 100000:
            return "🔥10 万+"
        elif heat_count >= 50000:
            return "🔥5 万+"
        elif heat_count >= 10000:
            return "🔥1 万+"
        else:
            return "normal"
    
    def model_post_init(self, __context):
        """模型初始化后处理"""
        # 如果未指定 heat_level，根据 heat_count 自动计算
        if not hasattr(self, '_heat_level_set') or self.heat_level == "normal":
            if self.heat_count > 0:
                self.heat_level = self.calculate_heat_level(self.heat_count)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.dict()
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        import json
        from datetime import datetime
        
        data = self.to_dict()
        # 处理 datetime 序列化
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        return json.dumps(data, ensure_ascii=False, default=str)
    
    @classmethod
    def from_database_row(cls, row: Dict[str, Any]) -> "HotNews":
        """
        从数据库行记录创建模型实例
        
        Args:
            row: 数据库查询结果行 (dict)
        
        Returns:
            HotNews 实例
        """
        # 处理 JSON 字段
        trend_data = row.get('trend_data')
        if isinstance(trend_data, str):
            trend_data = json.loads(trend_data)
        
        extra_data = row.get('extra_data')
        if isinstance(extra_data, str):
            extra_data = json.loads(extra_data)
        
        return cls(
            id=row['id'],
            title=row['title'],
            content=row.get('content'),
            platform=row.get('platform'),
            category=row.get('category'),
            heat_count=row.get('heat_count', 0),
            heat_level=row.get('heat_level', 'normal'),
            source_url=row.get('source_url'),
            publish_time=row.get('publish_time'),
            crawl_time=row.get('crawl_time', datetime.now()),
            trend_data=trend_data,
            extra_data=extra_data
        )


# ============================================
# 订阅表模型
# ============================================

class Subscription(BaseModel):
    """
    热点订阅模型
    
    对应数据库表：hotnews_subscriptions
    
    字段说明:
    - id: 订阅记录 ID
    - user_id: 用户 ID
    - keyword: 订阅关键词
    - platform: 订阅平台 (可选)
    - category: 订阅分类 (可选)
    - notify_enabled: 是否启用通知
    - created_at: 创建时间
    """
    
    id: Optional[int] = Field(None, description="订阅记录 ID")
    user_id: str = Field(..., description="用户 ID")
    keyword: str = Field(..., max_length=100, description="订阅关键词")
    platform: Optional[str] = Field(None, max_length=50, description="订阅平台")
    category: Optional[str] = Field(None, max_length=50, description="订阅分类")
    notify_enabled: bool = Field(True, description="是否启用通知")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_001",
                "keyword": "人工智能",
                "platform": "知乎",
                "category": "科技",
                "notify_enabled": True,
                "created_at": "2026-03-01T10:00:00"
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.dict()
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return self.json(ensure_ascii=False)
    
    @classmethod
    def from_database_row(cls, row: Dict[str, Any]) -> "Subscription":
        """
        从数据库行记录创建模型实例
        
        Args:
            row: 数据库查询结果行 (dict)
        
        Returns:
            Subscription 实例
        """
        return cls(
            id=row.get('id'),
            user_id=row['user_id'],
            keyword=row['keyword'],
            platform=row.get('platform'),
            category=row.get('category'),
            notify_enabled=bool(row.get('notify_enabled', True)),
            created_at=row.get('created_at', datetime.now())
        )


# ============================================
# 辅助数据模型
# ============================================

class TrendData(BaseModel):
    """热度趋势数据模型"""
    
    item_id: str = Field(..., description="热点 ID")
    trend: List[Dict[str, Any]] = Field(..., description="趋势数据列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "weibo_12345",
                "trend": [
                    {"time": "2026-03-01T00:00:00", "heat": 50000},
                    {"time": "2026-03-01T01:00:00", "heat": 55000},
                    {"time": "2026-03-01T02:00:00", "heat": 60000}
                ]
            }
        }


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    
    data: List[HotNews] = Field(..., description="数据列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    
    @classmethod
    def create(cls, items: List[HotNews], total: int, page: int, page_size: int) -> "PaginatedResponse":
        """创建分页响应"""
        return cls(
            data=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )


# ============================================
# 数据库表结构 SQL
# ============================================

CREATE_TABLE_SQL = """
-- 热点表
CREATE TABLE IF NOT EXISTS hotnews (
    id VARCHAR(64) PRIMARY KEY COMMENT '热点唯一标识 (平台_原始 ID)',
    title VARCHAR(500) NOT NULL COMMENT '热点标题',
    content TEXT COMMENT '热点内容/描述',
    platform VARCHAR(50) COMMENT '来源平台',
    category VARCHAR(50) COMMENT '分类',
    heat_count INT DEFAULT 0 COMMENT '热度数值',
    heat_level VARCHAR(20) DEFAULT 'normal' COMMENT '热度等级',
    source_url VARCHAR(500) COMMENT '原始链接',
    publish_time DATETIME COMMENT '发布时间',
    crawl_time DATETIME NOT NULL COMMENT '采集时间',
    trend_data JSON COMMENT '24 小时热度趋势',
    extra_data JSON COMMENT '扩展数据',
    INDEX idx_platform (platform),
    INDEX idx_category (category),
    INDEX idx_heat (heat_count),
    INDEX idx_time (publish_time),
    INDEX idx_crawl_time (crawl_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订阅表
CREATE TABLE IF NOT EXISTS hotnews_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL COMMENT '用户 ID',
    keyword VARCHAR(100) NOT NULL COMMENT '订阅关键词',
    platform VARCHAR(50) COMMENT '订阅平台',
    category VARCHAR(50) COMMENT '订阅分类',
    notify_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用通知',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user (user_id),
    INDEX idx_keyword (keyword),
    INDEX idx_platform (platform),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""
