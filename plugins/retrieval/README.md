# Retrieval Plugins - 情报搜集插件集

> **职责**: 为文章生成模块提供高质量、多角度的 Fact-Pack (事实包)

---

## 📦 模块清单

| 模块 | 功能 | 数据源 | 状态 |
|------|------|--------|------|
| `global_searcher.py` | 外网硬轨搜索 | Google/Brave/维基百科 | ✅ 已实现 |
| `domestic_sniffer.py` | 内网情绪探针 V2 | 微博/知乎/B 站/什么值得买/百度 | ✅ 已升级 |
| `hot_warehouse_miner.py` | 本地仓库深掘 | data/hotnews/daily/*.json | ✅ 已实现 |
| `live_searcher.py` | 实时热点监控 | DuckDuckGo/RSSHub | ⏳ 开发中 |
| `fact_packer.py` | 资料洗练打包 | 聚合上述所有来源 | ✅ 已实现 |
| `bilibili_collector.py` | B 站视频采集 | B 站 (RSSHub) | ✅ 新增 (小红书替代) |
| `smzdm_collector.py` | 什么值得买采集 | SMZDM(RSSHub) | ✅ 新增 (小红书替代) |

---

## 🔧 部署指南

### 1. RSSHub 本地服务 (必需)

**用途**: `domestic_sniffer.py` 依赖 RSSHub 抓取微博/知乎搜索结果

**部署命令**:
```bash
docker run -d --name rsshub -p 1200:1200 diygod/rsshub
```

**验证**:
```bash
curl http://localhost:1200/weibo/search/hot?format=json
```

---

### 2. 小红书 MCP 服务 (可选，强烈推荐)

**用途**: `xiaohongshu_mcp_client.py` 获取小红书高赞笔记与神评论

**部署方式 A - Docker (推荐)**:
```bash
docker run -d --name xiaohongshu-mcp -p 8333:8333 xpzouying/xiaohongshu-mcp
```

**部署方式 B - 二进制文件**:
```bash
# 下载 https://github.com/xpzouying/xiaohongshu-mcp/releases
chmod +x xiaohongshu-mcp-linux-amd64
./xiaohongshu-mcp-linux-amd64
```

**首次登录**:
```bash
# 运行登录工具 (按提示扫码)
./xiaohongshu-login-linux-amd64
```

**验证**:
```bash
curl -X POST http://localhost:8333/search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "AI 教育"}'
```

---

### 3. Baidu MCP (可选)

**用途**: `domestic_sniffer.py` 可挂载百度 MCP 获取官方通稿

**部署**:
```bash
git clone https://github.com/Evilran/baidu-mcp-server.git
cd baidu-mcp-server
npm install
npm start
```

---

## 📡 使用示例

### 基础用法：单模块调用

```python
from plugins.retrieval.domestic_sniffer import sniff_domestic_emotions

result = sniff_domestic_emotions("大模型价格战")
print(result["weibo_comments"])      # 微博评论
print(result["zhihu_debates"])       # 知乎辩论
print(result["xiaohongshu_comments"]) # 小红书神评论 (需部署 MCP)
```

### 高级用法：完整 Fact-Pack 组装

```python
from plugins.retrieval import global_searcher, domestic_sniffer, fact_packer

topic = "AI 编程课进入中小学"

# 1. 外网硬轨
global_facts = global_searcher.search_global(topic, limit=10)

# 2. 内网情绪
domestic_emotions = domestic_sniffer.sniff_domestic_emotions(topic)

# 3. 本地仓库深掘
local_context = hot_warehouse_miner.mine_local_warehouse(["AI", "编程", "中小学"], top_n=15)

# 4. 打包成 Fact-Pack
fact_pack = fact_packer.pack_all(
    global_facts=global_facts,
    domestic_emotions=domestic_emotions,
    local_context=local_context,
)

# 5. 传递给写作模块
from plugins.article_generator.outliner import generate_outline
outline = generate_outline(fact_pack)
```

---

## 🛠️ 开发新检索器

遵循以下接口规范：

```python
def search_your_source(keyword: str, limit: int = 10) -> list:
    """
    返回统一格式：
    [
        {
            "source": "平台名",
            "title": "标题",
            "snippet": "摘要/评论内容",
            "url": "原文链接",
            "score": 热度分数 (可选),
        }
    ]
    """
    pass
```

然后在 `fact_packer.py` 中注册即可。

---

## 📊 性能基准

| 模块 | 平均耗时 | 成功率 | 备注 |
|------|---------|--------|------|
| `global_searcher` | 2-5s | 95% | 依赖网络 |
| `domestic_sniffer` (微博/知乎) | 1-3s | 90% | RSSHub 稳定性决定 |
| `domestic_sniffer` (小红书) | 5-10s | 85% | MCP 服务 + 登录态 |
| `hot_warehouse_miner` | <0.1s | 100% | 纯本地读取 |

---

*最后更新：2026-02-25 23:30 UTC+8*
