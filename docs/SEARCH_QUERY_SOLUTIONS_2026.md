# 信息查询与搜索方案系统性调研 (2026)

> **调研时间**: 2026-02-27
> **调研目标**: 系统性梳理所有可用的搜索/查询信息方案
> **调研方法**: web_fetch 直接抓取 GitHub 项目文档 + 官方文档

---

## 📊 搜索方案全景图

### 六大类搜索方案

| 类别 | 代表方案 | 成本 | 稳定性 | 数据质量 | 推荐度 |
|------|---------|------|--------|---------|--------|
| **搜索引擎 API** | SerpApi/ZenSERP | 💰💰💰 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **自托管搜索引擎** | SearXNG | $0 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **无头浏览器** | Puppeteer+Browserless | $0 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **免费 API** | DuckDuckGo 非官方 | $0 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **工作流平台** | n8n/LangChain | $0-💰 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **公共 API 聚合** | Public-APIs | $0 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 🔬 方案一：搜索引擎 API (最稳定)

### 1.1 SerpApi

**项目**: https://serpapi.com
**支持引擎**: Google/Bing/Baidu/Yahoo/DuckDuckGo/eBay/YouTube 等

**价格**:
- 免费：100 次/月
- 入门：$50/月 (5000 次)
- 企业：$500/月 (无限制)

**Python 示例**:
```python
from serpapi import GoogleSearch

search = GoogleSearch({
    "q": "AI 教育",
    "location": "China",
    "hl": "zh-cn",
    "api_key": "your_api_key"
})
results = search.get_dict()
print(results["organic_results"])
```

**优势**:
- ✅ 最稳定可靠
- ✅ 支持 70+ 搜索引擎
- ✅ 返回结构化 JSON
- ✅ 处理反爬/验证码

**劣势**:
- ❌ 免费额度有限
- ❌ 付费版较贵

---

### 1.2 ZenSERP

**项目**: https://zenserp.com
**支持引擎**: Google/Bing

**价格**:
- 免费：1000 次/月
- 入门：$29/月 (5000 次)

**API 示例**:
```python
import requests

url = "https://api.zenserp.com/search"
params = {
    "apikey": "your_api_key",
    "q": "AI 教育",
    "device": "desktop",
    "location": "China"
}

response = requests.get(url, params=params)
results = response.json()
```

---

### 1.3 其他搜索 API

| 服务商 | 免费额度 | 付费起点 | 特点 |
|--------|---------|---------|------|
| **SerpApi** | 100 次/月 | $50/月 | 最成熟 |
| **ZenSERP** | 1000 次/月 | $29/月 | 性价比高 |
| **ScraperAPI** | 5000 次/月 | $29/月 | 内置代理 |
| **ScrapingBee** | 1000 次/月 | $49/月 | 支持 JS |
| **ValueSERP** | 100 次/月 | $12/月 | 最便宜 |

---

## 🔬 方案二：自托管搜索引擎 (推荐 ⭐⭐⭐⭐⭐)

### 2.1 SearXNG

**项目**: https://github.com/searxng/searxng
**许可证**: AGPL-3.0

**部署**:
```bash
# Docker 一键部署
docker run -d --name searxng \
  -p 8080:8080 \
  -e BASE_URL=http://localhost:8080/ \
  searxng/searxng
```

**API 使用**:
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

**配置优化** (`settings.yml`):
```yaml
search:
  safe_search: 0  # 关闭安全过滤
  autocomplete: "google"
  
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
    
  - name: wikipedia
    engine: wikipedia
    shortcut: wp
    disabled: false
```

**优势**:
- ✅ 完全免费 (自托管)
- ✅ 70+ 搜索源聚合
- ✅ 隐私保护 (不追踪)
- ✅ 可定制引擎
- ✅ 支持中文

**劣势**:
- ⚠️ 需要自己维护服务器
- ⚠️ 部分引擎可能限流

---

### 2.2 Whoogle Search

**项目**: https://github.com/benbusby/whoogle-search
**特点**: 专注于 Google 搜索的隐私前端

**部署**:
```bash
docker run -p 5000:5000 benbusby/whoogle-search
```

---

## 🔬 方案三：无头浏览器 (最灵活 ⭐⭐⭐⭐⭐)

### 3.1 Browserless + Puppeteer

**Browserless 项目**: https://github.com/browserless/browserless

**部署**:
```bash
# 自托管 Browserless
docker run -p 3000:3000 ghcr.io/browserless/chromium
```

**Puppeteer 使用**:
```javascript
const puppeteer = require('puppeteer-core');

const browser = await puppeteer.connect({
  browserWSEndpoint: 'ws://localhost:3000',
});

const page = await browser.newPage();
await page.goto('https://www.google.com/search?q=AI 教育');

// 等待搜索结果
await page.waitForSelector('.g');

// 提取搜索结果
const results = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('.g')).map(el => ({
    title: el.querySelector('h3')?.textContent,
    url: el.querySelector('a')?.href,
    snippet: el.querySelector('.VwiC3b')?.textContent
  }));
});

await browser.close();
console.log(results);
```

**Python 版本 (Playwright)**:
```python
from playwright.async_api import async_playwright

async def search_google(query):
    async with async_playwright() as p:
        browser = await p.chromium.connect('ws://localhost:3000')
        page = await browser.new_page()
        await page.goto(f'https://www.google.com/search?q={query}')
        await page.wait_for_selector('.g')
        
        results = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('.g')).map(el => ({
                title: el.querySelector('h3')?.textContent,
                url: el.querySelector('a')?.href,
                snippet: el.querySelector('.VwiC3b')?.textContent
            }));
        }''')
        
        await browser.close()
        return results
```

**优势**:
- ✅ 完全控制搜索过程
- ✅ 可处理 JS 渲染页面
- ✅ 可截图/录屏
- ✅ 可模拟人类行为
- ✅ 自托管免费

**劣势**:
- ⚠️ 需要处理反爬
- ⚠️ 需要维护浏览器
- ⚠️ 速度较慢

---

### 3.2 Selenium

**项目**: https://github.com/SeleniumHQ/selenium

**Python 示例**:
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')

driver = webdriver.Chrome(options=options)
driver.get('https://www.google.com/search?q=AI 教育')

results = []
for item in driver.find_elements('.g'):
    try:
        title = item.find_element('css selector', 'h3').text
        url = item.find_element('css selector', 'a').get_attribute('href')
        snippet = item.find_element('css selector', '.VwiC3b').text
        results.append({'title': title, 'url': url, 'snippet': snippet})
    except:
        pass

driver.quit()
```

---

## 🔬 方案四：免费 API (最简单)

### 4.1 DuckDuckGo 非官方 API

**API 端点**:
```
https://api.duckduckgo.com/?q=关键词&format=json
```

**Python 示例**:
```python
import urllib.request
import json
import urllib.parse

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

**优势**:
- ✅ 无需 API Key
- ✅ 完全免费
- ✅ 简单快速

**劣势**:
- ⚠️ 仅返回摘要 (~10 条)
- ⚠️ 不适合深度搜索

---

### 4.2 Wikipedia API

**API 端点**:
```
https://zh.wikipedia.org/w/api.php
```

**Python 示例**:
```python
import requests

def search_wikipedia(query, lang='zh'):
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 10
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    return [
        {
            "title": item['title'],
            "snippet": item['snippet'],
            "url": f"https://{lang}.wikipedia.org/wiki/{item['title']}"
        }
        for item in data['query']['search']
    ]

# 测试
results = search_wikipedia("人工智能")
print(results)
```

---

### 4.3 其他免费 API

| API | 端点 | 限制 | 特点 |
|-----|------|------|------|
| **DuckDuckGo** | `api.duckduckgo.com` | 无 | 摘要搜索 |
| **Wikipedia** | `wikipedia.org/w/api.php` | 无 | 百科条目 |
| **OpenWeather** | `api.openweathermap.org` | 60 次/分 | 天气数据 |
| **NewsAPI** | `newsapi.org` | 100 次/天 | 新闻搜索 |
| **Giphy** | `api.giphy.com` | 无 | GIF 搜索 |

---

## 🔬 方案五：工作流平台 (最强大)

### 5.1 n8n

**项目**: https://github.com/n8n-io/n8n
**特点**: 工作流自动化平台，400+ 集成

**部署**:
```bash
# Docker 部署
docker run -d --name n8n -p 5678:5678 docker.n8n.io/n8nio/n8n
```

**搜索工作流示例**:
```
1. HTTP Request 节点 → 调用 SearXNG API
2. Code 节点 → 处理搜索结果
3. HTTP Request 节点 → 抓取网页内容
4. AI 节点 → 分析总结
5. 输出节点 → 生成报告
```

**优势**:
- ✅ 可视化工作流
- ✅ 400+ 集成
- ✅ 支持 AI/LLM
- ✅ 自托管免费

---

### 5.2 LangChain

**项目**: https://github.com/langchain-ai/langchain
**特点**: LLM 应用开发框架

**搜索工具集成**:
```python
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI

# 初始化工具
search = DuckDuckGoSearchRun()

# 创建 Agent
llm = OpenAI(temperature=0)
agent = initialize_agent(
    tools=[search],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# 执行搜索
result = agent.run("AI 教育的最新发展")
print(result)
```

**优势**:
- ✅ 与 LLM 深度集成
- ✅ 支持多工具组合
- ✅ 自动推理

---

## 🔬 方案六：公共 API 聚合

### Public-APIs 项目

**项目**: https://github.com/public-apis/public-apis
**Stars**: 280K+

**收录 API 分类**:
- 动物/动漫/艺术
- 商业/加密货币/货币
- 开发/文档/邮件
- 娱乐/财务/食品
- 地理/政府/健康
- 新闻/音乐/照片
- 科学/体育/测试
- 天气/视频...

**使用方式**:
```python
import requests

# 获取 API 列表
response = requests.get(
    "https://api.publicapis.org/entries?category=News"
)
apis = response.json()

# 使用具体 API
for api in apis['entries']:
    print(f"{api['API']}: {api['Description']}")
    print(f"  URL: {api['Link']}")
    print(f"  Auth: {api['Auth']}")
    print(f"  HTTPS: {api['HTTPS']}")
```

---

## 📋 方案对比总结

### 按使用场景推荐

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| **快速验证** | DuckDuckGo API | 无需部署，立即使用 |
| **生产环境** | SerpApi/ZenSERP | 最稳定可靠 |
| **成本敏感** | SearXNG 自托管 | 完全免费 |
| **深度抓取** | Browserless+Puppeteer | 最灵活 |
| **工作流自动化** | n8n/LangChain | 可视化编排 |
| **学术研究** | Wikipedia API | 权威来源 |

---

### 按成本排序

| 方案 | 月度成本 | 部署难度 | 维护成本 |
|------|---------|---------|---------|
| **DuckDuckGo API** | $0 | 🟢 低 | 🟢 低 |
| **SearXNG 自托管** | $5 (VPS) | 🟡 中 | 🟢 低 |
| **Browserless 自托管** | $5 (VPS) | 🟡 中 | 🟢 低 |
| **n8n 自托管** | $5 (VPS) | 🟡 中 | 🟢 低 |
| **ZenSERP** | $29 起 | 🟢 低 | 🟢 低 |
| **SerpApi** | $50 起 | 🟢 低 | 🟢 低 |

---

### 按数据质量排序

| 方案 | 数据源 | 更新频率 | 准确性 |
|------|--------|---------|--------|
| **SerpApi** | Google 官方 | 实时 | ⭐⭐⭐⭐⭐ |
| **SearXNG** | 70+ 引擎 | 实时 | ⭐⭐⭐⭐⭐ |
| **Browserless** | 直接抓取 | 实时 | ⭐⭐⭐⭐⭐ |
| **DuckDuckGo** | 自有索引 | 小时级 | ⭐⭐⭐⭐ |
| **Wikipedia** | 社区编辑 | 天级 | ⭐⭐⭐⭐ |

---

## 🎯 最终推荐

### 最佳组合方案

**生产环境**:
```
SearXNG (搜索) + Browserless (抓取) + LangChain (分析)
```

**成本**: $10-15/月 (VPS 费用)
**数据质量**: ⭐⭐⭐⭐⭐
**稳定性**: ⭐⭐⭐⭐⭐

**快速验证**:
```
DuckDuckGo API + LangChain
```

**成本**: $0
**数据质量**: ⭐⭐⭐
**稳定性**: ⭐⭐⭐⭐

---

## 📚 参考资料

### 开源项目
- [SearXNG](https://github.com/searxng/searxng) - 元搜索引擎
- [Browserless](https://github.com/browserless/browserless) - Docker 化浏览器
- [Puppeteer](https://github.com/puppeteer/puppeteer) - Chrome 自动化
- [Selenium](https://github.com/SeleniumHQ/selenium) - 浏览器自动化
- [n8n](https://github.com/n8n-io/n8n) - 工作流自动化
- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用框架
- [Public-APIs](https://github.com/public-apis/public-apis) - 公共 API 聚合

### 商业服务
- [SerpApi](https://serpapi.com) - 搜索 API
- [ZenSERP](https://zenserp.com) - 搜索 API
- [ScraperAPI](https://scraperapi.com) - 爬虫 API

---

*调研完成时间：2026-02-27 03:00 UTC+8*
