# AI Article Publisher - 热点收集资源清单

> 热点自动收集相关的教程、MVP、Skill 和项目

---

## 🔥 核心推荐

### DailyHotApi - 今日热榜 API ⭐⭐⭐⭐⭐

**仓库**: https://github.com/imsyy/DailyHotApi  
**Stars**: 3.6k ⭐  
**语言**: TypeScript  
**更新**: 17 days ago

**这是热点收集模块的最佳选择！**

#### 功能特点
- 📊 **60+ 数据源** - 聚合全网热门数据
- ⚡ **极快响应** - 便于开发
- 📰 **支持 RSS/JSON** - 灵活的数据格式
- 🐳 **Docker 部署** - 一键部署
- ☁️ **Vercel 支持** - 免费托管

#### 支持的数据源（部分）
| 站点 | 类别 | 调用名称 |
|------|------|----------|
| 哔哩哔哩 | 热门榜 | `bilibili` |
| 微博 | 热搜榜 | `weibo` |
| 知乎 | 热榜 | `zhihu` |
| 百度 | 热搜榜 | `baidu` |
| 抖音 | 热点榜 | `douyin` |
| 快手 | 热点榜 | `kuaishou` |
| 今日头条 | 热榜 | `toutiao` |
| 36氪 | 热榜 | `36kr` |
| 稀土掘金 | 热榜 | `juejin` |
| IT之家 | 热榜 | `ithome` |
| 少数派 | 热榜 | `sspai` |
| 豆瓣电影 | 新片榜 | `douban-movie` |
| 澎湃新闻 | 热榜 | `thepaper` |
| CSDN | 排行榜 | `csdn` |
| Hacker News | 热榜 | `hackernews` |
| GitHub | Trending | `github` |
| ProductHunt | 热榜 | `producthunt` |
| ... | ... | **60+ 源** |

#### API 使用示例
```bash
# 获取微博热搜
curl https://api-hot.imsyy.top/weibo

# 获取知乎热榜
curl https://api-hot.imsyy.top/zhihu

# 获取 Hacker News
curl https://api-hot.imsyy.top/hackernews

# RSS 模式
curl https://api-hot.imsyy.top/weibo?rss=true
```

#### 部署方式
```bash
# Docker 部署
docker pull imsyy/dailyhot-api
docker run -d -p 6688:6688 imsyy/dailyhot-api

# Vercel 一键部署
# Fork 项目后直接部署到 Vercel
```

---

## 🦞 OpenClaw 相关 Skill

### wemp-operator - 公众号运营 Skill ⭐⭐⭐⭐⭐

**仓库**: https://github.com/IanShaw027/wemp-operator  
**Stars**: 21 ⭐  
**语言**: JavaScript

**OpenClaw 官方热点采集 Skill**

#### 数据源支持
| 类别 | 数据源 |
|------|--------|
| 科技 | hackernews, github, v2ex, sspai, juejin, ithome, producthunt |
| 中文热点 | weibo, zhihu, baidu, douyin, bilibili, toutiao, tencent, thepaper, hupu |
| 财经 | 36kr, wallstreetcn, cls |

#### 快捷分类
- `tech` - 所有科技类
- `china` - 所有中文热点
- `finance` - 所有财经类
- `all` - 全部数据源

#### 使用方式
```bash
# 安装
openclaw skill install IanShaw027/wemp-operator

# 使用
帮我采集今天的 AI 热点
从 Hacker News 和 V2EX 采集科技新闻
```

---

## 📰 其他热点收集项目

### 1. Google News Scraper
**仓库**: https://github.com/Decodo/Google-News-scraper  
**Stars**: 29  
**语言**: Python

**功能**:
- Google News 头条、摘要、来源采集
- 代理轮换防封禁
- 自动 CSV 导出
- 趋势分析

**安装**:
```bash
pip install requests beautifulsoup4 playwright
python -m playwright install
python google-news-scraper.py
```

---

### 2. Hacker News Scraper
**仓库**: https://github.com/filipzekavica/Hacker-News-Top-10-Web-Scraper  
**Stars**: 2  
**语言**: Python

**功能**:
- 采集 Hacker News Top 10
- CSV 导出

---

### 3. News Scraper (Discord)
**仓库**: https://github.com/tyronejosee/script_news_for_discord_scraper  
**Stars**: 2  
**语言**: Python

**功能**:
- 多新闻源采集
- 新内容检测
- Discord 推送

---

### 4. Weibo Actor (Apify)
**仓库**: https://github.com/bobofueeeee/apify-weibo-actor  
**Stars**: 0  
**语言**: Python

**功能**:
- 微博热搜采集
- Apify 平台支持

---

## 🔧 自建方案参考

### 方案一：直接调用 DailyHotApi

```javascript
// 热点采集脚本
const SOURCES = ['weibo', 'zhihu', '36kr', 'juejin', 'hackernews'];

async function collectHotNews() {
  const results = [];
  
  for (const source of SOURCES) {
    const response = await fetch(`https://api-hot.imsyy.top/${source}`);
    const data = await response.json();
    results.push({
      source,
      data: data.data.slice(0, 10) // 取前 10 条
    });
  }
  
  return results;
}
```

### 方案二：自建爬虫

```python
# 基于 BeautifulSoup 的简单爬虫
import requests
from bs4 import BeautifulSoup

def scrape_weibo_hot():
    url = "https://s.weibo.com/top/summary"
    headers = {"User-Agent": "Mozilla/5.0..."}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 解析逻辑...
```

---

## 📊 方案对比

| 方案 | 数据源数量 | 维护成本 | 稳定性 | 推荐度 |
|------|------------|----------|--------|--------|
| **DailyHotApi** | 60+ | 低 | 高 | ⭐⭐⭐⭐⭐ |
| **wemp-operator** | 20+ | 低 | 高 | ⭐⭐⭐⭐⭐ |
| **自建爬虫** | 自定义 | 高 | 中 | ⭐⭐⭐ |
| **Google News Scraper** | 1 | 中 | 中 | ⭐⭐⭐ |

---

## 🎯 推荐组合

**最佳方案**: DailyHotApi + wemp-operator

```
DailyHotApi (60+ 源)
      │
      ├── 提供统一 API 接口
      │
      ▼
wemp-operator (OpenClaw Skill)
      │
      ├── 关键词过滤
      ├── 热度评分
      ├── 分类标签
      │
      ▼
   AI Agent
      │
      └── 选题推荐
```

---

## 📝 集成示例

### 在 OpenClaw 中使用 DailyHotApi

```javascript
// SKILL.md 中的脚本示例
// scripts/collect-hot.mjs

const API_BASE = 'https://api-hot.imsyy.top';

export async function collectFromSource(source) {
  const response = await fetch(`${API_BASE}/${source}`);
  return response.json();
}

export async function collectAll() {
  const sources = ['weibo', 'zhihu', '36kr', 'juejin', 'hackernews'];
  const results = await Promise.all(
    sources.map(s => collectFromSource(s))
  );
  return results.flat();
}
```

---

## 📚 相关教程

1. [DailyHotApi 官方文档](https://github.com/imsyy/DailyHotApi)
2. [Google News Scraper 教程](https://decodo.com/blog/how-to-scrape-google-news)
3. [wemp-operator 使用指南](https://github.com/IanShaw027/wemp-operator)

---

*最后更新: 2026-02-21*