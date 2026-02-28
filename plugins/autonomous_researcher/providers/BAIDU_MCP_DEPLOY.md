# 百度 MCP 部署指南

> **项目**: https://github.com/Evilran/baidu-mcp-server
> **功能**: 通过百度搜索获取中文新闻、政策通稿、行业报告

---

## 📦 安装步骤

### 方式 1: 本地开发模式 (已执行)

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher/plugins/autonomous_researcher/providers/baidu-mcp-server
pip install -e .
```

### 方式 2: PyPI 安装

```bash
pip install baidu-mcp-server
```

### 方式 3: UV 安装

```bash
uv pip install baidu-mcp-server
```

---

## 🚀 启动服务

### 直接运行

```bash
baidu-mcp-server
# 默认监听 stdio (标准输入输出)
```

### HTTP 模式 (需要额外配置)

百度 MCP 默认使用 stdio 传输，如需 HTTP 模式需要：

1. 使用 `mcp-proxy` 或 `mcp-stdio-proxy` 转换
2. 或参考 `smithery.yaml` 配置

**推荐**: 直接在 Python 代码中 import 调用，无需独立服务

---

## 🔌 Python 代码集成

```python
from baidu_mcp_server.server import BaiduSearchTool

# 初始化
searcher = BaiduSearchTool()

# 搜索
results = searcher.search("AI 教育 政策 2025", num_results=10)

# 获取网页内容
content = searcher.fetch_url("https://example.com/article")
```

---

## 📡 集成到 Domestic Sniffer

在 `domestic_sniffer.py` 中：

```python
def sniff_baidu_news(keyword: str) -> list:
    """调用百度 MCP 获取官方通稿"""
    try:
        from baidu_mcp_server.server import BaiduSearchTool
        searcher = BaiduSearchTool()
        results = searcher.search(keyword, num_results=10)
        return [
            {"title": r.get('title', ''), "snippet": r.get('snippet', ''), "url": r.get('url', '')}
            for r in results
        ]
    except Exception as e:
        print(f"[Domestic Sniffer] ⚠️ 百度 MCP 调用失败：{e}")
        return []
```

---

## ⚠️ 注意事项

1. **依赖 Playwright**: 首次运行需要 `playwright install` 下载浏览器
2. **反爬策略**: 内置 rate limiting，建议单次请求间隔 1-2 秒
3. **代理配置**: 如需代理，设置环境变量 `HTTP_PROXY` / `HTTPS_PROXY`

---

## 🔍 测试命令

```bash
# 测试搜索
python -c "from baidu_mcp_server.server import BaiduSearchTool; print(BaiduSearchTool().search('AI 教育'))"
```

---

*最后更新：2026-02-26 22:15 UTC+8*
