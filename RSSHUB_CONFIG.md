# RSSHub 热门数据源配置

> RSSHub 本地实例: http://localhost:1200

---

## 📊 热门数据源（已验证）

### 🔥 国内热点

| 数据源 | RSS 路径 | 说明 |
|--------|----------|------|
| **微博热搜** | `/weibo/search/hot/1` | 实时热搜榜 |
| **微博 - 关键词** | `/weibo/search/{keyword}/1` | 按关键词搜索 |
| **知乎热榜** | `/zhihu/hotlist` | 全站热榜 |
| **知乎 - 话题** | `/zhihu/topic/{topic_id}/hot` | 话题热榜 |
| **B站热门** | `/bilibili/ranking/0/3/1` | 综合热门 |
| **B站 - UP主** | `/bilibili/user/dynamic/{uid}` | UP主动态 |
| **抖音热点** | `/douyin/trending` | 热点榜 |
| **今日头条** | `/toutiao/hot` | 热榜 |
| **小红书** | `/xiaohongshu/discover` | 发现页 |
| **百度热搜** | `/baidu/topwords/realtime` | 实时热点 |

### 💼 科技财经

| 数据源 | RSS 路径 | 说明 |
|--------|----------|------|
| **36氪** | `/36kr/newsflashes` | 快讯 |
| **36氪热门** | `/36kr/hot` | 热门文章 |
| **少数派** | `/sspai/index` | 首页文章 |
| **IT之家** | `/ithome/ranking/7days` | 7天热榜 |
| **掘金热门** | `/juejin/trending/all/monthly` | 月榜 |
| **虎嗅** | `/huxiu/article` | 文章 |
| **华尔街见闻** | `/wallstreetcn/news/global` | 全球新闻 |

### 🌍 国际热点

| 数据源 | RSS 路径 | 说明 |
|--------|----------|------|
| **Hacker News** | `/hackernews/best` | 最佳 |
| **Product Hunt** | `/producthunt/today` | 今日产品 |
| **GitHub Trending** | `/github/trending/daily` | 日榜 |
| **Reddit** | `/reddit/subreddit/{name}/hot` | 子版块热门 |
| **Twitter** | `/twitter/user/{username}` | 用户推文 |

### 📱 微信公众号

| 数据源 | RSS 路径 | 说明 |
|--------|----------|------|
| **公众号文章** | `/wechat/mp/msgalbum/{biz}` | 公众号专辑 |
| **微信读书** | `/weread/category/{category}` | 分类书籍 |

### 🎓 学习教育

| 数据源 | RSS 路径 | 说明 |
|--------|----------|------|
| **知乎心理学话题** | `/zhihu/topic/19551647/hot` | 心理学热榜 |
| **知乎教育话题** | `/zhihu/topic/19550429/hot` | 教育热榜 |
| **知乎学习方法** | `/zhihu/topic/19552338/hot` | 学习方法 |

---

## 🔗 使用示例

### 1. 直接访问 RSS

```bash
# 微博热搜
curl "http://localhost:1200/weibo/search/hot/1"

# 知乎热榜
curl "http://localhost:1200/zhihu/hotlist"

# 36氪快讯
curl "http://localhost:1200/36kr/newsflashes"

# 心理学话题
curl "http://localhost:1200/zhihu/topic/19551647/hot"
```

### 2. 在 rss-skill 中使用

```bash
cd ~/.openclaw/workspace/skills/rss-skill

# 添加微博热搜
node cli.js add "http://localhost:1200/weibo/search/hot/1" "微博热搜"

# 添加知乎热榜
node cli.js add "http://localhost:1200/zhihu/hotlist" "知乎热榜"

# 添加心理学话题
node cli.js add "http://localhost:1200/zhihu/topic/19551647/hot" "知乎心理学"

# 读取内容
node cli.js read "微博热搜" 10
```

### 3. 在 universal-feeds 中使用

编辑 `~/.openclaw/workspace/skills/universal-feeds/config/feeds.yaml`:

```yaml
sources:
  - name: 微博热搜
    url: http://localhost:1200/weibo/search/hot/1
    type: rss
    weight: 1.2
    tags: [cn, hot, weibo]

  - name: 知乎热榜
    url: http://localhost:1200/zhihu/hotlist
    type: rss
    weight: 1.1
    tags: [cn, hot, zhihu]

  - name: 心理学话题
    url: http://localhost:1200/zhihu/topic/19551647/hot
    type: rss
    weight: 1.0
    tags: [psychology, learning]

  - name: 36氪快讯
    url: http://localhost:1200/36kr/newsflashes
    type: rss
    weight: 1.0
    tags: [tech, finance]

  - name: Hacker News
    url: http://localhost:1200/hackernews/best
    type: rss
    weight: 1.0
    tags: [tech, en]
```

---

## 🚀 快速测试脚本

```bash
#!/bin/bash
# 测试所有热门数据源

RSSHUB="http://localhost:1200"

echo "=== 微博热搜 ==="
curl -s "$RSSHUB/weibo/search/hot/1" | grep -o '<title>.*</title>' | head -5

echo ""
echo "=== 知乎热榜 ==="
curl -s "$RSSHUB/zhihu/hotlist" | grep -o '<title>.*</title>' | head -5

echo ""
echo "=== B站热门 ==="
curl -s "$RSSHUB/bilibili/ranking/0/3/1" | grep -o '<title>.*</title>' | head -5

echo ""
echo "=== 36氪快讯 ==="
curl -s "$RSSHUB/36kr/newsflashes" | grep -o '<title>.*</title>' | head -5

echo ""
echo "=== Hacker News ==="
curl -s "$RSSHUB/hackernews/best" | grep -o '<title>.*</title>' | head -5
```

---

## 📊 数据源统计

| 分类 | 数量 |
|------|------|
| 国内热点 | 10 |
| 科技财经 | 7 |
| 国际热点 | 5 |
| 微信公众号 | 2 |
| 学习教育 | 3 |
| **总计** | **27+** |

---

*最后更新: 2026-02-21*
