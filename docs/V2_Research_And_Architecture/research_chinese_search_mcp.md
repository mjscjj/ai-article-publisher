# 🔍 中文语境寻矿工具链与内网探针设计 (Domestic Sniffer Architecture)

在“双轨混合式情报站（Deep Research & Domestic Search）”这一核心模块中，如果只依赖海外搜索/维基，产出的内容会充满“洋味”。公号爆款需要国内真实的民生情绪与“网感”。通过深入排查 GitHub 开源 MCP 库并结合现有基建，我们敲定了如下三路并进的【海陆空混编搜集部队】战术：

## 战术部署一览 (实操方案)

### 🎯 1. 抓取“内网官方通稿”与“背景事实” (基础兜底)
*   **接入项目**: [baidu-mcp-server](https://github.com/Evilran/baidu-mcp-server) 或者 中文 Bing MCP (`Uiverse_MCP`)
*   **战术意图**: 当输入硬核科技词条或国内政策时，充当背景词典。比传统爬虫稳定，符合 MCP 协议，大模型调用极度舒适。它构筑文章理信部分的“骨架”。

### 🎯 2. 抓取“下沉情绪”与“野生神评论” (核心武器！)
*   **接入项目**: 🔥 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) (9000+ Stars)
*   **战术意图**: 解决百度文章空洞无梗的问题。小红书是简中少数未经大规模 AI 机器化污染的活体语料库。
*   **实操机制**: `domestic_sniffer.py` 内部检测到是“消费/职场/两性”类热点时，直接让 Agent 挂载该 MCP 接口，强行提取话题排名前 5 帖子的“高赞爆梗评论”。作为毒舌主编进行反转驳斥的“弹药”。

### 🎯 3. 抓取“深度辩论”与“增量搜索库” (内网 RSSHub 并网重铸)
*   **项目沿用与进化**: 抛弃外部极其脆弱的针对个别站点的防爬轮子，直接拉满利用我们系统的天然优势——宿主机上正在运行的 **RSSHub 服务 (Port: 1200)**。
*   **战术意图**: 
    1.  **静态聚合升级为动态检索**：RSSHub 除了提供固定的热榜（如 `/zhihu/hot`）外，它绝大多数的路由本身支持带有参数的搜索透传！比如某平台路由 `/bilibili/search/{keyword}` 或微博搜索钩子。大模型可以直接对 `domestic_sniffer.py` 吐出关键词，程序拼接至 `localhost:1200/...` ，实现无阻碍的内网高速全文检索。
    2.  **获取极端论战**：针对性抽取各大高冲突类社群（例如 V2EX、知乎、虎扑）的原生 XML/JSON 流。因为是由本地 RSSHub 中转，请求不仅免登录封禁问题，且返回的数据格式异常干净规则，为多智能体提取“争议论点”提供完美的序列化支持。

---
## ⚙️ 模块二 `domestic_sniffer.py` 详细开发计划

未来在开发 `plugins/retrieval/domestic_sniffer.py` 模块时，其代码架构逻辑必须按照上述兵种严格执行路由分发：

```python
def domestic_search_router(topic: dict):
    """
    智能内网探针路由分配器 (基于关键词与分类)
    """
    category = topic.get("category", "综合")
    keyword = topic.get("keyword", "")
    pack = {"facts": [], "emotions": [], "debates": [], "rss_search_raw": []}

    # 1. 基础事实兜底 (Baidu / Bing)
    pack["facts"] = call_baidu_mcp(keyword)
    
    # 2. 情绪短评抓取 (小红书/生活方式)
    if is_emotional_category(category):
        pack["emotions"] = call_xiaohongshu_mcp(keyword)
    
    # 3. 深度内容与发散搜索 (全面接线本地 RSSHub 接口引擎)
    # 利用 RSSHub 把关键词打向各大垂直平台 (通过类似于 /weibo/search/:keyword 获取)
    if is_debate_required(topic):
        pack["rss_search_raw"] = call_local_rsshub_search_router(keyword, target_hubs=["zhihu", "weibo", "bilibili"])
        
    return process_and_flatten_to_markdown(pack)
```

有了这套严丝合缝的【事实+情绪+内网RSS搜索联链】的三叉戟配方护航，我们产出的 `Fact-Pack` (投包材料) 已经足以碾压市面上 99% 靠猜词堆砌的营销号矩阵，为并联写作模型提供“开炮”级别的绝杀弹药！
