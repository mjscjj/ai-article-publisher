# AI Article Publisher - 热点采集能力扩展

> 新增 OpenClaw Skills 和数据源

---

## 🎉 新增 Skills（已安装）

### 1. universal-feeds ⭐⭐⭐⭐⭐

**仓库**: https://github.com/ripplek/universal-feeds  
**Stars**: 2  
**更新**: 14 days ago

**通用 Feed 聚合框架，支持：**

| 平台 | 状态 | 说明 |
|------|------|------|
| X (Twitter) | ✅ | 需要 Chrome profile |
| RSS | ✅ | 任意 RSS 源 |
| V2EX | ✅ | 技术社区 |
| YouTube | ✅ | 视频内容 |
| Weibo 热搜 | ✅ | 微博热点 |
| 微信公众号 | ✅ | 公众号文章 |
| TikTok | 🔲 计划中 | - |

**使用方式**:
```bash
cd ~/.openclaw/workspace/skills/universal-feeds

# 运行 demo
node bin/digest --config config/feeds.demo.yaml --date today

# 自定义配置
cp config/feeds.example.yaml config/feeds.yaml
# 编辑 feeds.yaml 添加你的订阅源
node bin/digest --config config/feeds.yaml --date today
```

**输出**:
- `out/items-YYYY-MM-DD.jsonl` - 原始数据
- `out/digest-YYYY-MM-DD.md` - 每日摘要

---

### 2. rss-skill

**仓库**: https://github.com/sincere-arjun/rss-skill  
**Stars**: 0  
**更新**: 17 days ago

**RSS 阅读器，功能：**
- ✅ 添加/管理多个 RSS 源
- ✅ 读取订阅内容
- ✅ 关键词搜索
- ✅ JSON 输出

**使用方式**:
```bash
cd ~/.openclaw/workspace/skills/rss-skill

# 添加订阅
node cli.js add https://news.ycombinator.com/rss "Hacker News"

# 读取内容
node cli.js read "Hacker News" 10

# 搜索
node cli.js search "AI"
```

---

## 📊 完整热点采集能力

### 已安装组件汇总

| 组件 | 类型 | 数据源 | 状态 |
|------|------|--------|------|
| **wemp-operator** | Skill | 微博/知乎/B站等 20+ 源 | ✅ 已安装 |
| **universal-feeds** | Skill | X/RSS/YouTube/微信等 | ✅ 已安装 |
| **rss-skill** | Skill | 任意 RSS 源 | ✅ 已安装 |
| **wechat-article-skill** | Skill | 写作+发布 | ✅ 已安装 |
| **professional_sources.py** | Script | 学术论文搜索 | ✅ 已安装 |
| **search_api.py** | Script | 搜索引擎 | ✅ 已安装 |

### 数据源覆盖

```
┌─────────────────────────────────────────────────────────────┐
│                    热点采集能力矩阵                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  【国内热点】                                                │
│  ✅ 微博热搜      - wemp-operator                          │
│  ✅ 知乎热榜      - wemp-operator (受限)                   │
│  ✅ B站热搜       - wemp-operator                          │
│  ✅ 今日头条      - wemp-operator (受限)                   │
│  ✅ 百度热搜      - wemp-operator (受限)                   │
│  ✅ 36氪         - wemp-operator                          │
│  ✅ 微信公众号    - universal-feeds                        │
│                                                             │
│  【国际热点】                                                │
│  ✅ Hacker News   - wemp-operator + rss-skill             │
│  ✅ GitHub Trend  - wemp-operator                          │
│  ✅ V2EX         - wemp-operator + universal-feeds        │
│  ✅ YouTube       - universal-feeds                        │
│  ✅ X (Twitter)   - universal-feeds                        │
│  ✅ Product Hunt  - wemp-operator                          │
│                                                             │
│  【任意 RSS】                                               │
│  ✅ RSSHub       - 42k stars，支持 5000+ 网站              │
│  ✅ rss-skill    - 任意 RSS 订阅                           │
│                                                             │
│  【学术搜索】                                                │
│  ✅ Semantic Scholar - 学术论文搜索                        │
│  ✅ Wikipedia       - 百科搜索                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔥 RSSHub（推荐）

**仓库**: https://github.com/DIYgod/RSSHub  
**Stars**: 42k ⭐⭐⭐⭐⭐

**世界最大的 RSS 网络，5000+ 全球实例！**

支持的数据源（部分）：
- 微博、知乎、B站、抖音、小红书
- 微信公众号、今日头条、百家号
- Twitter、Instagram、YouTube
- GitHub、ProductHunt、Hacker News
- 几乎所有主流网站...

**使用方式**:
```bash
# 使用公共实例
https://rsshub.app/weibo/search/心理学

# Docker 自部署
docker pull diygod/rsshub
docker run -d -p 1200:1200 diygod/rsshub
```

---

## 📝 测试结果

### universal-feeds 今日摘要

```
✅ 机器之心 - AI 相关文章 (10篇)
✅ OpenAI News - First Proof submissions
✅ Claude Opus 4.6 发布
✅ YouTube - OpenAI Codex 视频
```

### rss-skill 测试

```json
{
  "title": "Hacker News",
  "items": [
    {"title": "Keep Android Open"},
    {"title": "Turn Dependabot Off"},
    {"title": "CERN rebuilt the original browser"},
    {"title": "I found a Vulnerability. They found a Lawyer"},
    {"title": "Facebook is cooked"}
  ]
}
```

---

## 🚀 推荐配置

**最佳热点采集组合：**

```
wemp-operator (国内热点)
    +
universal-feeds (国际热点 + 微信公众号)
    +
rss-skill (任意 RSS 订阅)
    +
RSSHub (5000+ 数据源)
```

---

## 📈 能力提升对比

| 指标 | 之前 | 现在 |
|------|------|------|
| 数据源数量 | 5 个 | **50+ 个** |
| 国内热点 | 部分 | **全覆盖** |
| 微信公众号 | ❌ | ✅ |
| YouTube | ❌ | ✅ |
| Twitter/X | ❌ | ✅ |
| 任意 RSS | ❌ | ✅ |
| 学术搜索 | ❌ | ✅ |

---

*最后更新: 2026-02-21*