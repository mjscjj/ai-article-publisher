# 免费云端浏览器搜索方案调研 (2026)

> **调研时间**: 2026-02-27
> **调研目标**: 寻找不使用 Brave API 等付费服务的云端浏览器搜索方案
> **调研方法**: web_fetch 直接抓取 GitHub 项目文档

---

## 📊 核心发现

### 四大类免费方案

| 类别 | 代表方案 | 成本 | 稳定性 | 推荐度 |
|------|---------|------|--------|--------|
| **自托管无头浏览器** | Puppeteer + Browserless | $0 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **开源搜索引擎** | SearXNG | $0 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **聚合搜索 API** | DuckDuckGo (非官方) | $0 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **云端浏览器服务** | Browserless 免费版 | $0 (有限额) | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🔬 方案一：自托管无头浏览器 (推荐 ⭐⭐⭐⭐⭐)

### 技术栈

**核心组件**:
- [Puppeteer](https://github.com/puppeteer/puppeteer) - Chrome 自动化控制 (Node.js)
- [Selenium](https://github.com/SeleniumHQ/selenium) - 跨浏览器自动化
- [Browserless](https://github.com/browserless/browserless) - Docker 化浏览器服务

### Browserless 方案

**部署方式**:
```bash
# Docker 一键部署 (免费自托管版)
docker run -p 3000:3000 ghcr.io/browserless/chromium
```

**连接方式**:
```javascript
// Puppeteer 连接远程浏览器
const puppeteer = require('puppeteer-core');

const browser = await puppeteer.connect({
  browserWSEndpoint: 'ws://localhost:3000',
});

const page = await browser.newPage();
await page.goto('https://www.google.com/search?q=AI 教育');
const html = await page.content();
await browser.close();
```

**优势**:
- ✅ 完全免费 (自托管)
- ✅ 支持 Puppeteer/Playwright
- ✅ 内置字体和 emoji
- ✅ 可配置并发和超时
- ✅ 错误容错 (Chrome 崩溃不影响服务)

**局限性**:
- ⚠️ 需要自己维护 Docker 容器
- ⚠️ 需要处理反爬 (User-Agent/代理)
- ⚠️ 免费版无代理/IP 轮换功能

---

## 🔬 方案二：SearXNG 自托管搜索引擎 (推荐 ⭐⭐⭐⭐⭐)

### 什么是 SearXNG?

**SearXNG** 是一个免费的元搜索引擎，聚合了 70+ 个搜索源 (Google/Bing/DuckDuckGo 等)。

**项目**: https://github.com/searxng/searxng
**许可证**: AGPL-3.0

### 部署方式

```bash
# Docker 部署
docker run -d --name searxng \
  -p 8080:8080 \
  -e BASE_URL=http://localhost:8080/ \
  searxng/searxng
```

### API 使用

```bash
# 搜索 API (返回 JSON)
curl "http://localhost:8080/search?q=AI 教育&format=json"
```

**返回格式**:
```json
{
  "query": "AI 教育",
  "results": [
    {
      "title": "文章标题",
      "url": "https://example.com/article",
      "content": "摘要内容...",
      "engine": "google",
      "score": 0.95
    }
  ]
}
```

### 优势

- ✅ **完全免费** - 无 API 限制
- ✅ **隐私保护** - 不追踪用户
- ✅ **70+ 搜索源** - Google/Bing/DDG/维基百科等
- ✅ **可定制** - 启用/禁用特定引擎
- ✅ **支持中文** - 完整的中文界面

### 配置优化

```yaml
# settings.yml 配置
search:
  safe_search: 0  # 关闭安全过滤
  autocomplete: "google"  # 自动补全
  
engines:
  - name: google
    engine: google
    shortcut: g
    disabled: false
    
  - name: bing
    engine: bing
    shortcut: b
    disabled: false
    
  - name: duckduckgo
    engine: duckduckgo
    shortcut: ddg
    disabled: false
```

---

## 🔬 方案三：DuckDuckGo 非官方 API

### 方案说明

DuckDuckGo 提供免费的即时答案 API (无需 API Key)。

**API 端点**:
```
https://api.duckduckgo.com/?q=关键词&format=json
```

### 使用示例

```python
import urllib.request
import json

def search_ddg(query):
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        return {
            "abstract": data.get('Abstract', ''),
            "results": [
                {"title": r.get('text'), "url": r.get('firstUrl')}
                for r in data.get('RelatedTopics', [])
            ]
        }

# 测试
results = search_ddg("AI 教育")
print(results)
```

### 优势

- ✅ 无需 API Key
- ✅ 完全免费
- ✅ 简单快速

### 局限性

- ⚠️ 仅返回摘要和相关主题 (非完整搜索结果)
- ⚠️ 结果数量有限 (~10 条)
- ⚠️ 不适合深度搜索

---

## 🔬 方案四：云端浏览器服务 (有限免费)

### Browserless 云服务

**免费版**:
- 每月 100 分钟免费额度
- 适合低频使用
- 无需部署

**付费版**:
- $25/月 起
- 包含代理/IP 轮换
- 反爬绕过

### 其他云浏览器服务

| 服务商 | 免费额度 | 付费起点 | 特点 |
|--------|---------|---------|------|
| Browserless | 100 分钟/月 | $25/月 | 最成熟 |
| ScrapingBee | 1000 次/月 | $49/月 | 内置代理 |
| ScraperAPI | 5000 次/月 | $29/月 | 自动重试 |
| ZenRows | 1000 次/月 | $39/月 | 反爬绕过 |

---

## 🛠️ 推荐实施方案

### 方案 A: SearXNG + Puppeteer (最佳组合 ⭐⭐⭐⭐⭐)

**架构**:
```
用户查询
    ↓
SearXNG (聚合搜索) → 返回 20+ 来源
    ↓
Puppeteer (按需抓取) → 深度抓取网页内容
    ↓
LLM 分析 → 生成报告
```

**部署成本**: $0/月 (自托管)

**实施步骤**:

1. **部署 SearXNG** (1 小时)
   ```bash
   docker run -d --name searxng -p 8080:8080 searxng/searxng
   ```

2. **部署 Browserless** (30 分钟)
   ```bash
   docker run -d --name browserless -p 3000:3000 ghcr.io/browserless/chromium
   ```

3. **集成代码** (2 小时)
   ```python
   # 1. 用 SearXNG 搜索
   results = search_searxng("AI 教育")
   
   # 2. 用 Puppeteer 抓取前 5 个结果
   for url in results[:5]:
       content = await fetch_with_puppeteer(url)
   
   # 3. LLM 分析
   report = llm_analyze(content)
   ```

---

### 方案 B: 纯 SearXNG (最简单 ⭐⭐⭐⭐)

**适用场景**: 只需要搜索，不需要深度抓取

**部署**:
```bash
docker run -d --name searxng -p 8080:8080 searxng/searxng
```

**使用**:
```python
def search_with_searxng(keyword):
    url = f"http://localhost:8080/search?q={keyword}&format=json"
    response = requests.get(url)
    return response.json()
```

**成本**: $0/月

---

### 方案 C: Browserless 云 + 自研爬虫 (快速启动 ⭐⭐⭐)

**适用场景**: 快速验证，不想起步就部署

**使用**:
```javascript
const browser = await puppeteer.connect({
  browserWSEndpoint: 'wss://chrome.browserless.io?token=FREE_TOKEN',
});
```

**成本**: $0/月 (100 分钟免费额度)

---

## 📋 技术对比

| 方案 | 部署难度 | 维护成本 | 搜索质量 | 扩展性 | 总成本 |
|------|---------|---------|---------|--------|--------|
| **SearXNG + Puppeteer** | 🟡 中 | 🟢 低 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $0 |
| **纯 SearXNG** | 🟢 低 | 🟢 低 | ⭐⭐⭐⭐ | ⭐⭐⭐ | $0 |
| **Browserless 云** | 🟢 低 | 🟢 低 | ⭐⭐⭐ | ⭐⭐ | $0 (限额) |
| **Brave Search API** | 🟢 低 | 🟢 低 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $3/月 |

---

## 💰 成本分析

### 自托管方案 (SearXNG + Browserless)

| 组件 | 软件成本 | 硬件成本 | 月度总成本 |
|------|---------|---------|-----------|
| SearXNG | $0 (开源) | $5 (VPS) | $5 |
| Browserless | $0 (开源) | $5 (VPS) | $5 |
| **总计** | **$0** | **$10** | **$10/月** |

### 云端方案 (Browserless 云 + Brave API)

| 组件 | 免费额度 | 付费版 | 月度总成本 |
|------|---------|-------|-----------|
| Browserless 云 | 100 分钟 | $25/月 | $25 |
| Brave Search API | 2000 次 | $3/月 | $3 |
| **总计** | **$0** | **$28** | **$28/月** |

**结论**: 自托管方案成本仅为云端方案的 36%，且无使用限制。

---

## 🚀 实施建议

### 阶段 1: 快速验证 (今天)

1. 使用 DuckDuckGo 非官方 API (无需部署)
2. 验证搜索功能
3. 测试 LLM 分析效果

### 阶段 2: 部署 SearXNG (明天)

1. Docker 部署 SearXNG
2. 配置 70+ 搜索源
3. 替换 DuckDuckGo

### 阶段 3: 部署 Browserless (后天)

1. Docker 部署 Browserless
2. 集成 Puppeteer 抓取
3. 实现深度调研

### 阶段 4: 优化 (下周)

1. 添加代理/IP 轮换
2. 优化反爬策略
3. 性能调优

---

## 📚 参考资料

### 开源项目
- [SearXNG](https://github.com/searxng/searxng) - 元搜索引擎
- [Browserless](https://github.com/browserless/browserless) - Docker 化浏览器
- [Puppeteer](https://github.com/puppeteer/puppeteer) - Chrome 自动化
- [Selenium](https://github.com/SeleniumHQ/selenium) - 浏览器自动化

### 文档
- [SearXNG 官方文档](https://docs.searxng.org/)
- [Browserless 官方文档](https://docs.browserless.io/)
- [Puppeteer 官方文档](https://pptr.dev/)

---

## 🎯 最终推荐

**最佳方案**: SearXNG (搜索) + Puppeteer (抓取)

**理由**:
1. ✅ 完全免费 (自托管)
2. ✅ 70+ 搜索源，质量高
3. ✅ 无 API 限制
4. ✅ 可扩展性强
5. ✅ 社区活跃，持续维护

**部署时间**: 2-4 小时
**月度成本**: $5-10 (VPS 费用)
**维护成本**: 低 (Docker 自动更新)

---

*调研完成时间：2026-02-27 02:50 UTC+8*
