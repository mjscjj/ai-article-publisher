# 📁 AI Article Publisher V2 - 目录结构与模块技术选型白皮书

为了彻底告别 V1 时代“大泥球 (Big Ball of Mud)”式的单体脚本堆砌模式，V2 全面进化为**【微内核+插件 (Core-Plugins)】**架构。
> **⚠️ 核心继承声明**: V1 阶段极为成功且极具价值的【每日定点被动热源采集器】（即 `sources/` 下统筹 95+ 个外部 API 或 RSS 热榜直接爬取、构建 3000 行庞大新闻库的机制）**非但未被削弱，反而正式上位为 V2 这张大网的正中心**。

---

## 🏗️ 顶层目录结构 (Root Structure)

```text
ai-article-publisher/
├── core/                # 🧠 [大脑] 核心微内核：负责控制流和状态管理
├── plugins/             # 🔌 [器官] 可插拔业务插件群：真正的干活工具库
├── data/                # 💾 [血液] 数据持久层：热点库、向量、产出归档
├── docs/                # 📜 [蓝图] 架构图纸与系统手册
├── sources/             # 🕸️ [进货区] 每日被动热点榜单抓取器 (继承自 V1)
├── tests/               # 🧪 [质检] 验证各模块的断言测试
├── archive_v1/          # 📦 [遗物] V1 单体时代的其余杂乱脚本备份
├── PROGRESS.md          # 🟢 全局开发进度锁
└── README.md            # 🟢 项目首页
```

---

## 🔌 Plugins (五大业务器官群及去 Brave 技术选型)

**(极简版概说：去除了一切依赖于外部收费接口或易被屏蔽的墙外探针，极致下潜重用本地资源)**

### 模块一：`plugins/topic_discovery/` (选题预处理与降噪选品)
*   只处理 `sources/` 扔给它的 3000 条生肉，提炼出顶配点子。不查全网。
*   **技术**: `scikit-learn` 轻量聚类 + DeepSeek 清洗 JSON。

### 模块二：`plugins/retrieval/` (【焕新】内网原生情报整合组 / The Researchers)
*   **重大调整**: **剥离了一切调用外部公网（如 Brave Search）的意图！**彻底把这个模块转变为“本地金库的高级拾荒者”。
*   **技术选型**:
    *   `hot_warehouse_miner.py` (热点聚能作手)：**不搜全网了**。大模型直接潜入我们硬盘里的 `data/hotnews/daily_unified.json`。比如遇到了“苹果放弃造车”的主题，它直接用 Python 从包含几十个平台的 Json Array 中瞬间刮出 25 条含有苹果和造车片段的各家热搜视角供文案汲取养料！
    *   `domestic_sniffer.py` (本土 RSSHub 探针)：利用本机服务器极其强悍的 `1200` 端口 `RSSHub` 服务，发送例如 `http://localhost:1200/zhihu/search/xxx` 请求。绕开封禁，直取深度骂战评论补充情绪。
*   **输出**: 极其纯正、完全取材于中华局域网的 `Fact-Pack` 垫本！

### 模块三：`plugins/article_generator/` (多 Agent 孤岛级加工厂)
*   断掉通讯模块隔离操作。
*   **技术**: 基于 Python 本地协程的 `Tree-Outline` 撰写，外加利用 Ping-Pong Loop 的毒舌主编 `editor_room.py` 踢掉所有的“然而在这个瞬息万变的时代...”等 AI 口水语。

### 模块四：`plugins/visual_and_layout/` (微信环境破壁包装与美学中心)
*   **技术**: Python 运行时画 `matplotlib` 折线图 + `mdnice` 纯原生 CSS 包装壳。

### 模块五：`plugins/publishers/` (生死判官端大闸)
*   **技术**: 调用已接线的 `feishu_doc` 原生接口创建飞书文件 -> 系统挂起 -> 等您发送 `@立刻发布` 文字指令方可通关推到微信。

