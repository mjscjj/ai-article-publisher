# 🧠 Autonomous Researcher (独立自治调研器)

这是一个完全零外部成本、零商业爬虫依赖的**深潜式独立 AI 调研引擎**。
它的设计灵感来源于 `gpt-researcher` 和 `deep-research`，剥离了它们臃肿的框架和高昂的 API(Tavily/Firecrawl) 费用，在 Python 原生环境中实现了**“假设与验证驱动的迭代式深网打捞”**。

## 🌟 核心特性 (Features)

1. **零成本探测 (Zero-Cost Scraping)**：底层对接 DuckDuckGo 无头 HTML 节点，并内建基于正则表达式的极简纯文本清洗器，直取网页正文。
2. **多视角分词 (Multi-perspective Queries)**：AI 主编不会直接去搜大词，而是将大命题拆解为 3-5 个极其精准的技术/商业/下沉等视角的关键词。
3. **自我反思与多轮下潜 (Self-Reflection & Iterative Depth)**：搜索完一轮后，AI 会自我阅读材料，如果发现“当前素材不足以支撑深度写作”，它会自动修正搜索词，发起更深一层的定向打捞（受 Depth 参数控制）。
4. **高压浓缩 (Fact-Pack Sinthesis)**：将高达数万字的网页噪音压缩成附带具体数据、极端观点的终极“事实包”。

## 🔌 接口规范 (API Reference)

将本模块作为独立 SDK 引入任意 Python 项目：

```python
from plugins.autonomous_researcher.researcher import AutonomousResearcher

# 必须提供一个用于对话的 LLM 回调函数
# 签名: def my_llm(prompt: str, system_prompt: str) -> str:
def my_llm_func(prompt, sys_prompt):
    return ask_ai(prompt, sys_prompt)

# 初始化研究员 (可指定最大下潜深度)
researcher = AutonomousResearcher(llm_callable=my_llm_func, max_depth=2)

# 启动深度调查
fact_pack = researcher.run("人工智能大模型对全球白领就业的真实冲击数据")

print(fact_pack)
```

## ⚙️ 工作流 (Workflow)

`[接收命题] -> [AI规划3个子查询] -> [DDG搜索] -> [抓取网页剥离HTML] -> [内存合并] -> [AI判别是否继续深潜] -> (若继续则循环) -> [最终提炼Fact-Pack]`

