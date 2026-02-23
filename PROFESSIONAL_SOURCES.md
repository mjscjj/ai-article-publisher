# AI Article Publisher - 专业数据源模块

> 扩展心理学、教育、学习方法等专业领域的数据采集能力

---

## 📁 模块结构

```
scripts/content/custom_sources/
├── professional_sources.py  # 专业数据源（知乎、B站、豆瓣等）
└── search_api.py            # 搜索API集成（DuckDuckGo、Wikipedia、Semantic Scholar）
```

---

## 🔧 使用方法

### 1. 专业数据源（professional_sources.py）

```bash
# 心理学领域综合搜索
python3 professional_sources.py --source psychology --limit 20

# 青少年心理健康
python3 professional_sources.py --source teenager --limit 20

# 学习方法
python3 professional_sources.py --source learning --limit 20

# 自定义搜索
python3 professional_sources.py --source zhihu_search --query "心理学" --limit 10
python3 professional_sources.py --source bilibili --query "学习方法" --limit 10

# 查看所有数据源
python3 professional_sources.py --list
```

**支持的数据源**:
| 数据源 | 调用名称 | 说明 |
|--------|----------|------|
| 心理学领域 | `psychology` | 综合搜索 |
| 青少年心理健康 | `teenager` | 综合搜索 |
| 学习方法 | `learning` | 综合搜索 |
| 知乎话题 | `zhihu_topic` | 需要登录 |
| 知乎搜索 | `zhihu_search` | 需要 --query |
| B站视频 | `bilibili` | 需要 --query |
| 微信公众号 | `wechat` | 需要 --query |
| 豆瓣小组 | `douban` | 心理学小组 |
| 果壳网 | `guokr` | 科学文章 |

---

### 2. 搜索API集成（search_api.py）

```bash
# 学术论文搜索（推荐，免费）
python3 search_api.py --engine scholar --query "psychology learning" --limit 10

# Wikipedia搜索
python3 search_api.py --engine wikipedia --query "心理学" --limit 10

# DuckDuckGo搜索
python3 search_api.py --engine duckduckgo --query "learning methods" --limit 10

# 综合搜索
python3 search_api.py --engine all --query "psychology" --limit 10

# 查看所有引擎
python3 search_api.py --list
```

**支持的搜索引擎**:

| 引擎 | 调用名称 | 免费 | 说明 |
|------|----------|------|------|
| Semantic Scholar | `scholar` | ✅ | 学术论文搜索 |
| Wikipedia | `wikipedia` | ✅ | 百科搜索 |
| DuckDuckGo | `duckduckgo` | ✅ | 即时答案 |
| 综合搜索 | `all` | ✅ | 以上全部 |
| Google (SerpAPI) | `google` | ❌ | 需要 API Key |
| Bing | `bing` | ❌ | 需要 API Key |

---

## ✅ 测试结果

### Semantic Scholar 学术搜索（成功）

**搜索: "psychology learning methods teenagers"**

```
1. Metaverse: Innovation in Teaching Methods for Teenagers (2023)
2. Effects of ICT use on self-regulated learning (2025)
3. Parental Psychological Control on Students' Learning Motivation (2025)
4. Influence of Social Intelligence of Teachers on Learning (2023)
5. Parenting styles and adolescents' educational motivation (2024)
6. Single Mother Parenting on Adolescent Learning Outcomes (2024)
7. Children with ADHD and Anxiety Disorders (2023)
8. Fear of Missing Out in Adolescents during Covid-19 (2022)
```

---

## ⚠️ 注意事项

### API 限制

| 平台 | 状态 | 原因 |
|------|------|------|
| 知乎 API | ❌ 403 Forbidden | 需要登录/反爬虫 |
| B站 API | ❌ 412 Precondition | 需要特定请求头 |
| Wikipedia | ⚠️ 限流 | 请求频率限制 |
| Semantic Scholar | ⚠️ 429 限流 | 免费API有请求限制 |
| DuckDuckGo | ⚠️ 空结果 | 需要更具体查询 |

### 解决方案

1. **添加请求头/Token** - 模拟浏览器行为
2. **添加延时** - 避免触发限流
3. **使用代理** - 分散请求
4. **使用官方API Key** - 获取更高配额

---

## 🚀 推荐配置

**最佳免费组合**:
```
大众热点: wemp-operator (fetch_news.py)
专业内容: Semantic Scholar (学术论文)
```

**使用示例**:
```bash
# 1. 采集大众热点
python3 ../fetch_news.py --source weibo,zhihu --limit 10

# 2. 采集专业内容
python3 search_api.py --engine scholar --query "青少年心理健康" --limit 10
```

---

## 📊 数据源对比

| 数据源类型 | 热点采集 | 专业内容 | 学术论文 |
|------------|----------|----------|----------|
| wemp-operator | ✅ 优秀 | ❌ 不支持 | ❌ 不支持 |
| Semantic Scholar | ❌ 不支持 | ✅ 优秀 | ✅ 优秀 |
| 知乎/B站 | ⚠️ 受限 | ⚠️ 受限 | ❌ 不支持 |

---

*最后更新: 2026-02-21*