# 热点展示系统 - 完整部署总结

**开发时间**: 2026-03-01
**技术栈**: MySQL + FastAPI + Vue 3
**对齐**: YouMind 技术栈

---

## 📊 开发成果

### 1. MySQL 数据库模块

**文件**: `core/hot_database_mysql.py` (19KB)

**功能**:
- ✅ MySQL 连接管理 (43.134.234.4:3306/youmind)
- ✅ 4 张核心表 (热点/来源/关键词/统计)
- ✅ 智能去重 (关键词哈希)
- ✅ 热度评分 (多维权重)
- ✅ 自动分类
- ✅ 统计分析

**数据库配置**:
```python
{
    "host": "43.134.234.4",
    "port": 3306,
    "database": "youmind",
    "user": "youmind",
    "password": "YouMind2026"
}
```

### 2. FastAPI 后端

**文件**: `api/hot_news_api.py` (6KB)

**API 接口**:
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/topics` | GET | 获取热点列表 |
| `/api/topics/{id}` | GET | 获取热点详情 |
| `/api/sources` | GET | 获取数据源 |
| `/api/statistics` | GET | 获取统计数据 |
| `/api/categories` | GET | 获取分类列表 |
| `/api/keywords` | GET | 获取热门关键词 |

**特性**:
- ✅ RESTful API 设计
- ✅ Swagger 文档 (/docs)
- ✅ CORS 支持
- ✅ Pydantic 数据验证
- ✅ 错误处理

### 3. Vue 3 前端

**文件**: `frontend/hot-news-dashboard.html` (17KB)

**功能**:
- ✅ 热点列表展示 (按热度排序)
- ✅ 多维度筛选 (分类/热度/时间)
- ✅ 统计卡片 (4 个指标)
- ✅ 热词云展示
- ✅ 热点详情弹窗
- ✅ 自动刷新 (5 分钟)
- ✅ 响应式设计

**技术栈**:
- Vue 3 (CDN)
- TailwindCSS (CDN)
- 原生 Fetch API
- 单文件 HTML (无需构建)

### 4. 部署脚本

**文件**: `scripts/start_hot_news.sh` (2KB)

**功能**:
- ✅ 依赖检查 (pymysql/fastapi/uvicorn)
- ✅ 自动安装缺失依赖
- ✅ 后台启动 API 服务
- ✅ 健康检查
- ✅ 日志管理

---

## 🚀 部署步骤

### 1. 安装依赖

```bash
pip3 install fastapi uvicorn pymysql
```

### 2. 启动服务

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher
bash scripts/start_hot_news.sh
```

### 3. 访问系统

| 服务 | 地址 |
|------|------|
| API 文档 | http://43.134.234.4:8080/docs |
| 前端页面 | http://43.134.234.4:3000/hot-news-dashboard.html |

---

## 📁 文件清单

```
ai-article-publisher/
├── core/
│   ├── hot_database_mysql.py      (19KB) - MySQL 数据库模块
│   └── hot_database.py            (20KB) - SQLite 版本 (保留)
├── api/
│   └── hot_news_api.py            (6KB)  - FastAPI 后端
├── frontend/
│   └── hot-news-dashboard.html    (17KB) - Vue 3 前端
├── scripts/
│   └── start_hot_news.sh          (2KB)  - 启动脚本
└── docs/
    ├── HOT_NEWS_DEPLOYMENT.md     - 部署指南
    ├── HOT_NEWS_DATABASE_GUIDE.md - 数据库指南
    └── HOT_NEWS_SUMMARY.md        - 本文件
```

---

## 🎯 与 YouMind 技术栈对齐

| 组件 | YouMind | 热点系统 | 状态 |
|------|---------|---------|------|
| 数据库 | MySQL | MySQL (youmind 库) | ✅ 对齐 |
| 后端框架 | FastAPI | FastAPI | ✅ 对齐 |
| 前端框架 | Vue 3 | Vue 3 | ✅ 对齐 |
| API 风格 | RESTful | RESTful | ✅ 对齐 |
| 数据格式 | JSON | JSON | ✅ 对齐 |

---

## 📊 数据库表结构

### hot_topics (热点主表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| title | VARCHAR(500) | 热点标题 |
| content | TEXT | 内容摘要 |
| url | VARCHAR(1000) | 原文链接 |
| source_id | INT | 来源 ID |
| crawl_time | DATETIME | 采集时间 |
| heat_score | DECIMAL(5,2) | 热度值 |
| heat_level | VARCHAR(20) | 热度等级 |
| category | VARCHAR(50) | 分类 |
| tags | JSON | 标签 |
| keyword_hash | VARCHAR(64) | 去重哈希 |

### hot_sources (来源表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| name | VARCHAR(100) | 来源名称 |
| platform | VARCHAR(50) | 平台 |
| category | VARCHAR(50) | 分类 |
| priority | INT | 优先级 |
| credibility | DECIMAL(3,2) | 可信度 |

### hot_keywords (关键词表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| topic_id | INT | 热点 ID |
| keyword | VARCHAR(100) | 关键词 |
| weight | DECIMAL(5,2) | 权重 |

### hot_statistics (统计表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| stat_date | DATE | 统计日期 |
| category | VARCHAR(50) | 分类 |
| source_id | INT | 来源 ID |
| total_count | INT | 总数 |
| avg_heat_score | DECIMAL(5,2) | 平均热度 |

---

## 🧪 测试数据

### 添加测试热点

```python
from core.hot_database_mysql import HotNewsDatabaseMySQL

db = HotNewsDatabaseMySQL()

# 添加数据源
db.add_source("微博热搜", platform="微博", category="综合", credibility=0.8)
db.add_source("知乎热榜", platform="知乎", category="综合", credibility=0.85)
db.add_source("澎湃新闻", platform="澎湃新闻", category="新闻", credibility=0.9)

# 添加热点
db.add_hot_topic(
    title="教育部发布 AI+ 教育指导意见，60% 高校已开设相关课程",
    content="教育部近日发布...",
    source_name="澎湃新闻",
    category="教育",
    tags=["AI", "教育", "政策"],
    keywords=["教育部", "AI 教育", "高校课程"]
)

db.close()
```

---

## 📈 系统特性

### 性能

- **数据库**: MySQL InnoDB 引擎
- **索引**: crawl_time/heat_score/category/keyword_hash
- **缓存**: 前端 5 分钟自动刷新
- **并发**: 支持多用户同时访问

### 安全

- **CORS**: 可配置跨域限制
- **参数验证**: Pydantic 模型验证
- **SQL 注入**: 参数化查询
- **错误处理**: 统一的异常处理

### 可扩展性

- **模块化**: 数据库/API/前端分离
- **RESTful**: 标准 API 设计
- **文档**: Swagger 自动生成
- **日志**: 集中日志管理

---

## 🔧 运维管理

### 服务管理

```bash
# 启动
bash scripts/start_hot_news.sh

# 停止
pkill -f "hot_news_api"

# 重启
pkill -f "hot_news_api" && sleep 2 && bash scripts/start_hot_news.sh

# 查看状态
ps aux | grep uvicorn
curl http://localhost:8080/

# 查看日志
tail -f /tmp/hot_news_api.log
```

### 数据库管理

```bash
# 连接数据库
mysql -h 43.134.234.4 -u youmind -pYouMind2026 youmind

# 查看热点数量
SELECT COUNT(*) FROM hot_topics;

# 查看最新热点
SELECT * FROM hot_topics ORDER BY crawl_time DESC LIMIT 10;

# 清理旧数据
DELETE FROM hot_topics WHERE crawl_time < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

---

## 📝 API 使用示例

### 获取热点列表

```bash
curl "http://43.134.234.4:8080/api/topics?limit=20&category=教育"
```

### 获取统计数据

```bash
curl "http://43.134.234.4:8080/api/statistics?days=7"
```

### 获取热门关键词

```bash
curl "http://43.134.234.4:8080/api/keywords?limit=50"
```

### Python 调用

```python
import requests

# 获取热点
res = requests.get("http://43.134.234.4:8080/api/topics")
topics = res.json()["data"]["topics"]

# 获取统计
res = requests.get("http://43.134.234.4:8080/api/statistics")
stats = res.json()["data"]
```

---

## 🎨 前端截图功能

### 热点列表
- 按热度排序显示
- 热度等级颜色标识
- 分类/来源/时间标签
- 点击查看详情

### 统计卡片
- 总热点数
- 平均热度
- 最高热度
- 唯一热点

### 热词云
- 按词频显示
- 字体大小反映热度
- 点击可筛选

---

## ⏭️ 后续优化

1. **用户认证**: JWT Token 认证
2. **权限管理**: 角色权限控制
3. **数据导入**: 批量导入工具
4. **导出功能**: Excel/CSV 导出
5. **图表展示**: ECharts 可视化
6. **实时推送**: WebSocket 实时更新
7. **移动端**: 小程序/App

---

## 📞 技术支持

### 常见问题

**Q: API 无法启动？**
A: 检查端口占用 `netstat -tlnp | grep 8080`，检查依赖 `pip3 list`

**Q: 数据库连接失败？**
A: 检查网络 `ping 43.134.234.4`，检查凭据，检查防火墙

**Q: 前端无法访问？**
A: 检查文件路径，启动 HTTP 服务器 `python3 -m http.server 3000`

### 日志位置

- API 日志：`/tmp/hot_news_api.log`
- MySQL 日志：`/var/log/mysql/error.log`

---

*最后更新：2026-03-01*
*版本：1.0.0*
