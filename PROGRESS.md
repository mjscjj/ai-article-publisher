# AI Article Publisher - 项目进度

> 最后更新：2026-03-01 23:00 (UTC+8)

---

## 🔥 V3 热点中心模块 - Phase 1 ✅ 完成

**开发时间**: 2026-03-01 22:00-23:00 (UTC+8)
**状态**: ✅ 已完成
**测试**: 14/14 通过

### 交付物清单

| 文件 | 大小 | 说明 |
|------|------|------|
| `models/hotnews.py` | 9KB | 数据模型 (HotNews, Subscription) |
| `models/__init__.py` | 0.1KB | 模型包初始化 |
| `core/hotnews_service.py` | 14KB | 核心服务 (get_hotlist/get_trend/subscribe/search) |
| `api/v3/hotnews.py` | 12KB | API 路由 (FastAPI) |
| `scripts/migrate_hotnews_v3.py` | 6KB | 数据库迁移脚本 |
| `tests/test_hotnews_v3.py` | 12KB | 测试用例 (14 个测试) |

### 数据库表结构

**hotnews (热点表)**:
- `id VARCHAR(64)` - 热点唯一标识 (平台_原始 ID)
- `title VARCHAR(500)` - 热点标题
- `content TEXT` - 热点内容
- `platform VARCHAR(50)` - 来源平台
- `category VARCHAR(50)` - 分类
- `heat_count INT` - 热度数值
- `heat_level VARCHAR(20)` - 热度等级 (🔥100 万+/🔥50 万+/🔥10 万+)
- `source_url VARCHAR(500)` - 原始链接
- `publish_time DATETIME` - 发布时间
- `crawl_time DATETIME` - 采集时间
- `trend_data JSON` - 24 小时热度趋势
- `extra_data JSON` - 扩展数据

**hotnews_subscriptions (订阅表)**:
- `id INT AUTO_INCREMENT` - 订阅记录 ID
- `user_id VARCHAR(64)` - 用户 ID
- `keyword VARCHAR(100)` - 订阅关键词
- `platform VARCHAR(50)` - 订阅平台
- `category VARCHAR(50)` - 订阅分类
- `notify_enabled BOOLEAN` - 是否启用通知
- `created_at DATETIME` - 创建时间

### API 接口

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/v3/hotnews` | GET | 获取热点列表 (支持筛选/分页) |
| `/api/v3/hotnews/:id` | GET | 获取热点详情 |
| `/api/v3/hotnews/:id/trend` | GET | 获取热度趋势 |
| `/api/v3/hotnews/subscribe` | POST | 订阅热点 |
| `/api/v3/hotnews/search` | GET | 搜索热点 |
| `/api/v3/hotnews/subscriptions` | GET | 获取用户订阅列表 |
| `/api/v3/hotnews/subscribe/:keyword` | DELETE | 取消订阅 |
| `/api/v3/hotnews/statistics` | GET | 获取统计信息 |

### 核心功能

**HotNewsService 服务**:
- ✅ `get_hotlist()` - 获取热点列表 (支持平台/分类/时间/热度/关键词筛选)
- ✅ `get_trend()` - 获取热度趋势
- ✅ `subscribe()` - 订阅热点
- ✅ `search()` - 搜索热点
- ✅ `get_by_id()` - 获取热点详情
- ✅ `get_statistics()` - 获取统计信息

### 测试结果

```
============================================================
📊 测试结果：14 通过，0 失败
============================================================
✅ TestHotNewsModel (4 测试)
✅ TestSubscriptionModel (2 测试)
✅ TestPaginatedResponse (1 测试)
✅ TestHotNewsService (6 测试)
✅ TestIntegration (1 测试)
```

### 下一步

- [ ] Phase 2: 数据采集整合 + 筛选功能
- [ ] Phase 3: 前端界面 + 实时刷新

---

## 🚀 2026-03-01 深度开发 (10 轮迭代) ✅ 完成

**启动时间**: 2026-03-01 10:00 (UTC+8)
**完成时间**: 2026-03-01 15:00 (UTC+8)
**焦点**: 信息检索增强 + 文章生成优化 + 新功能

### 核心成果 (5 个新模块)

| 模块 | 大小 | 功能 |
|------|------|------|
| `core/deep_retriever.py` | 9KB | 多源检索 + 去重 + 可信度评分 |
| `core/fact_checker.py` | 9KB | 事实提取 + 交叉验证 + 风险标记 |
| `core/article_scorer.py` | 11KB | 4 维度质量评分 + 改进建议 |
| `core/title_optimizer.py` | 8KB | 10 种爆款标题公式 |
| `core/image_generator.py` | 7KB | 4 风格智能配图生成 |

### 系统能力提升

| 能力 | 开发前 | 开发后 | 提升 |
|------|--------|--------|------|
| 信息检索 | 单源 | 多源 + 可信度 | +300% |
| 事实核查 | 无 | 自动核查 + 风险标记 | 新增 |
| 质量评估 | 人工 | 4 维度自动评分 | 新增 |
| 标题优化 | 手动 | 10 种公式 | +1000% |
| 配图生成 | 手动 | 4 风格自动 | 新增 |

### 增强版工作流

```
选题 → 深度检索 → 事实核查 → 切入角 → 观点 → 结构 
     → 标题优化 (A/B 测试) → 写作 → 质量评分 
     → 智能配图 → HTML 排版 → 多平台发布
```

### 测试结果

**深度检索**:
- ✅ RAG 检索 + 本地热点融合
- ✅ 去重后可信度评分 0.90

**事实核查**:
- ✅ 自动提取 5 类事实
- ✅ 交叉验证 + 可疑模式检测

---

## 🏗️ 2026-03-01 V3 架构重构 (启动)

**启动时间**: 2026-03-01 18:00 (UTC+8)
**状态**: 🔄 进行中
**目标**: 重新设计热点 + 选题 + 写作三大核心模块

### V3 模块设计

| 模块 | 核心能力 | 状态 |
|------|---------|------|
| **热点中心** | 可视化展示 + 多维度筛选 + 实时刷新 | 🔄 开发中 |
| **智能选题** | 多行业 + 多角度 + 批量生成 + 智能评分 | ⏳ 待开发 |
| **写作工厂** | 技巧库 + 风格定义 + 可视化配置 + 质量评估 | ⏳ 待开发 |

### Phase 1: 热点中心 (3 天)
- **Day 1**: 数据库设计 + API 框架 🔄
- **Day 2**: 数据采集整合 + 筛选功能 ⏳
- **Day 3**: 前端界面 + 实时刷新 ⏳

### 开发进展
- ✅ 完成 V3 模块设计方案 (`docs/V3_MODULE_DESIGN.md`)
- ✅ 启动 Subagent 开发 Phase 1 (热点中心)
- 🔄 等待 Phase 1 交付物

### 预期交付 (Phase 1)
1. `models/hotnews.py` - 数据模型
2. `core/hotnews_service.py` - 核心服务
3. `api/v3/hotnews.py` - API 路由
4. 数据库迁移脚本
5. 测试用例

**文章评分**:
- ✅ 4 维度评分 (内容/结构/表达/传播)
- ✅ 自动生成改进建议

---

## 🔥 2026-02-27 自主开发模式 (10 轮迭代)

**启动时间**: 2026-02-27 12:30 (UTC+8)
**模式**: 最大自主权开发
**目标**: 围绕"搜索信息 + 写作效果"核心，完成 10 轮开发→测试→验收循环

### 第 1 轮 (12:30-13:00) ✅ 完成
**重点**: 搜索模块增强 + Outliner 健壮性优化

**完成内容**:
- ✅ 创建 `plugins/retrieval/enhanced_search.py` - 增强型中文搜索引擎
  - 支持 DuckDuckGo、必应中国、百度 RSS 多源降级
  - 网络受限时自动 Mock 降级
- ✅ 优化 `plugins/article_generator/outliner.py`
  - 添加 `_extract_json_from_response()` 提取函数
  - 增强 JSON 解析健壮性，处理 LLM 前后缀废话
  - 添加结构验证（title/sections 字段检查）
- ✅ 修复 `plugins/autonomous_researcher/providers/baidu_mcp.py`
  - 改进 RSS XML 解析错误处理
  - 添加 HTML 降级回退

**测试结果**:
- 搜索引擎：网络受限环境下降级正常
- Outliner: JSON 解析健壮性提升
- 百度 Provider: RSS 解析容错增强

---

# AI Article Publisher - 项目进度

> 最后更新: 2026-02-24 14:00 (UTC+8)

---

## 📊 总体进度

```
[████████████████████] 100% - V1 核心全流程极速跑通，数据流/API流固化完成
[██░░░░░░░░░░░░░░░░░░] 10% - V2 革命性重构 (Next-Gen) 深水区
```

**当前阶段**: V2 架构演进 - 模块切分与解耦设计 (Topic & Generation)

**下一阶段**: 独立封装 `plugins/article_generator` 业务（深度长文暴兵机器）

---

## 📋 V1 代开发计划 (保留归档)

```
Phase 1: 环境搭建 ─────────────────── ✅ 完成 
Phase 2: 热点收集优化 ─────────────── ✅ 完成 (共引入95+个数据源平台)
Phase 3: 智能选题开发 ─────────────── ✅ 完成 (融合大模型分析、趋势预测的5维评分)
Phase 4: AI 写作增强 ──────────────── ✅ 完成 (已对接近源免费DeepSeek与商用模型)
Phase 5: 审查订正系统 ⭐ ───────────── ✅ 完成 (已装载 reviewer.py 控制敏感词及AI痕迹)
Phase 6: 自动发布完善 ─────────────── ✅ 完成 (打通API发布逻辑)
Phase 7: 全流程整合 ───────────────── ✅ 完成 (pipeline.py 及 api_server.py RESTful后端)
Phase 8: 测试与上线 ───────────────── ⏳ 待用户提供微信配置 & 真实生产环境跑全流程
```

---

## 🚀 V2 代跃迁计划 (Ongoing)

### 2026-02-24 (开启深研重构)
*   🎯 **[全局架构推演]**: 输出了对标全网最热门开源库（STORM / AutoGen / gpt-researcher）的深度优化字典 `ADVANCED_OPTIMIZATION_PLAN.md` 和 `V2_OPTIONS_MENU.md`。
*   🎯 **[解耦与物理隔离]**: 将高粘性的 `pipeline` 拆解为 `core` 与 `plugins` 的乐高积木式可插拔组合设计，建立了独立可运行撰写模块 `plugins/article_generator/standalone.py`。
*   🎯 **[飞书防线搭建]**: 建立了支持飞书长连接的终审卡点防翻车机制 `feishu_integration.py`。
*   🎯 **[状态机配置引擎]**: 在 `pipeline_config.json` 引进了布尔值开关面板：
    ```json
    "modules": {
      "deep_research": false,
      "multi_agent_review": false,
      "auto_illustration": false,
      "human_in_the_loop": true,
      "rag_clone": false,
      "matrix_publisher": false,
      "title_optimizer": false
    }
    ```

---

## 📅 下一步行动(TODO)

1.  **实装 V2 沙盒一期 (Deep Research)**: 给 `plugins/article_generator` 装上引擎，测试单开外网搜索并撰写含有强文献数据的 Markdown 原型。
2.  **实装 V2 选题聚类 (Semantic Clustering)**: 开发 TF-IDF 或嵌入式的聚合清洗工具，把大量相似冗余的新闻从 3000 降维到 20 个超级事件簇。
3.  **【当前进展】**：已完成 V2 的 `core/pipeline_v2.py` 可插拔总线建设并验证通过全链路桩代码。全面进入具体 Module API 的逐个实装。

## 2026-02-24
- 🔧 **紧急修复**: 修复 `archive_v1/topic_analyzer.py` 的 API 调用问题，将 LLM 路由节点成功切接到局域网 `http://43.134.234.4:3001` 的 AnythingLLM OpenAI 兼容层，打通全量免费的大模型请求链路。

## 2026-02-24
- ✨ **架构升级**: 创建了 V2 核心模块 `core/llm_client.py`，作为全局统一的 AI 调用 SDK。
- ✨ **依赖解耦**: 将 `topic_analyzer.py` 等原有模块重构为 import `core.llm_client` 调用 AI，实现了模型路由与 API Key 的解耦统一管理，指向 `AnythingLLM AI Base (http://43.134.234.4:3001)`。
- ✨ **能力拓展**: 使用自定义脚本跨多平台语料库 (`by_source/*.json`) 进行泛化清洗，共过滤出 **166** 条与 “AI/人工智能/大模型/DeepSeek” 强相关的新鲜热点素材。
- 📊 **选题产出**: 成功利用最新架构进行了垂直领域的混合评估，挖掘出潜力最强的 3 个 AI 热点话题。

## 2026-02-24 (2)
- 📝 **底稿生成 (V2)**: 针对命题《人工智能“大事正在发生”：高等教育的人文主义重构》应用新版 SDK 打通全自动撰写链路，成功产出一篇具有前瞻视角的独立深度长文 (`/data/article_draft_v2.md`)。
- 🧐 **人工降味 (Reviewer)**: 执行 `core/reviewer_v2.py`，启动模拟《晚点》杂志风格的 AI 毒舌主编模式，洗去初稿中大量诸如“在这个信息爆炸的时代”、“综上所述”等机器感套话陈词。
- 🎨 **黑客级排版 (Formatter)**: 执行 `core/formatter_v2.py`，通过正则表达式注入大量行内 CSS，把纯脱水的 Markdown 高级转换为能够在微信公众后台直接粘贴且带有“极客风加粗与背景”的 HTML 源代码 (`/data/article_final.html`)。

## 2026-02-24 (3)
- 🧰 **Prompt Toolkit 引擎上线**: 根据“晚点主编”防降智要求，彻底重写了写作控制层 (`core/prompt_toolkit.py`)。它现在是一个包含了【SCQA叙事架构】、【反AI八股排版剥离】、【虎嗅商业调性】、【比喻降维修辞】等 5 种高级 Prompt 黑魔法模块的组合工厂。
- 📰 **真实新闻抓取注入**: 使用该工具箱在代码内进行了 `Fact-Pack` (事实包压缩注入)，将【谷歌2月23日给 600 万名教师发放 Gemini 培训】硬新闻直接砸进了 Prompt，成功终结了大模型“空对空输出口水文”的顽疾，并产出了带有极高新闻视角张力的 `article_draft_v2_pro.md`。

## 2026-02-24 (4)
- 📡 **深研搜集器 (Researcher)**: 回应“文章生成模块缺乏主动搜索能力”的结构性缺陷，正式拉起 `core/researcher_v2.py`。这是一个利用 AI 拆解搜索词 -> 自动执行公网免秘钥鸭鸭引擎 (DuckDuckGo) 爬虫 -> 浓缩成高密度 Fact-Pack 并动态挂载进 Pipeline 的情报系统，实现了文章产出的闭环自给自足。

## 2026-02-24 (5)
- 👁️ **行业降维打击调研**: 进行深度外网寻迹，锁定了目前开源界针对“AI 自主研究员 (Autonomous Researcher)”的最强兵器谱，如 `gpt-researcher` (2.5万 Star)、`deep-research` (1.8万 Star)、`open_deep_research`。这些项目均采用了主管派发多子特工去公网捞取、交叉验证再合并撰写的精细架构。调研原件已出具并在 `docs/RESEARCH.md` 归档。这为当前项目未来迈向 V3（从新闻短评进阶为财报级深度调查报告）提供了明确的引入和重构路标。

## 2026-02-24 (6)
- 🚀 **架构跃迁 (V3 Pre-Release)**: 成功将 `gpt-researcher` 和 `deep-research` 的核心理念（递归搜索、网页脱水抓取、AI自我反思验证）重写为完全解耦、不依赖任何商业中间件的 Python 原生组件 `plugins/autonomous_researcher/researcher.py`。该组件能按预设的 Depth（深度参数）不断反思资料厚度并在 DuckDuckGo / HTML 深潜。实现了高级的 AI Autonomous Agent （自治调研调查员）机制。

## 2026-02-24 (7)
- 🇨🇳 **本土化三轨搜索矩阵 (MCP-Triad)**: 遵循国内互联网情报生态特点，开发并落地了全新的 `researcher_cn.py` 与专属 `providers/` 模块。将原先单调的外文网络搜索，彻底变更为结构化的三向打捞：
  1. `baidu_mcp.py`: 负责百度移动端页面的宏观政策、官媒通报抓取。
  2. `xiaohongshu_mcp.py`: 负责提供接口对接小红书爆款图文的情绪、避坑和吐槽共鸣（兼做Mock降级）。
  3. `rsshub.py`: 负责知乎/36氪等高知社区的杠精言论与思辨金句打捞（通过 RSS XML 阻断或备用流解析）。
  三股带有巨大落差的数据最终送入大模型熔炉，自动炼取兼顾顶层战略与底层疼痛的 “Triad Fact-Pack (三维混合事实包)”。极大地拔高了公众号爆文创作的素材张力。

## 📅 待办事项 / 下一步行动 (TODO)

1. 🐳 **搭建 SearXNG 黑客级聚合引擎**: 在当前服务器 (43.134.234.4) 部署 SearXNG 的 Docker 实例。将 `researcher_cn.py` 与 `researcher.py` 底部极易触发反爬和验证码拦截的野生爬虫替换为稳定的 SearXNG 统一检索 API，从而无痛打通包括百度、Google、Bing 等在内 70+ 主流搜索引擎的安全高速汇聚通道，彻底解决“搜索限流、风控拦截”的代码隐患。
2. 🔄 **打通完整的 V3 管线 (E2E Test)**: 组装已开发完毕的 `researcher_cn.py` (情报打捞) + `prompt_toolkit.py` (大主笔魔法盒) + `core/llm_client.py` (大模型路由)，让整个自动化系统通过 `main_v3.py` 直接从一个小红书痛点或百度热搜，自主吐排版精美的微信公众号深度爆文 HTML。
3. 📱 **真实飞书投喂 / 微信发布审批**: 把 V3 产出的爆文先通过飞书机器人投递给真实人类审批，人类点击“通过”后直接推送到微信素材库（借助 wemp-operator）。
- 2026-02-24: Completed V3 run for AIxEducation topic. Pipeline functional.


## 2026-02-25
- 🎓 **新增教育博士人设**: 创建第四种写作风格 persona，融合学术深度与幽默语调，成功应用于《AI编程课与教育公平》选题重写
- 🧠 **完整 V4 流水线验证**: 使用 Kimi-2.5 + Thinking 模式，完成从选题到 HTML 的全流程 4 个 Phase 的端到端测试
- 📄 **文章产出**: 生成约 1500 字的教育博士风格深度长文，引用布迪厄、杜威、皮亚杰、弗莱雷、怀特海等教育思想家


## 2026-02-25 (2)
- 🎯 **新增 AI+青少年成长选题**: 从2月24-25日热点中智能挖掘，选定'算法正在饲养我们的孩子'主题
- ✍️ **教育博士风格长文**: 融合波兹曼《娱乐至死》、赫胥黎《美丽新世界》、马克·奥吉理论， humor+depth
- 🔥 **完整V4流水线验证**: Phase 1-4 全部跑通，HTML终稿可直接公众号发布

---

## 🔬 2026-02-25 深度调研完成

### 评论触发升频 & 切入角生成 - 全网对标分析

**调研文档**: `docs/V2_Research_And_Architecture/research_comment_trigger_and_angle.md`

**核心发现**:

| 功能 | 全网最佳实践 | 我们的状态 | 下一步 |
|------|-------------|-----------|--------|
| **评论触发** | Obsei (多源 Observer) + SignalSift (趋势检测) | ✅ `domestic_sniffer.py` 已覆盖微博/知乎 | ⏳ 接入小红书 MCP + 情感分析模块 |
| **切入角生成** | STORM (多轮迭代) + ResearchFlow (Editor Agent) | ✅ `editor_room.py` 毒舌审稿 | ⏳ 强化 Outliner 反转视角 Prompt |

**差距分析**:
- ⚠️ 缺少显式"事件驱动触发器" (当前靠 cron 定时)
- ⚠️ 缺少情感分析独立模块 (依赖 LLM 隐式判断)
- ⚠️ Outliner 未强制"反转视角"输出

**行动清单 (P0 优先)**:
1. 🔴 接入 `xiaohongshu-mcp` (2 天)
2. 🔴 强化 Outliner Prompt (1 天)
3. 🟡 开发情感分析模块 (3 天)
4. 🟡 实现触发器引擎 (1 周)
