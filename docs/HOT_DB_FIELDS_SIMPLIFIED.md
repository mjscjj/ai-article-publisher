# 🔥 热点数据库字段精简

**更新时间**: 2026-03-01
**变更**: 删除 `keyword_hash` 和 `is_unique` 字段

---

## 📊 字段变更

### 删除的字段

| 字段 | 类型 | 说明 | 删除原因 |
|------|------|------|---------|
| `keyword_hash` | VARCHAR(64) | 关键词哈希 (去重用) | 不需要自动去重 |
| `is_unique` | TINYINT | 是否唯一标记 | 冗余字段 |

### 保留的字段 (13 个)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | INT | ✅ | 主键 |
| `title` | VARCHAR(500) | ✅ | 热点标题 |
| `content` | TEXT | ❌ | 内容摘要 |
| `url` | VARCHAR(1000) | ❌ | 原文链接 |
| `source_id` | INT | ❌ | 来源 ID |
| `crawl_date` | DATE | ✅ | 采集日期 (按天索引) |
| `crawl_time` | DATETIME | ✅ | 采集时间 |
| `publish_time` | DATETIME | ❌ | 发布时间 |
| `heat_score` | DECIMAL(5,2) | ❌ | 热度值 |
| `heat_level` | VARCHAR(20) | ❌ | 热度等级 |
| `category` | VARCHAR(50) | ❌ | 分类 |
| `tags` | JSON | ❌ | 标签 |
| `created_at` | DATETIME | ✅ | 创建时间 |
| `updated_at` | DATETIME | ✅ | 更新时间 |

---

## 🔧 数据库变更

### SQL 操作

```sql
-- 删除字段
ALTER TABLE hot_topics 
DROP COLUMN keyword_hash;

ALTER TABLE hot_topics 
DROP COLUMN is_unique;

-- 删除索引
ALTER TABLE hot_topics 
DROP INDEX idx_hash;
```

### 表结构

```sql
CREATE TABLE hot_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    url VARCHAR(1000),
    source_id INT,
    crawl_date DATE NOT NULL,
    crawl_time DATETIME NOT NULL,
    publish_time DATETIME,
    heat_score DECIMAL(5,2) DEFAULT 0,
    heat_level VARCHAR(20) DEFAULT 'normal',
    category VARCHAR(50),
    tags JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_crawl_date (crawl_date),
    INDEX idx_crawl_time (crawl_time),
    INDEX idx_heat (heat_score),
    INDEX idx_category (category)
);
```

---

## 📝 代码变更

### 删除的方法

```python
# 已删除
def _calculate_keyword_hash(self, title: str, keywords: List[str] = None) -> str:
    """计算关键词哈希"""
    ...

def _check_duplicate(self, keyword_hash: str, title: str, time_window_hours: int = 24) -> bool:
    """检查是否重复"""
    ...
```

### 修改的方法

```python
# 简化后的 add_hot_topic
def add_hot_topic(self, title: str, content: str = None, ...) -> int:
    # 1. 获取或创建来源
    source_id = self._get_or_create_source(source_name)
    
    # 2. 设置默认值
    if crawl_time is None:
        crawl_time = datetime.now()
    if heat_score is None:
        heat_score = self._calculate_heat_score(title, content, source_name)
    
    # 3. 插入数据库 (去掉 keyword_hash)
    self._execute('''
        INSERT INTO hot_topics 
        (title, content, url, source_id, crawl_date, crawl_time, publish_time, 
         heat_score, heat_level, category, tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (title, content, url, source_id, crawl_date, crawl_time, publish_time,
          heat_score, self._get_heat_level(heat_score), category, tags))
    
    topic_id = self._fetch_one('SELECT LAST_INSERT_ID() as id')['id']
    
    # 4. 添加关键词
    if keywords:
        self._add_keywords(topic_id, keywords)
    
    return topic_id
```

---

## ✅ 测试结果

```
✅ 字段删除成功
✅ 数据库连接正常
✅ 添加热点正常
✅ 查询热点正常
✅ 按天查询正常
```

### 测试数据

```
总热点数：4 条
日期范围：2026-02-27 至 2026-03-01
分类：科技 (2), 教育 (1), 综合 (1)
来源：微博热搜，澎湃新闻，知乎热榜
```

---

## 🎯 优化效果

### 存储优化

| 项目 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| 字段数 | 15 个 | 13 个 | -13% |
| 每行字节 | ~850 字节 | ~780 字节 | -8% |
| 索引数 | 5 个 | 4 个 | -20% |

### 性能影响

- **插入速度**: 略微提升 (少计算哈希)
- **查询速度**: 无明显影响
- **去重功能**: 移除 (不再自动去重)

---

## ⚠️ 注意事项

### 1. 去重功能

**原功能**: 基于 `keyword_hash` 自动去重

**现状**: 不再自动去重，需要在应用层处理

**解决方案**:
```python
# 应用层去重 (如果需要)
def is_duplicate(title: str, hours: int = 24) -> bool:
    threshold = datetime.now() - timedelta(hours=hours)
    result = db._fetch_one('''
        SELECT id FROM hot_topics 
        WHERE title LIKE %s AND crawl_time > %s
    ''', (f'%{title[:30]}%', threshold))
    return result is not None
```

### 2. 数据迁移

如果是现有数据库，执行:

```sql
ALTER TABLE hot_topics 
DROP COLUMN keyword_hash,
DROP COLUMN is_unique;
```

### 3. 索引优化

删除了 `idx_hash` 索引，保留:
- `idx_crawl_date` - 按天查询
- `idx_crawl_time` - 时间排序
- `idx_heat` - 热度排序
- `idx_category` - 分类筛选

---

## 📊 最终字段说明

### 核心字段 (必需)

| 字段 | 用途 |
|------|------|
| `title` | 热点标题 |
| `crawl_date` | 采集日期 (按天隔离) |
| `crawl_time` | 采集时间 |

### 内容字段

| 字段 | 用途 |
|------|------|
| `content` | 内容摘要 |
| `url` | 原文链接 |
| `tags` | 标签 (JSON) |

### 分类字段

| 字段 | 用途 |
|------|------|
| `category` | 主分类 (教育/科技/财经...) |
| `source_id` | 来源 ID |

### 热度字段

| 字段 | 用途 |
|------|------|
| `heat_score` | 热度值 (0-100) |
| `heat_level` | 热度等级 (explosive/hot/warm/normal) |

### 时间戳

| 字段 | 用途 |
|------|------|
| `created_at` | 创建时间 (自动) |
| `updated_at` | 更新时间 (自动) |
| `publish_time` | 原文发布时间 (可选) |

---

## 🚀 使用示例

### Python

```python
from core.hot_database_mysql import HotNewsDatabaseMySQL

db = HotNewsDatabaseMySQL()

# 添加热点
db.add_hot_topic(
    title='教育部发布 AI+ 教育指导意见',
    content='教育部近日发布...',
    url='https://example.com/news/123',
    source_name='澎湃新闻',
    category='教育',
    tags=['AI', '教育', '政策']
)

# 按天查询
today = db.get_hot_topics(crawl_date='today')

# 统计
stats = db.get_statistics(days=7)

db.close()
```

### API

```bash
# 查询今天热点
curl "http://43.134.234.4:8080/api/topics?date=today"

# 获取统计
curl "http://43.134.234.4:8080/api/statistics"

# 获取日期列表
curl "http://43.134.234.4:8080/api/dates?limit=30"
```

---

*最后更新：2026-03-01*
*版本：2.0 (精简版)*
