# 🏛️ AI Article Publisher V2 - 模块化可插拔架构工程白皮书 (Master Architecture & Tech Spec)

> 生效时间：2026-02-24
> 设计原则：低耦合、高内聚、降维无感降级、纯净隔离沙盒、**极致去公网外部依赖化**。

---

## 一、 系统工程基座：面向接口的插件总线设计

本系统彻底摒弃过程式脚本流。使用一主多从的星型拓扑架构。所有大模块均必须设计为**无副作用、返回标准化实体的独立包 (Independent Packages)**。

### 1.1 中枢控制：集线器引擎 (`core/pipeline_v2.py`)
*   **形态**: Python 原生过程调度器。
*   **通信协议**: 各个 Plugin 入口函数必须接收与返回标准化 `Dict` 对象。如果模块报错或配置为 `False`，通过 `try-except` 或 `if not config` 进行平滑跳过，绝不允许阻塞下游（Graceful Degradation）。
*   **入参配置**: 读取根节点 `pipeline_config.json` 的二叉树型 Boolean 开关群。

---

## 二、 核心五大插件工坊 (The Pluggable Factory)

### 📦 Plugin 0: 原始矿脉 (`sources/`) —— (作为基础设施保留的孤立进程)
*   **架构占位**: 这个模块其实并不是在 `pipeline_v2.py` 执行时即时调用的，它是一条长期蛰伏在系统后台的“矿车”，由 Linux `crontab` 独立管理。
*   **任务定义**: 定时去刮擦所有的 `DailyHotApi/RSSHub` 平台，往文件系统丢 JSON 尸块供下游调用。
*   **输出约定**: `@daily /data/hotnews/..._unified.json`

### 🧠 Plugin 1: 智能选题与沙砾提纯 (`topic_discovery`)
**目标**: 将 3000 多条离散的新闻点子，捏合成至多 5 个宏观爆款选题方案 (Topic Proposals)。
*   **A. 语义聚类打桩机 (`semantic_cluster.py`)**
    *   **技术选型**: `scikit-learn` 内的 `TfidfVectorizer` + `DBSCAN` 聚类算法。
    *   **入参/出参**: In: `daily_unified.json` -> Out: 包含了 20 个簇的 List。同一事件底下的全部报道被归入一个簇中。
*   **B. 选题决策引擎 (`topic_selector.py`)**
    *   **技术选型**: LangChain/LLM 原生 `DeepSeek-r1-free` 调用。
    *   **职责**: 向大模型下发这 20 个簇的摘要。让大模型输出最具争议性的选题、自带的核心角度 (Angle) 以及一个吸睛备选标题。
    *   **标准化输出**: 返回统一对象 `TopicObject { "title": "...", "angle": "...", "keywords": ["..."], "cluster_source_ids": ["..."] }`。

### 📡 Plugin 2: 内网巨型数据回采库/情报包 (`information_retrieval`)
**目标**: 【彻底抛弃 Brave/Google 搜索】，在确认好 `TopicObject` 后，通过内网爬犁搜刮所有的支撑事实和草根情绪，打成一个“防幻觉数据垫本 `Fact-Pack`”。
*   **A. 历史热网探雷车 (`hot_warehouse_miner.py`)**
    *   **技术选型**: 原生 Python 多正则匹配 / 倒排索引 (如果有 LanceDB 即可用它，若无则纯代码扫描)。
    *   **职责**:拿着 `TopicObject.keywords` 再一次扎进 `data/hotnews/daily_unified.json` 大库，把这个词在网易、36氪、什么值得买等几十个平台的**原标题、下挂短介、爬取排名**全刮出来。充当宏大事实基座。
*   **B. 戾气情绪吸尘器 (`domestic_sniffer.py`)**
    *   **技术选型**: `requests.get` 请求本机的 `localhost:1200` (原有基础设施 RSSHub)。
    *   **职责**: 发送诸如 `/zhihu/search/{keyword:url_encoded}?format=json` 或小红书路由的请求，把热榜评论扒下来，补充最接地的“金句情绪”。
*   **标准化输出**: 一个体积庞大、信噪比极高的 JSON 文本块组合 `Fact-Pack { "facts": [...], "emotions": [...] }`。

### 🏭 Plugin 3: 多端闭门写作编辑部 (`article_generator`)
**目标**: 系统最不可替代的绝对护城河！禁止它发起哪怕一个网络请求，断绝其所有的幻觉渠道，唯一的信息来源只有上面的 `Fact-Pack`。而且它本身完全可以脱离流水线接客（只要通过 CLI 传给它一句话，它自己就能跑完生成）。
*   **A. 钢筋解剖手 (`outliner.py`)**
    *   **技术选型**: 调用拥有强大逻辑树分割能力的模型 (如 `DeepSeek-Reasoner`)。
    *   **职责**: 吃进 `Fact-Pack`，吐出标准的 JSON 树状分论点（第一部分：铺垫；第二部分：转折及引用；第三部分：升华）。必须在对应部分塞入要引用的证据条目以防止瞎编。
*   **B. 黑箱织肉厂 (`writer_agents.py`)**
    *   **技术选型**: Python 原生 `asyncio` 并行发送 3 次 LLM 请求，或用 OpenClaw `sessions_spawn` 构建基于隔离环境的 Sub-agent。
    *   **职责**: 3 位赛博写手认领各自分论点并排撰写草稿，由于同时处理且拥有各自限定的 `Fact-Pack` 区块，文本水分将被无限挤压，返回纯正致密的干段落。
*   **C. 毒舌裁判长 (`editor_room.py`)**
    *   **技术选型**: 带状态循环的 LLM 对话回路 (`While Ping-Pong Loop`, Max-Turns=2)。
    *   **职责**: 拼接并读完通稿后，带入“虎嗅资深极客主编”性格模板。挑出“滥用套话”、“废话多”、“未引用确凿数据”等问题并要求返回重写！通关后吐出 Markdown 成片定稿！

### 🎨 Plugin 4: 微信原生排版与图文生成基站 (`visual_and_layout`)
**目标**: 将程序员审美粗暴的 `Markdown` 彻底埋葬，转化为新媒体顶级富文本表现层。
*   **A. 动态表图渲染机 (`code_illustrator.py`)**
    *   **技术选型**: Python 沙盒内执行 `matplotlib`。
    *   **职责**: 系统探测到文本包含连续折线级参数流时，动态生产并运行 Py 脚本写出高清大图（替代 AI 虚假生图带来的不实感），抛出图床链接并进行替换。（*如果此节点未开启配置，本环自动熔断无视*）。
*   **B. CSS 封装工 (`mdnice_renderer.py`)**
    *   **技术选型**: 结合包 `markdown2` 或 `mistune` 配合抽取自开源项目 `mdnice` 的行内高级 CSS 样式字典。
    *   **职责**: Markdown 转内联 `style=` 的微信独占 HTML 高爆文图。

### 🛡️ Plugin 5: 生死卡口飞书核验闸 (`publishers`)
**目标**: 作为系统唯一触碰外网输出的最终执行件，这里掌管着“封号防范”和“发送放行”的命脉。
*   **A. 投递展示橱窗 (`feishu_reviewer.py`)**
    *   **技术选型**: 挂载 OpenClaw 的 `feishu_doc` 原生级插件模块。
    *   **职责**: 将渲染好的成稿扔进指定审查群的只读飞书文档（不惊扰微信大盘接口）。
*   **B. Cron 倒悬钩锁 (Approval Poller)**
    *   **技术选型**: `openclaw system:cron` 结合 `re` 匹配。
    *   **职责**: 主程序到飞书发完之后，这部分线程挂起死亡或移交 cron 定期查岗。如果在文档末看到 `@发布` 等字眼，释放最终拦截权。向 `wechat_pusher.py` (内置 `wemp-operator` 引擎) 下达微信草稿发送指令。
