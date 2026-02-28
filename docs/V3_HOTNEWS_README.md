# V3 热点中心模块文档

> 版本：3.0.0  
> 状态：Phase 1 ✅ 完成  
> 最后更新：2026-03-01

---

## 📋 概述

V3 热点中心模块提供全面的热点数据采集、存储、查询和订阅功能。

### 核心功能

- 🔥 **实时热榜**: 支持 50+ 平台热榜聚合展示
- 🔍 **多维度筛选**: 平台/分类/时间/热度/关键词
- 📊 **热度趋势**: 24 小时热度变化曲线
- 📬 **热点订阅**: 关键词/平台/分类订阅
- 🎯 **智能搜索**: 全文检索

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────┐
│          Frontend (Web UI)              │
│  - 热点列表  - 筛选器  - 搜索          │
│  - 热点详情  - 趋势图  - 订阅管理      │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         API Layer (FastAPI)             │
│  /api/v3/hotnews/* (8 个接口)           │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       Core Service (Python)             │
│  HotNewsService (6 个核心方法)          │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│        Data Layer (MySQL)               │
│  - hotnews (热点表)                     │
│  - hotnews_subscriptions (订阅表)       │
└─────────────────────────────────────────┘
```

---

## 📦 文件结构

```
ai-article-publisher/
├── models/
│   ├── __init__.py              # 模型包初始化
│   └── hotnews.py               # 数据模型 (HotNews, Subscription)
├── core/
│   └── hotnews_service.py       # 核心服务
├── api/v3/
│   └── hotnews.py               # API 路由
├── scripts/
│   ├── migrate_hotnews_v3.py    # 数据库迁移
│   └── run_hotnews_api.py       # API 启动脚本
├── tests/
│   └── test_hotnews_v3.py       # 测试用例
└── docs/
    ├── V3_MODULE_DESIGN.md      # 模块设计方案
    └── V3_HOTNEWS_README.md     # 本文档
```

---

## 🚀 快速开始

### 1. 数据库迁移

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher
python scripts/migrate_hotnews_v3.py
```

输出:
```
============================================================
🚀 V3 热点中心数据库迁移
============================================================
✅ 数据库迁移成功完成!
📋 创建的表:
   - hotnews (12 字段)
   - hotnews_subscriptions (7 字段)
```

### 2. 启动 API 服务

```bash
python scripts/run_hotnews_api.py
```

服务启动后:
- **API 地址**: http://0.0.0.0:8081
- **API 文档**: http://localhost:8081/api/v3/docs
- **ReDoc**: http://localhost:8081/api/v3/redoc

### 3. 运行测试

```bash
python tests/test_hotnews_v3.py
```

预期输出:
```
============================================================
📊 测试结果：14 通过，0 失败
============================================================
```

---

## 📡 API 接口

### 获取热点列表

```http
GET /api/v3/hotnews
```

**查询参数**:
- `platform` (可选): 平台筛选 (微博/知乎/B 站等)
- `category` (可选): 分类筛选 (科技/教育/财经等)
- `time_range` (可选): 时间范围 (1h/6h/24h/7d), 默认 24h
- `min_heat` (可选): 最低热度值，默认 0
- `keyword` (可选): 关键词过滤
- `page` (可选): 页码，默认 1
- `page_size` (可选): 每页数量，默认 50

**示例**:
```bash
curl "http://localhost:8081/api/v3/hotnews?platform=知乎&category=科技&time_range=24h&page=1&page_size=20"
```

**响应**:
```json
{
  "success": true,
  "data": {
    "data": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "message": "获取成功，共 100 条记录"
}
```

---

### 获取热点详情

```http
GET /api/v3/hotnews/:id
```

**示例**:
```bash
curl "http://localhost:8081/api/v3/hotnews/zhihu_12345"
```

---

### 获取热度趋势

```http
GET /api/v3/hotnews/:id/trend?hours=24
```

**参数**:
- `hours`: 时间范围 (小时), 默认 24, 最大 168

**示例**:
```bash
curl "http://localhost:8081/api/v3/hotnews/zhihu_12345/trend?hours=24"
```

---

### 订阅热点

```http
POST /api/v3/hotnews/subscribe
Content-Type: application/json

{
  "keyword": "人工智能",
  "platform": "知乎",
  "category": "科技",
  "notify_enabled": true
}
```

---

### 搜索热点

```http
GET /api/v3/hotnews/search?q=AI&platform=知乎&limit=50
```

**参数**:
- `q` (必填): 搜索关键词
- `platform` (可选): 平台筛选
- `category` (可选): 分类筛选
- `time_range` (可选): 时间范围
- `limit` (可选): 返回数量限制

---

### 获取用户订阅列表

```http
GET /api/v3/hotnews/subscriptions?user_id=test_user_001
```

---

### 取消订阅

```http
DELETE /api/v3/hotnews/subscribe/:keyword?user_id=test_user_001
```

---

### 获取统计信息

```http
GET /api/v3/hotnews/statistics?days=7
```

**响应**:
```json
{
  "success": true,
  "data": {
    "total": 500,
    "avg_heat": 125000,
    "max_heat": 2500000,
    "by_platform": [...],
    "by_category": [...],
    "period_days": 7
  }
}
```

---

## 💾 数据模型

### HotNews (热点)

```python
{
  "id": "zhihu_12345",           # 热点唯一标识
  "title": "某热点新闻",           # 标题
  "content": "详细描述...",       # 内容
  "platform": "知乎",             # 平台
  "category": "科技",             # 分类
  "heat_count": 1500000,         # 热度数值
  "heat_level": "🔥100 万+",      # 热度等级
  "source_url": "https://...",   # 原始链接
  "publish_time": "2026-03-01T10:00:00",  # 发布时间
  "crawl_time": "2026-03-01T10:05:00",    # 采集时间
  "trend_data": {...},           # 趋势数据
  "extra_data": {...}            # 扩展数据
}
```

### Subscription (订阅)

```python
{
  "id": 1,
  "user_id": "user_001",
  "keyword": "人工智能",
  "platform": "知乎",
  "category": "科技",
  "notify_enabled": true,
  "created_at": "2026-03-01T10:00:00"
}
```

---

## 🔧 核心服务

### HotNewsService 方法

```python
from core.hotnews_service import HotNewsService

service = HotNewsService()

# 1. 获取热点列表
result = service.get_hotlist(
    platform="知乎",
    category="科技",
    time_range="24h",
    min_heat=100000,
    page=1,
    page_size=50
)

# 2. 获取热度趋势
trend = service.get_trend("zhihu_12345", hours=24)

# 3. 订阅热点
subscription = service.subscribe(
    keyword="人工智能",
    user_id="user_001",
    platform="知乎",
    category="科技"
)

# 4. 搜索热点
results = service.search(
    query="AI 技术",
    platform="知乎",
    limit=50
)

# 5. 获取热点详情
hotnews = service.get_by_id("zhihu_12345")

# 6. 获取统计信息
stats = service.get_statistics(days=7)

service.close()
```

---

## 🧪 测试

### 运行所有测试

```bash
python tests/test_hotnews_v3.py
```

### 测试覆盖

- ✅ 数据模型测试 (7 个)
  - HotNews 创建
  - 热度等级自动计算
  - 序列化/反序列化
  - 从数据库行创建
  - Subscription 创建
  - 分页响应

- ✅ 核心服务测试 (6 个)
  - 获取热点列表
  - 筛选功能
  - 搜索功能
  - 统计功能
  - 订阅/取消订阅
  - 根据 ID 获取

- ✅ 集成测试 (1 个)
  - 完整工作流测试

---

## 📊 数据库表结构

### hotnews (热点表)

```sql
CREATE TABLE hotnews (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    platform VARCHAR(50),
    category VARCHAR(50),
    heat_count INT DEFAULT 0,
    heat_level VARCHAR(20) DEFAULT 'normal',
    source_url VARCHAR(500),
    publish_time DATETIME,
    crawl_time DATETIME NOT NULL,
    trend_data JSON,
    extra_data JSON,
    INDEX idx_platform (platform),
    INDEX idx_category (category),
    INDEX idx_heat (heat_count),
    INDEX idx_time (publish_time),
    INDEX idx_crawl_time (crawl_time)
);
```

### hotnews_subscriptions (订阅表)

```sql
CREATE TABLE hotnews_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    platform VARCHAR(50),
    category VARCHAR(50),
    notify_enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_keyword (keyword),
    INDEX idx_platform (platform),
    INDEX idx_category (category)
);
```

---

## 🎯 Phase 1 完成状态

- ✅ 数据库设计 (2 张表)
- ✅ 核心服务 (6 个方法)
- ✅ API 路由 (8 个接口)
- ✅ 数据模型 (HotNews, Subscription)
- ✅ 数据库迁移脚本
- ✅ 测试用例 (14 个测试)
- ✅ 文档更新

**测试通过率**: 14/14 (100%)

---

## 📝 下一步计划

### Phase 2: 数据采集整合
- [ ] 复用 `sources/dailyhot_collector.py`
- [ ] 复用 `sources/extended_collectors_v2.py`
- [ ] 统一数据格式
- [ ] 自动采集调度

### Phase 3: 前端界面
- [ ] 热点列表页面
- [ ] 筛选器组件
- [ ] 搜索功能
- [ ] 热度趋势图
- [ ] 订阅管理

---

## 🔗 相关文档

- [V3 模块设计方案](./V3_MODULE_DESIGN.md)
- [项目进度](../PROGRESS.md)
- [API 文档](http://localhost:8081/api/v3/docs)

---

*文档创建时间：2026-03-01*
