# 数据源扩展方案

> 创建时间: 2026-02-22
> 状态: 调研中

---

## 🎯 目标

扩展热点数据源，覆盖：
- 热词热榜
- 视频平台
- 图文平台
- 社交媒体
- 垂直领域

---

## 📊 当前状态

| 指标 | 当前 | 目标 |
|------|------|------|
| 数据源数量 | 29 | 100+ |
| 数据类型 | 文本 | 文本+视频+图文 |
| 更新频率 | 每3小时 | 实时+定时 |
| 国际来源 | 少量 | 50%+ |

---

## 🔍 调研发现

### 1. 今日热榜 API (DailyHotApi)

**GitHub**: https://github.com/imsyy/DailyHotApi

**特点**:
- 免费 API
- 聚合多平台热搜
- 包含微博、知乎、抖音、B站、今日头条等

**数据源**:
- 微博热搜 ✅
- 知乎热榜 ✅
- 抖音热点 ✅
- B站热门 ✅
- 今日头条 ✅
- 百度贴吧 ✅
- 网易新闻 ✅
- 腾讯新闻 ✅
- 澎湃新闻 ✅

**接口示例**:
```
https://api.v3.iowiki.cn/api/weibo
https://api.v3.iowiki.cn/api/zhihu
https://api.v3.iowiki.cn/api/douyin
```

---

### 2. RSSHub (已部署)

**GitHub**: https://github.com/DIYgod/RSSHub

**特点**:
- 5000+ 数据源
- 开源免费
- 本地已部署 (localhost:1200)

**当前已用路由**:
- 微博热搜 ✅
- 知乎热榜 ✅
- Hacker News ✅
- GitHub Trending ✅
- V2EX ✅
- 36氪 ✅
- 少数派 ✅
- IT之家 ✅
- 掘金 ✅

**可扩展路由**:
- 抖音热门 `/douyin/hot`
- 快手热门 `/kuaishou/hot`
- 小红书热门 `/xiaohongshu/hot`
- YouTube热门 `/youtube/trending`
- Twitter热点 `/twitter/trends`
- Instagram热门 `/instagram/popular`
- TikTok热门 `/tiktok/trending`
- ProductHunt `/producthunt/today`

---

### 3. 热词 API

**百度热榜**:
```
https://top.baidu.com/board?tab=realtime
```

**微博热搜** (已有):
```
http://localhost:1200/weibo/hot
```

**知乎热榜** (已有):
```
http://localhost:1200/zhihu/hot
```

**抖音热点**:
```
http://localhost:1200/douyin/hot
```

---

### 4. 视频平台

| 平台 | 数据源 | RSSHub路由 | 状态 |
|------|--------|------------|------|
| B站热门 | RSSHub | `/bilibili/ranking/0/0/0/0/0` | 待接入 |
| 抖音热点 | RSSHub | `/douyin/hot` | 待接入 |
| 快手热门 | RSSHub | `/kuaishou/hot` | 待接入 |
| YouTube热门 | RSSHub | `/youtube/trending` | 待接入 |
| TikTok热门 | RSSHub | `/tiktok/trending` | 待接入 |
| 西瓜视频 | RSSHub | `/ixigua/hot` | 待接入 |

---

### 5. 图文平台

| 平台 | 数据源 | 方案 | 状态 |
|------|--------|------|------|
| 小红书 | RSSHub | `/xiaohongshu/hot` | 待接入 |
| 今日头条 | DailyHotApi | API | 待接入 |
| 百家号 | 爬虫 | 需开发 | 待开发 |
| 微信公众号 | wemp-operator | 已有 | ✅ 已接入 |

---

### 6. 国际热点

| 平台 | 数据源 | RSSHub路由 | 状态 |
|------|--------|------------|------|
| Twitter Trends | RSSHub | `/twitter/trends` | 待接入 |
| Reddit | RSSHub | `/reddit/hot` | 待接入 |
| ProductHunt | RSSHub | `/producthunt/today` | 待接入 |
| Instagram | RSSHub | `/instagram/popular` | 待接入 |
| Pinterest | RSSHub | `/pinterest/search` | 待接入 |

---

## 🚀 实施计划

### Phase 1: RSSHub 扩展 (1天)

添加以下 RSSHub 路由:

```python
# 新增路由
NEW_RSSHUB_SOURCES = {
    # 视频平台
    "bilibili_hot": {
        "name": "B站热门",
        "route": "/bilibili/ranking/0/0/0/0/0",
        "category": "视频"
    },
    "douyin_hot": {
        "name": "抖音热点",
        "route": "/douyin/hot",
        "category": "视频"
    },
    "kuaishou_hot": {
        "name": "快手热门",
        "route": "/kuaishou/hot",
        "category": "视频"
    },
    "youtube_trending": {
        "name": "YouTube热门",
        "route": "/youtube/trending",
        "category": "视频"
    },
    
    # 图文平台
    "xiaohongshu_hot": {
        "name": "小红书热门",
        "route": "/xiaohongshu/hot",
        "category": "图文"
    },
    
    # 国际热点
    "twitter_trends": {
        "name": "Twitter热点",
        "route": "/twitter/trends",
        "category": "国际"
    },
    "reddit_hot": {
        "name": "Reddit热门",
        "route": "/reddit/hot",
        "category": "国际"
    },
    "producthunt_today": {
        "name": "ProductHunt今日",
        "route": "/producthunt/today",
        "category": "科技"
    }
}
```

### Phase 2: DailyHotApi 集成 (1天)

```python
# DailyHotApi 数据源
DAILYHOT_SOURCES = {
    "weibo": "https://api.v3.iowiki.cn/api/weibo",
    "zhihu": "https://api.v3.iowiki.cn/api/zhihu",
    "douyin": "https://api.v3.iowiki.cn/api/douyin",
    "bilibili": "https://api.v3.iowiki.cn/api/bilibili",
    "toutiao": "https://api.v3.iowiki.cn/api/toutiao",
    "baidu": "https://api.v3.iowiki.cn/api/baidu",
    "zhihu_daily": "https://api.v3.iowiki.cn/api/zhihu-daily",
    "weixin": "https://api.v3.iowiki.cn/api/weixin",
    "baidu_tieba": "https://api.v3.iowiki.cn/api/baidu-tieba",
    "netease_news": "https://api.v3.iowiki.cn/api/netease-news",
    "tencent_news": "https://api.v3.iowiki.cn/api/tencent-news",
}
```

### Phase 3: 热词系统 (1天)

```python
# 热词数据源
HOTWORD_SOURCES = {
    "baidu_hot": {
        "name": "百度热榜",
        "url": "https://top.baidu.com/board?tab=realtime",
        "parser": "baidu_parser"
    },
    "weibo_hot": {
        "name": "微博热搜",
        "url": "http://localhost:1200/weibo/hot",
        "parser": "rsshub_parser"
    },
    "zhihu_hot": {
        "name": "知乎热榜",
        "url": "http://localhost:1200/zhihu/hot",
        "parser": "rsshub_parser"
    }
}
```

### Phase 4: 视频热门 (1天)

```python
# 视频热门采集
VIDEO_SOURCES = {
    "bilibili": {
        "name": "B站热门",
        "routes": [
            "/bilibili/ranking/0/0/0/0/0",  # 综合热门
            "/bilibili/ranking/1/0/0/0/0",  # 动画热门
            "/bilibili/ranking/3/0/0/0/0",  # 音乐热门
            "/bilibili/ranking/4/0/0/0/0",  # 游戏热门
        ]
    },
    "douyin": {
        "name": "抖音热点",
        "route": "/douyin/hot"
    },
    "youtube": {
        "name": "YouTube热门",
        "route": "/youtube/trending"
    }
}
```

---

## 📁 文件结构

```
ai-article-publisher/
├── hotnews_storage.py          # 现有存储系统
├── extended_sources.py         # 现有扩展源
├── sources/                    # 新增目录
│   ├── __init__.py
│   ├── rsshub_extended.py      # RSSHub 扩展源
│   ├── dailyhot_api.py         # DailyHotApi 数据源
│   ├── hotword_collector.py    # 热词采集器
│   ├── video_collector.py      # 视频热门采集器
│   └── social_collector.py     # 社交媒体采集器
└── config/
    └── sources_extended.json   # 扩展数据源配置
```

---

## 📊 预期效果

| 指标 | 当前 | 扩展后 |
|------|------|--------|
| 数据源数量 | 29 | 100+ |
| 视频数据源 | 0 | 20+ |
| 国际数据源 | 16 | 50+ |
| 热词数据源 | 0 | 10+ |
| 更新频率 | 每3小时 | 实时+定时 |
| 日均数据量 | 1000+ | 5000+ |

---

## ⚠️ 注意事项

1. **频率限制**: RSSHub 有请求频率限制，需要控制并发
2. **IP白名单**: 部分平台需要 IP 白名单
3. **数据去重**: 多源采集需要去重逻辑
4. **存储优化**: 数据量增大需要优化存储

---

*最后更新: 2026-02-22 16:45*