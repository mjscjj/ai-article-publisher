# 📁 V2 核心工程指引与研究文库 (Research & Architecture)

本项目 `ai-article-publisher` 已全面迈入 V2 可插拔架构时代。为了保证知识与开发的序列化，本目录下的文件经过严格的重新洗牌与定性。

## 📜 一、 调研与情报类 (Research)
此类文档属于我们在开发初期的脑暴与情报收集。记录了开源圈的发展现状及我们的破局思路。

*   `research_advanced_optimization.md`: [进阶点] 探讨 Storm, CrewAI, gpt-researcher 等顶级开源方案对我们的降维打击启发。
*   `research_chinese_search_mcp.md`: [痛点攻坚] 深度排查全网开源的纯正简中搜索/情绪 MCP (如 xiaohongshu-mcp, baidu-mcp, 回流定调内网 RSSHub)。
*   `research_options_menu.md`: [可选菜单] 将全盘方案做了难度分级 (A1, B1, C2 等) 形成的点菜菜单。
*   `research_topic_and_generation.md`: [立项书] 早期对智能选题与爆文生产脱钩的粗略方向探讨。

## 🛠️ 二、 核心技术规范指引 (Tech)
此类文档是 **真刀真枪写代码的“红头文件”**。任何 AI Agent 下场敲代码前，必须查阅这部分规范。

*   **`tech_master_specification.md`**: 【总纲】囊括一切的技术总方案。明确了从零到一去外部依赖、内部五大插件串联运作。
*   **`tech_architecture_master_plan.md`**: 【白皮书】极其详细地描写了五大中心枢纽模块（Plugin 0 - 5）的物理边界设定与出入参约束。
*   **`tech_execution_plan.md`**: 【宏观拆解】阐明了配置文件中各个 Boolean 控制开关的具体职责与生效顺序。
*   **`tech_directory_and_modules.md`**: 【目录导读】定义并解析 `plugins/` 下几十个 Python 脚本的具体使命。
*   **`tech_module_details.md`**: 【函数拆解方案】细化到 `domestic_sniffer.py` 等文件中该怎么写正则表达式与分发路由。
*   **`tech_implementation_checklist.md`**: 【报工追踪打卡表】定义了每一个短冲刺 (Sprint) 应当跑通哪几项具体的存根脚本。

## ⚠️ 三、 开发准则
*   `doc_workflow_rule.md`: 硬性纪律 —— 要求所有代理在此目录下做任何活，都必须改写 `PROGRESS.md` !
