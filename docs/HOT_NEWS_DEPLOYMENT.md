# 热点展示系统部署指南

## 📊 系统概述

基于 MySQL + FastAPI + Vue 3 的热点数据展示系统，与 YouMind 技术栈对齐。

**技术栈**:
- **后端**: FastAPI (Python)
- **数据库**: MySQL (43.134.234.4:3306/youmind)
- **前端**: Vue 3 + TailwindCSS
- **API 文档**: Swagger/OpenAPI

---

## 🚀 快速启动

### 方式 1: 使用启动脚本 (推荐)

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher
bash scripts/start_hot_news.sh
```

### 方式 2: 手动启动

```bash
# 1. 安装依赖
pip3 install fastapi uvicorn pymysql

# 2. 启动 API 服务
cd /root/.openclaw/workspace-writer/ai-article-publisher
python3 -m uvicorn api.hot_news_api:app --host 0.0.0.0 --port 8080 --reload

# 3. 启动前端 (可选)
cd frontend
python3 -m http.server 3000
```

---

## 📍 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **API 服务** | http://43.134.234.4:8080 | 后端 API |
| **API 文档** | http://43.134.234.4:8080/docs | Swagger UI |
| **前端页面** | http://43.134.234.4:3000/hot-news-dashboard.html | Vue 前端 |
| **直接打开** | `frontend/hot-news-dashboard.html` | 本地文件 |

---

## 🔧 数据库配置

### 连接信息

```python
{
    "host": "43.134.234.4",
    "port": 3306,
    "database": "youmind",
    "user": "youmind",
    "password": "YouMind2026"
}
```

### 数据表结构

```sql
-- 热点主表
CREATE TABLE hot_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    url VARCHAR(1000),
    source_id INT,
    crawl_time DATETIME,
    heat_score DECIMAL(5,2),
    heat_level VARCHAR(20),
    category VARCHAR(50),
    tags JSON,
    keyword_hash VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 来源表
CREATE TABLE hot_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    platform VARCHAR(50),
    category VARCHAR(50),
    priority INT DEFAULT 5,
    credibility DECIMAL(3,2) DEFAULT 0.5
);

-- 关键词表
CREATE TABLE hot_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    weight DECIMAL(5,2) DEFAULT 1.0
);
```

---

## 📡 API 接口

### 获取热点列表

```bash
GET /api/topics?limit=20&category=教育&heat_level=hot&hours=24
```

**参数**:
- `limit`: 返回数量 (1-100)
- `category`: 分类过滤
- `heat_level`: 热度等级 (explosive/hot/warm/normal)
- `hours`: 时间范围 (小时)

**响应**:
```json
{
  "success": true,
  "data": {
    "topics": [...],
    "count": 20,
    "filters": {...}
  },
  "message": "success",
  "timestamp": "2026-03-01T12:00:00"
}
```

### 获取统计数据

```bash
GET /api/statistics?days=7
```

### 获取数据源

```bash
GET /api/sources?active_only=true
```

### 获取热门关键词

```bash
GET /api/keywords?limit=50
```

### 获取分类列表

```bash
GET /api/categories
```

---

## 🎨 前端功能

### 功能列表

- ✅ 热点列表展示 (按热度排序)
- ✅ 多维度筛选 (分类/热度/时间)
- ✅ 统计卡片 (总数/平均热度/最高热度)
- ✅ 热词云展示
- ✅ 热点详情弹窗
- ✅ 自动刷新 (5 分钟)
- ✅ 响应式设计 (手机/平板/PC)

### 热度等级标识

| 等级 | 分数 | 颜色 | 标识 |
|------|------|------|------|
| explosive | 90-100 | 🔴 红色 | 🚀 爆款 |
| hot | 75-89 | 🟠 橙色 | 🔥 热门 |
| warm | 60-74 | 🟡 黄色 | 🌡️ 温热点 |
| normal | 0-59 | 🟢 绿色 | 📊 普通 |

---

## 📝 使用示例

### 1. 添加测试数据

```python
from core.hot_database_mysql import HotNewsDatabaseMySQL

db = HotNewsDatabaseMySQL()

# 添加数据源
db.add_source("微博热搜", platform="微博", category="综合", credibility=0.8)

# 添加热点
db.add_hot_topic(
    title="教育部发布 AI+ 教育指导意见",
    content="教育部近日发布...",
    source_name="澎湃新闻",
    category="教育",
    tags=["AI", "教育"],
    keywords=["教育部", "AI 教育"]
)

db.close()
```

### 2. 查询热点

```python
# 获取最新热点
topics = db.get_hot_topics(limit=20)

# 按分类查询
edu_topics = db.get_hot_topics(category="教育")

# 按热度查询
hot_topics = db.get_hot_topics(heat_level="hot")
```

### 3. 获取统计

```python
stats = db.get_statistics(days=7)

print(f"总热点数：{stats['overall']['total_count']}")
print(f"平均热度：{stats['overall']['avg_heat']}")

# 按分类统计
for cat in stats['by_category']:
    print(f"{cat['category']}: {cat['count']}条")
```

---

## 🔍 服务管理

### 查看服务状态

```bash
# 检查 API 服务
curl http://localhost:8080/

# 查看进程
ps aux | grep hot_news_api

# 查看日志
tail -f /tmp/hot_news_api.log
```

### 停止服务

```bash
# 查找进程
ps aux | grep uvicorn

# 停止服务
kill <PID>

# 或者强制停止
pkill -f "hot_news_api"
```

### 重启服务

```bash
# 停止
pkill -f "hot_news_api"

# 等待
sleep 2

# 启动
bash scripts/start_hot_news.sh
```

---

## 🛠️ 故障排查

### API 无法启动

```bash
# 检查端口占用
netstat -tlnp | grep 8080

# 检查日志
cat /tmp/hot_news_api.log

# 检查依赖
pip3 list | grep -E "fastapi|uvicorn|pymysql"
```

### 数据库连接失败

```bash
# 测试数据库连接
mysql -h 43.134.234.4 -u youmind -pYouMind2026 youmind

# 检查网络
ping 43.134.234.4

# 检查端口
telnet 43.134.234.4 3306
```

### 前端无法访问

```bash
# 检查文件权限
ls -la frontend/hot-news-dashboard.html

# 启动 HTTP 服务器
cd frontend
python3 -m http.server 3000

# 检查防火墙
ufw status
```

---

## 📊 性能优化

### 数据库索引

```sql
-- 添加索引
CREATE INDEX idx_crawl_time ON hot_topics(crawl_time);
CREATE INDEX idx_heat ON hot_topics(heat_score);
CREATE INDEX idx_category ON hot_topics(category);
CREATE INDEX idx_hash ON hot_topics(keyword_hash);
```

### API 缓存

```python
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

@app.get("/api/topics")
@cache(expire=300)  # 5 分钟缓存
async def get_hot_topics():
    ...
```

---

## 🔐 安全建议

### 生产环境配置

1. **限制 CORS**: 修改 `allow_origins` 为具体域名
2. **添加认证**: 使用 JWT 或 API Key
3. **HTTPS**: 配置 SSL 证书
4. **限流**: 添加请求频率限制
5. **日志**: 记录所有 API 访问

### 数据库安全

1. **最小权限**: 只授予必要的权限
2. **定期备份**: 每天备份数据库
3. **密码强度**: 使用强密码
4. **网络隔离**: 限制数据库访问 IP

---

## 📈 监控指标

### API 监控

- 请求量 (QPS)
- 响应时间 (P95/P99)
- 错误率
- 活跃连接数

### 数据库监控

- 查询量
- 慢查询
- 连接数
- 表空间

---

*最后更新：2026-03-01*
