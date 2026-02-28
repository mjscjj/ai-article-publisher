# 🎯 评论触发升频与切入角生成 - 全网深度调研

> **调研时间**: 2026-02-25
> **调研目标**: 针对"评论触发升频"和"文章切入角生成"两大核心功能，扫描全网开源方案与最佳实践

---

## 📊 一、评论触发升频 (Comment-Driven Trigger Escalation)

### 1.1 核心定义

**问题**: 如何基于社交媒体评论的热度、情绪、争议性，自动提升选题优先级并触发写作流程？

**关键指标**:
- 评论数量阈值 (如 >100 条)
- 情感极性分布 (正面/负面/争议)
- 热词密度 (关键词在评论中出现频率)
- 互动率 (点赞数/评论数比值)

---

### 1.2 全网开源方案对标

#### [Obsei](https://github.com/obsei/obsei) ⭐⭐⭐⭐
- **定位**: Low-code AI 自动化平台，支持 Social Listening
- **核心能力**:
  - **Observer**: 抓取 Twitter、Reddit、Facebook、YouTube、Google Reviews 等评论
  - **Analyzer**: 情感分析、分类、PII 识别
  - **Informer**: 推送至 Slack、Jira、Elasticsearch 等
- **可借鉴点**:
  - 多源评论统一接入架构
  - 状态持久化 (SQLite/Postgres)，适合定时任务
  - 模块化设计 (Source/Analyzer/Sink 三段式)
- **局限性**:
  - 国内平台支持弱 (无微博、知乎、小红书)
  - 依赖官方 API，反爬能力弱

#### [SignalSift](https://github.com/thebiglaskowski/signalsift) ⭐⭐⭐⭐
- **定位**: 个人社区情报工具，生成 Markdown 报告
- **核心能力**:
  - 监控 Reddit、YouTube、Hacker News
  - 关键词过滤 + 语义匹配 (FAISS 加速)
  - **趋势检测**: 识别升温/降温话题
  - 自动生成 Markdown 报告
- **可借鉴点**:
  - **趋势评分算法**: 基于时间窗口的热度变化率
  - 语义去重 (Embedding + FAISS)
  - RSS 免登录抓取 (规避 API 限制)
- **局限性**:
  - 仅支持英文平台
  - 无触发机制 (仅生成报告，不自动执行下游任务)

#### [Universal AI Lead Scraper](https://github.com/Drift-Sphere/Universal-AI-Lead-Scraper-Signal-Engine) ⭐⭐⭐
- **定位**: n8n 工作流，高意向销售线索挖掘
- **核心能力**:
  - 通过 Google Search 聚合 8+ 平台信号
  - LLM (Llama 3 via Groq) 资格筛选
  - **紧急度分级**: Low/Medium/High
  - Telegram 即时推送
- **可借鉴点**:
  - **紧急度检测 Prompt**: "这是一条高意向线索吗？为什么？"
  - 多渠道信号归一化
- **局限性**:
  - 依赖 n8n 编排框架
  - 侧重销售场景，非内容创作

---

### 1.3 我们的实现方案对比

| 功能模块 | 全网最佳实践 | ai-article-publisher 现状 | 差距分析 |
|---------|-------------|------------------------|---------|
| **评论抓取** | Obsei: 多平台统一 Observer | `domestic_sniffer.py` (RSSHub 微博/知乎) | ✅ 已覆盖国内主流，但缺少小红书/抖音 |
| **情感分析** | Obsei: 内置 Transformer 模型 | 暂无独立模块，依赖 LLM 隐式判断 | ⚠️ 需补充轻量级情感分类器 |
| **热度评分** | SignalSift: 时间窗口趋势算法 | `topic_selector.py` 5 维评分 (含评论数) | ✅ 已有基础，可优化趋势权重 |
| **触发升频** | Universal Lead Scraper: 紧急度分级 | 暂无显式触发器，靠 cron 定时执行 | ⚠️ 需增加事件驱动机制 |
| **告警推送** | 全部支持 (Slack/Telegram) | 飞书文档终审 (`feishu_integration.py`) | ✅ 已实现，但非实时 |

---

### 1.4 建议升级路线

#### Phase 1: 补全评论数据源 (1 周)
- 接入 `xiaohongshu-mcp` (小红书评论)
- 接入 Douyin/Bilibili API (视频评论)
- 目标：覆盖 90% 中文主流平台

#### Phase 2: 情感分析模块 (3 天)
- 方案 A: 本地 `transformers` 库 (BERT-chinese-sentiment)
- 方案 B: 免费 API (百度 NLP / 腾讯文智)
- 输出：每条评论的情感标签 (正/负/中立) + 置信度

#### Phase 3: 触发器引擎 (1 周)
```python
# plugins/topic_discovery/comment_trigger.py
class CommentTrigger:
    def __init__(self, thresholds: dict):
        self.thresholds = thresholds  # {min_comments, min_sentiment_score, ...}
    
    def check(self, topic_id: str, comments: list) -> bool:
        # 规则引擎：
        # 1. 评论数 > 阈值
        # 2. 负面情感占比 > 30% (争议性)
        # 3. 热词密度 > 阈值
        # 满足任意 2 条 → 触发升频
        pass
    
    def escalate(self, topic_id: str):
        # 动作：
        # 1. 提升选题优先级 (写入 Redis 队列)
        # 2. 发送飞书告警
        # 3. 立即启动写作流程 (绕过定时任务)
        pass
```

---

## 🎨 二、文章切入角生成 (Angle Generation)

### 2.1 核心定义

**问题**: 如何让 AI 生成的文章避免"官方通稿"，具备独特视角、反转逻辑、锐度？

**关键要素**:
- 反差感 (预期 vs 现实)
- 利益相关者冲突 (谁受益/谁受损)
- 历史类比 (类似事件回顾)
- 数据支撑 (硬核证据)

---

### 2.2 全网开源方案对标

#### [ResearchFlow](https://github.com/amitksingh2103/ResearchFlow-Agentic-AI-Research-Content-Automation-System) ⭐⭐⭐⭐
- **定位**: 多 Agent 自主研究 + 内容生成系统
- **核心能力**:
  - 自主网页搜索 → RAG 处理 → 多格式输出
  - **多角色 Agent**: Researcher、Writer、Editor、SEO Specialist
  - 一次性生成 Blog、LinkedIn、Newsletter、X Thread
- **可借鉴点**:
  - **Editor Agent**: 专门负责"挑毛病"，要求 Writer 重写
  - 多角度并行撰写 (同一主题，不同口吻)
- **局限性**:
  - 依赖 CrewAI 框架，学习曲线陡
  - 无中文优化

#### [STORM (Stanford)](https://github.com/stanford-oval/storm) ⭐⭐⭐⭐⭐
- **定位**: 斯坦福官方项目，长文深度研究生成
- **核心能力**:
  - **多轮检索**: 先广搜→再深挖→验证矛盾点
  - **大纲迭代**: 根据检索结果动态调整骨架
  - 引用溯源 (每条论述附带来源 URL)
- **可借鉴点**:
  - **视角多样性 Prompt**: "从经济学家/社会学家/技术专家三个角度分析此事件"
  - 自我反思机制："我是否遗漏了反面证据？"
- **局限性**:
  - 学术导向，文风偏严肃
  - 计算成本高 (多次检索 + 多轮 LLM)

#### [Medium-Article-Generator](https://github.com/Nikhil-MLOPs/Medium-Article-Generator) ⭐⭐⭐
- **定位**: 生产级 AI 写作系统
- **核心能力**:
  - Writer + Reviewer + **Editor-in-Chief** 三级审核
  - Editor-in-Chief 负责全局流畅度与爆款结构
- **可借鉴点**:
  - **总编 Prompt**: "这篇文章的 Hook 是什么？前 3 段能否留住读者？"
- **局限性**:
  - 代码较旧 (2023 年)
  - 无多 Agent 并发

---

### 2.3 我们的实现方案对比

| 功能模块 | 全网最佳实践 | ai-article-publisher 现状 | 差距分析 |
|---------|-------------|------------------------|---------|
| **大纲生成** | STORM: 动态迭代骨架 | `outliner.py` (一次 LLM 调用生成 JSON) | ⚠️ 缺少多轮 refinement |
| **视角多样性** | STORM: 多学科角度 Prompt | 暂无显式控制 | ⚠️ 需增加"视角切换"指令 |
| **毒舌审稿** | ResearchFlow: Editor Agent | `editor_room.py` (暴躁主编人设) | ✅ 已实现，效果待验证 |
| **引用溯源** | STORM: 每条论述带 URL | `fact_packer.py` 打包事实，但未强制引用 | ⚠️ 需增强引用约束 |
| **反差感营造** | Medium: Editor-in-Chief 审 Hook | 暂无 | ⚠️ 需补充"反转视角"Prompt |

---

### 2.4 建议升级路线

#### Phase 1: 强化 Outliner (3 天)
```python
# plugins/article_generator/outliner.py 升级
SYSTEM_PROMPT = """
你是一个冷酷的新闻骨架解剖手。必须输出严格的 JSON。

【强制要求】
1. sections 恰好 3 个，且每条都强关联 fact_pack 中的事实点。
2. 必须包含一个"反转视角"小节 (如："看似 X，实则 Y")。
3. 必须指定每个小节要引用的上游事实 (quote_req)。
4. 禁止输出除 JSON 外的任何文本。

【视角模板】(随机选 1 个)
- 利益冲突视角：谁受益？谁受损？
- 历史类比视角：3 年前发生过类似事件吗？
- 数据打假视角：表面数据 vs 真实数据
- 底层逻辑视角：第一性原理拆解
"""
```

#### Phase 2: 多 Agent 视角并发 (1 周)
```python
# plugins/article_generator/perspective_agents.py
PERSPECTIVES = {
    "economist": "从成本收益、市场格局、商业模式角度分析",
    "sociologist": "从社会结构、群体心理、文化变迁角度分析",
    "technologist": "从技术原理、工程实现、创新瓶颈角度分析",
    "critic": "从伦理风险、权力失衡、人性异化角度分析",
}

async def generate_multi_perspective(topic: str, fact_pack: dict):
    tasks = []
    for role, prompt in PERSPECTIVES.items():
        tasks.append(llm_call(role_prompt, topic, fact_pack))
    results = await asyncio.gather(*tasks)
    return merge_perspectives(results)
```

#### Phase 3: STORM 式大纲迭代 (2 周)
```
Loop (max 3 轮):
  1. 生成初始大纲
  2. 调用检索器查找"反面证据"
  3. 如果找到矛盾点 → 修改大纲增加"争议"小节
  4. 如果信息不足 → 追加检索词，继续搜索
  5. 满意度达标 → 退出循环
```

---

## 📋 三、总结与行动清单

### 3.1 评论触发升频

| 优先级 | 任务 | 预计工时 | 依赖 |
|-------|------|---------|------|
| 🔴 P0 | 接入 `xiaohongshu-mcp` | 2 天 | MCP 工具可用 |
| 🟡 P1 | 开发情感分析模块 | 3 天 | 无 |
| 🟡 P1 | 实现触发器引擎 | 1 周 | 情感分析完成 |
| 🟢 P2 | 飞书实时告警 | 2 天 | 触发器完成 |

### 3.2 切入角生成

| 优先级 | 任务 | 预计工时 | 依赖 |
|-------|------|---------|------|
| 🔴 P0 | 强化 Outliner (反转视角 Prompt) | 1 天 | 无 |
| 🟡 P1 | 多 Agent 视角并发 | 1 周 | 无 |
| 🟡 P1 | Editor Room 增加"Hook 检查" | 2 天 | 无 |
| 🟢 P2 | STORM 式大纲迭代 | 2 周 | 检索器稳定 |

---

## 🔗 四、参考资源

### 开源项目
- [Obsei](https://github.com/obsei/obsei) - Social Listening 全流程
- [SignalSift](https://github.com/thebiglaskowski/signalsift) - 趋势检测 + 报告生成
- [STORM](https://github.com/stanford-oval/storm) - 斯坦福长文研究系统
- [ResearchFlow](https://github.com/amitksingh2103/ResearchFlow-Agentic-AI-Research-Content-Automation-System) - 多 Agent 内容工厂

### 论文/文章
- STORM 论文: https://arxiv.org/abs/2402.14207
- gpt-researcher 技术解析: https://github.com/assafelovic/gpt-researcher

---

*最后更新: 2026-02-25 23:00 UTC+8*
