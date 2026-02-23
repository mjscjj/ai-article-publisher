# AI Article Publisher 使用指南

> 完整工作流：热点采集 → 智能选题 → 内容创作 → 发布

---

## 🚀 快速开始

### 1. 采集热点并推荐选题

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher

# 基础用法
python3 workflow.py --sources "weibo,hackernews,github" --keywords "AI,学习,心理学" --top 5

# 完整参数
python3 workflow.py \
  --sources "weibo,zhihu,hackernews,github,v2ex" \
  --keywords "AI,心理学,教育,学习" \
  --top 10 \
  --output report
```

### 2. 只采集教育热点

```bash
python3 collect_education.py --type all --limit 10
```

### 3. 选题评分

```bash
# 对已有数据进行评分
python3 topic_scorer.py --input output/topics_xxx.json --keywords "AI,心理学"
```

---

## 📊 数据源列表

### 已验证可用

| 数据源 | 类型 | RSSHub路由 |
|--------|------|------------|
| 微博热搜 | 综合 | `/weibo/search/hot` |
| Hacker News | 技术 | `/hackernews/best` |
| GitHub Trending | 技术 | `/github/trending/daily` |
| V2EX | 技术 | `/v2ex/topics/hot` |
| 少数派 | 科技 | `/sspai/index` |
| IT之家 | 科技 | `/ithome/ranking/7days` |
| 掘金 | 技术 | `/juejin/trending/all/monthly` |
| 豆瓣心理学小组 | 心理 | `/douban/group/psychology` |

### 需要Puppeteer

| 数据源 | 状态 |
|--------|------|
| 知乎热榜 | 需配置 |
| 微信公众号 | 需配置 |
| B站UP主 | 需配置 |

---

## 📁 文件结构

```
ai-article-publisher/
├── workflow.py              # 完整工作流脚本
├── topic_scorer.py          # 选题评分系统
├── collect_education.py     # 教育热点采集
├── output/                  # 输出结果
│   └── topics_xxx.json      # 选题列表
├── README.md                # 项目概述
├── PROGRESS.md              # 进度跟踪
├── EDUCATION_SOURCES.md     # 教育数据源文档
├── PSYCHOLOGY_SOURCES.md    # 心理学数据源文档
└── HOTNEWS_RESOURCES.md     # 热点采集资源
```

---

## 🔄 完整工作流

```
┌─────────────────────────────────────────────────────────────┐
│                   AI Article Publisher                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 热点采集                                                │
│     ├── wemp-operator (微博/知乎/GitHub...)                │
│     ├── RSSHub (5000+ 数据源)                              │
│     └── 自定义脚本 (教育/心理学)                            │
│                                                             │
│  2. 智能选题                                                │
│     ├── 热度评分 (30%)                                     │
│     ├── 时效评分 (20%)                                     │
│     ├── 受众匹配 (25%)                                     │
│     ├── 竞争评分 (15%)                                     │
│     └── 难度评分 (10%)                                     │
│                                                             │
│  3. 内容创作 (wechat-article-skill)                        │
│     ├── AI 写作                                            │
│     ├── 封面生成                                           │
│     └── 格式排版                                           │
│                                                             │
│  4. 审查订正 (Phase 5 待开发)                              │
│     ├── 语法检查                                           │
│     ├── 敏感词检测                                         │
│     └── AI痕迹消除                                         │
│                                                             │
│  5. 草稿发布 (wemp + wechat-article-skill)                 │
│     └── 推送到公众号草稿箱                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 选题评分算法

### 权重配置

```python
WEIGHTS = {
    "热度": 0.30,      # 阅读量/点赞/评论数
    "时效": 0.20,      # 发布时间新鲜度
    "受众匹配": 0.25,  # 与用户关注领域匹配度
    "竞争": 0.15,      # 竞争激烈程度
    "难度": 0.10       # 写作难度
}
```

### 推荐等级

| 分数 | 等级 |
|------|------|
| 80+ | 强烈推荐 |
| 70+ | 推荐 |
| 60+ | 可以考虑 |
| 50+ | 一般 |
| <50 | 不推荐 |

---

## 🔌 已安装的 Skills

| Skill | 功能 |
|-------|------|
| wemp-operator | 热点采集 + 70 API |
| wechat-article-skill | 写作 + 封面 + 发布 |
| universal-feeds | RSS聚合 |
| rss-skill | RSS订阅 |

---

## 📝 下一步

1. **配置公众号凭据** - 需要用户提供 AppID/AppSecret
2. **开发 Phase 5** - 审查订正系统
3. **配置 Puppeteer** - 解锁更多数据源
4. **定时任务** - 设置 Cron 自动采集

---

*最后更新: 2026-02-21*