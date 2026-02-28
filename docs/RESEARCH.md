# AI 辅助写作深研架构评测 (Deep Research Agents)
整理时间: 2026-02-24

在当前文章生成模块基础上，引入具有"自动推理、拆词、多次搜索校验、合并"的开源项目。

## 顶级开源项目推荐

1. **assafelovic/gpt-researcher** (2.5万 Star)
- **状态**: 现象级绝对标杆
- **机制**: 采用 Master-Subagent (主管-分析员) 机制。输入一个命题后，主管特工会拆选出 3-5 个不同视角的子特工。子特工并行去公网多线程爬虫找新闻、汇总。主管最后将所有碎片整合出一篇长达数千字的学术标准 Research Report。
- **优点**: 非常成熟，支持直接输出 PDF/Word，接口模块化，原生支持多 LLM 和 Tavily (AI 搜索 API)。

2. **dzhng/deep-research** (1.8万 Star)
- **状态**: 爆红的纯精简实现版
- **机制**: 旨在用极少的代码实现完全迭代式的深度潜水搜索（可以随着时间推移修正研究方向的 agent）。
- **优点**: 代码精简容易二次开发（极其轻量），融合了 search engines + web scraping + LLM，非常适合被剥离部分核心逻辑融合到我们现在的流水线中。

3. **langchain-ai/open_deep_research** (1万+ Star)
- **机制**: 由 Langchain 官方下场发布的基于 LangGraph 的开源深度调查特工。主要借助 LangChain 框架本身的图计算管线特性。
- **优点**: 稳定且工业级可插拔，适合长期运转在需要流状态管理的企业级 Agent Pipeline 中。

## 对本项目的启示
目前 AI-Article-Publisher（写作机器人）内自研的 `core/researcher_v2.py` 虽然已经跑通了初步逻辑，但仍是个简易版的爬虫。要达到工业级抗幻觉和高信息密度，我们可以考虑将 `gpt-researcher` 或核心理念进行剥离，作为独立的子插件集成在下一代写作流水线（V3）内。

## 🔍 聚合检索引擎底座推荐 (Meta-Search Engines)

除了上述的 Agent 逻辑框架外，在底层的数据搜索（Information Retrieval）层，我们也调研了开源界最顶级的聚合搜索基建，用于替代现有的简易/易风控的单点爬虫。

4. **searxng/searxng** (2.5万+ Star)
- **状态**: 绝对统治地位的开源元搜索引擎（Meta-search engine）。
- **机制**: 在本地或云端通过 Docker 部署后，将对外暴露一个极简的 API（或 Web UI）。当你向它发送一个搜索词时，它会在后台**并发请求 Google、Bing、Baidu、DuckDuckGo、Qwant 等 70 多个搜索引擎**，然后对结果进行去重、清洗，直接返回干净的 JSON。
- **优点**: 它是目前解决“被谷歌/百度弹验证码、封杀 IP”的最佳方案。目前市面上大部分商业 AI 搜索应用（如 Perplexica、Local Deep Research）的底层全都在白嫖它。
- **对本项目的启示**: 如果我们未来的 V3 爬虫节点因为高频搜索被 DuckDuckGo 或百度拉黑，直接在 43.134.234.4 服务器上起一个 SearXNG 的 Docker 容器作为搜索代理中枢，我们的 Python 代码只需要发一个干净的 HTTP GET 请求，就能一网打尽中外所有引擎的优质结果链路，彻底告别写各种复杂反爬正则的痛苦。
