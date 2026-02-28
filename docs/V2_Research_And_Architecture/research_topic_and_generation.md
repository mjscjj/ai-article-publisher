# 🎯 智能选题与文章生成 V2 (Topic & Generation V2)

> **立项时间**: 2026-02-24
> **阶段目标**: 将 `ai-article-publisher` 从“单线热点搬运工”升级为“拥有独立智库搜索、多角博弈能力的全网爆款制造机”。
> **核心原则**: 分步骤、渐进式重构，确保线上业务不断流。

---

## 🔍 一、 全网前沿开源方案与 MCP 工具深度调研

我们对 GitHub 上最新的 AI 内容生成与 Agent 架构进行了深度挖掘，筛选出以下最适合直接“拿来主义”的开源方案与工具：

### 1. 多智能体博弈与编排 (Multi-Agent Orchestration / Editor-in-Chief System)
*   **[Medium-Article-Generator](https://github.com/Nikhil-MLOPs/Medium-Article-Generator)**: 一个生产级的 AI 系统，包含写手、审阅者、以及一个 **Editor-in-Chief（总编代理）**。总编负责审查整篇文章的流畅度与爆款结构。
*   **[AI-Agent-Orchestrator](https://github.com/edilma/AI-Agent-Orchestrator)**: 基于 Autogen 的多代理文章生成域，可以动态分配“搜索”、“排版”、“修正”的子任务。
*   **启发**: 我们可以直接提取“总编审核 Prompt”，放在我们的 `reviewer.py` 或未来的 `feishu_integration.py` 环节之前。

### 2. 长文网状检索与 RAG 防同质化 (Agentic Research & Outlining)
*   **[ResearchFlow](https://github.com/amitksingh2103/ResearchFlow-Agentic-AI-Research-Content-Automation-System)**: 自动发起 Web 检索，拉取数百个网页喂给本地 RAG 管道，最终输出深度报告的超级代理。
*   **[arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) / Brave Search MCP**: 能够让模型直接调用外部接口搜索 arXiv 论文和最新网页。
*   **启发**: 我们的选题必须增加外挂搜索功能（借用 OpenClaw 的 Web fetch/search 能力）。遇到“AI 替代打工人”这种热点，自动用 MCP 工具抓取 3 篇外网独立研报，作为子节点的输入材料。

### 3. 数据降噪与聚合 (Semantic Clustering)
*   本地算法 / `scikit-learn`: 使用轻量级的 TF-IDF 文本聚类算法，在 3000 多条热点丢给 LLM 之前，先把同类项合并拼成一个“大新闻簇”。（避免大模型白白消耗 token 去阅读 50 条“某地大雪”的新闻）。

---

## 🛠️ 二、 V2 架构落地实操建议（MVP 拆解）

我们要将这些庞大的概念转化为 OpenClaw 环境下具体的 Python 代码实现。为了防止步子迈得太大扯破了现有运行流，**我强烈建议将 V2 升级拆分为 4 个渐进式的 Step**：

### 🚀 Step 1: 选题清洗（今明两天完成）
*   **目标**: 解决“满屏相似热点轰炸 LLM，导致选题过于平庸且成本高”的痛点。
*   **操作**: 新建 `sources/cluster_hotspots.py`，用 Python 本地的相似度算法（如 `Levenshtein` 或 `SentenceTransformer` 甚至简单的关键词重合度）或者让免费的 `deepseek-r1` 做前置提纯。把今天搜集到的所有“同源事件”打包为一个 Topic。
*   **验收**: 运行集群脚本后，交给 `topic_selector.py` 的选项从 3000 个乱语变成了 20 个“重磅宏大议题”。

### ⚖️ Step 2: 引入“毒舌主编”对冲制（本周中期完成）
*   **目标**: 解决“选出的切入点像官方通稿、毫无自媒体锐度”的痛点。
*   **操作**: 改造 `topic_selector.py`。拿到大模型一发的选题后，拉起一个扮演“咪蒙/虎嗅主编”的隔离 Agent（子代理）。设定它的职责是“挑毛病并提出逆向思维的反转角度”。
*   **验收**: 比如系统给的普通大纲是“分析大模型降价”，毒舌主编打回并强制修改为：“大模型跳水的背后：是谁在为这波算力买单？普通人根本接不住。”

### 🕸️ Step 3: STORM 式并行抓取与织肉（本周末完成核心）
*   **目标**: 解决文章太短、水分多、AI 味重的痛点。
*   **操作**: 
    1. 敲定大纲后，提取 3 个核心论点。
    2. 使用 OpenClaw `web_search` 搜索外网新闻或百度资讯。
    3. 调用 `sessions_spawn` 启动 3 个子 Agent，把搜回来的客观素材塞给它们，要求它们并行写出 3 个不带废话的重度分析小节。
*   **验收**: 输出的文稿突破 2500 字，包含极具信息差的外部新闻引用。

### 🎨 Step 4: Python 数据绘图与飞书组装（下周迭代）
*   **目标**: 图文并茂，并在飞书里做最终的人工防爆确认。
*   **操作**: 遇到需要说明的走势，代码执行 Agent 在后台跑出统计图保存至本地。最后图文排版通过 `feishu_integration.py` 扔进群里等待您回复“@发布”。
*   **验收**: 收到飞书提醒，审阅无误后文章通过 `wemp-operator` 进入公众号。

---

## 📝 总结路线图

目前的 `ai-article-publisher` 是一个高效率的**单管步枪（V1）**。
通过以上 **4 个 Step 分步迭代**，它将进化为一个带领**前哨侦查员（MCP 聚类搜查）、总编裁判（辩论 Agent）、三位特约撰稿人（并行写肉），最后交递到您手里（飞书终审）的现代化自动编辑部（V2）**。
