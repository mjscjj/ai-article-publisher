# 热点数据库与采集器 V2 使用指南

## 📊 概述

热点采集模块已完成重构，采用新的数据库架构，实现：
- ✅ 结构化存储 (SQLite)
- ✅ 智能去重 (关键词哈希)
- ✅ 热度评分 (多维权重)
- ✅ 自动分类 (基于关键词)
- ✅ 统计分析 (多维度报表)

---

## 🗄️ 数据库结构

### 1. hot_topics (热点主表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| title | TEXT | 热点标题 |
| content | TEXT | 内容摘要 |
| url | TEXT | 原文链接 |
| source_id | INTEGER | 来源 ID |
| crawl_time | DATETIME | 采集时间 |
| publish_time | DATETIME | 发布时间 |
| heat_score | REAL | 热度值 (0-100) |
| heat_level | TEXT | 热度等级 (explosive/hot/warm/normal) |
| category | TEXT | 分类 |
| tags | TEXT | 标签 (JSON) |
| keyword_hash | TEXT | 关键词哈希 (去重用) |

### 2. hot_sources (来源表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 来源名称 |
| platform | TEXT | 平台 |
| category | TEXT | 分类 |
| priority | INTEGER | 优先级 |
| credibility | REAL | 可信度 (0-1) |

### 3. hot_keywords (关键词表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| topic_id | INTEGER | 热点 ID |
| keyword | TEXT | 关键词 |
| weight | REAL | 权重 |

### 4. hot_statistics (统计表)

| 字段 | 类型 | 说明 |
|------|------|------|
| stat_date | DATE | 统计日期 |
| category | TEXT | 分类 |
| source_id | INTEGER | 来源 ID |
| total_count | INTEGER | 总数 |
| avg_heat_score | REAL | 平均热度 |

---

## 🚀 快速开始

### 1. 基础使用

```python
from core.hot_database import HotNewsDatabase

# 初始化数据库
db = HotNewsDatabase()

# 添加数据源
db.add_source("微博热搜", platform="微博", category="综合", 
              priority=10, credibility=0.8)

# 添加热点
db.add_hot_topic(
    title="教育部发布 AI+ 教育指导意见",
    content="教育部近日发布...",
    url="https://example.com/news/123",
    source_name="澎湃新闻",
    category="教育",
    tags=["AI", "教育", "政策"],
    keywords=["教育部", "AI 教育", "高校课程"]
)

# 查询热点
topics = db.get_hot_topics(limit=20)
for topic in topics:
    print(f"{topic['title']} - 热度：{topic['heat_score']}")

# 统计数据
stats = db.get_statistics(days=7)
print(f"总热点数：{stats['overall']['total_count']}")

db.close()
```

### 2. 使用采集器 V2

```python
from core.hot_collector_v2 import HotNewsCollectorV2

# 初始化采集器
collector = HotNewsCollectorV2()

# 采集所有数据源
report = collector.collect_all(save_to_db=True)

# 查询热点
topics = collector.get_hot_topics(limit=10)

# 获取统计
stats = collector.get_statistics(days=7)

collector.close()
```

### 3. 模拟数据测试

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher
python3 core/test_hot_collector_v2.py
```

---

## 📋 热点数据结构

### 完整字段说明

```python
{
    "title": "热点标题",
    "content": "内容摘要",
    "url": "原文链接",
    "source_name": "来源名称",
    "crawl_time": datetime.now(),  # 采集时间
    "publish_time": None,  # 发布时间 (可选)
    "heat_score": 75.0,  # 热度值 (自动计算)
    "heat_level": "hot",  # 热度等级 (自动计算)
    "category": "科技",  # 分类
    "tags": ["AI", "科技"],  # 标签列表
    "keywords": ["AI", "科技", "创新"]  # 关键词列表
}
```

### 热度评分规则

| 因素 | 权重 | 说明 |
|------|------|------|
| 基础分 | 50 分 | 所有热点起始分 |
| 标题长度 | ±10 分 | 20-40 字最佳 |
| 来源可信度 | ±20 分 | 官方媒体>自媒体 |
| 内容长度 | ±10 分 | 100-500 字最佳 |
| 热点关键词 | +5 分 | 包含"突发""重磅"等 |

### 热度等级

| 等级 | 分数范围 | 说明 |
|------|---------|------|
| explosive | 90-100 | 爆款 |
| hot | 75-89 | 热门 |
| warm | 60-74 | 温热点 |
| normal | 0-59 | 普通 |

---

## 🔧 高级功能

### 1. 批量添加热点

```python
topics = [
    {
        "title": "热点 1",
        "source_name": "微博热搜",
        "category": "娱乐"
    },
    {
        "title": "热点 2",
        "source_name": "知乎热榜",
        "category": "科技"
    }
]

result = db.batch_add_topics(topics)
print(f"成功：{result['added']}, 跳过：{result['skipped']}")
```

### 2. 条件查询

```python
# 按分类查询
edu_topics = db.get_hot_topics(category="教育", limit=10)

# 按热度等级查询
hot_topics = db.get_hot_topics(heat_level="hot", limit=10)

# 按来源查询
weibo_topics = db.get_hot_topics(source_name="微博热搜", limit=10)

# 按时间范围查询
recent_topics = db.get_hot_topics(time_range_hours=24, limit=10)
```

### 3. 获取关键词

```python
keywords = db.get_keywords_by_topic(topic_id=1)
for kw in keywords:
    print(f"{kw['keyword']} - 权重：{kw['weight']}")
```

### 4. 数据清理

```python
# 清理 30 天前的旧数据
deleted = db.cleanup_old_data(days_to_keep=30)
print(f"删除 {deleted} 条旧数据")
```

---

## 📊 统计分析

### 获取统计报告

```python
stats = db.get_statistics(days=7)

# 总体统计
print(f"总热点数：{stats['overall']['total_count']}")
print(f"平均热度：{stats['overall']['avg_heat']}")
print(f"唯一热点：{stats['overall']['unique_count']}")

# 按分类统计
for cat in stats['by_category']:
    print(f"{cat['category']}: {cat['count']}条")

# 按来源统计
for src in stats['by_source']:
    print(f"{src['name']}: {src['count']}条")

# 热词统计
for kw in stats['hot_keywords'][:20]:
    print(f"{kw['keyword']}: {kw['count']}次")
```

### 统计维度

- **总体统计**: 总数、平均热度、唯一热点数
- **分类统计**: 按教育/科技/财经等分类
- **来源统计**: 按微博/知乎/澎湃新闻等来源
- **热词统计**: 出现频率最高的关键词

---

## 🔄 复用已有采集器

采集器 V2 复用了以下已有模块：

| 采集器 | 路径 | 状态 |
|--------|------|------|
| DailyHotApi | `sources/dailyhot_collector.py` | ✅ 已集成 |
| RSSHub | `sources/extended_collectors_v2.py` | ✅ 已集成 |
| 视频采集 | `sources/video_collector.py` | ✅ 已集成 |
| 内容采集 | `sources/content_collector.py` | ⏳ 待集成 |
| 垂直领域 | `sources/vertical_collector.py` | ⏳ 待集成 |

### 集成方式

```python
# 采集器 V2 自动调用已有采集器
from core.hot_collector_v2 import HotNewsCollectorV2

collector = HotNewsCollectorV2()

# 自动调用 DailyHotApi、RSSHub、视频采集器
report = collector.collect_all()

# 结果自动标准化并存储到数据库
```

---

## ⚠️ 注意事项

1. **数据库路径**: 默认 `data/hot_news.db`，可自定义
2. **去重时间窗口**: 默认 24 小时内相同标题/关键词视为重复
3. **热度计算**: 自动计算，也可手动指定
4. **并发安全**: SQLite 支持有限并发，高并发建议用 MySQL
5. **数据清理**: 建议定期清理 30 天前旧数据

---

## 📝 示例脚本

### 定时采集脚本

```python
#!/usr/bin/env python3
"""定时采集热点数据"""

from core.hot_collector_v2 import HotNewsCollectorV2
from datetime import datetime

def main():
    collector = HotNewsCollectorV2()
    
    print(f"[{datetime.now()}] 开始采集...")
    report = collector.collect_all()
    print(f"采集完成：{report['total_collected']}条")
    
    collector.close()

if __name__ == "__main__":
    main()
```

### 导出热点报告

```python
#!/usr/bin/env python3
"""导出热点统计报告"""

from core.hot_database import HotNewsDatabase
import json

db = HotNewsDatabase()

# 获取统计
stats = db.get_statistics(days=7)

# 导出为 JSON
with open('hot_news_report.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print("报告已导出到 hot_news_report.json")

db.close()
```

---

*最后更新：2026-03-01*
