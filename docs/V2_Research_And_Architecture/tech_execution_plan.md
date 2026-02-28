# 🎯 V2 项目执行计与可插拔架构重构 (Execution Plan)

> **目标**: 将原本高度耦合的“流水线”拆解为相互独立的“微内核+插件”架构。
> **核心诉求**: **选题 (Topic Selection)**、**图文与排版 (Visual & Formatting)** 与 **文章写作 (Article Generation)** 完全物理隔离。写作模块必须支持独立运行，人工审核环节（Human-in-the-loop）将作为守护发布的最终阀门前置配置在最晚期执行段。

---

## 🏗️ 总体物理架构拆解 (Directory Restructuring)

我们将在项目根目录建立统一的 `plugins/` 架构，核心如下：

```text
ai-article-publisher/
├── core/                       # 核心调度器 (负责读取 config, 按需组装流)
├── plugins/                    # 可插拔模块区
│   ├── topic_discovery/        # 独立模块 1：智能选题系统
│   │   ├── cluster.py          # 聚类降噪
│   │   ├── probe.py            # 浏览器探针防红海
│   │   └── main.py             # 模块入口，输出 [Topic Object]
│   │
│   ├── article_generator/      # 独立模块 2：文章写作系统 (★ 核心)
│   │   ├── researcher.py       # STORM 式全网长研报搜索 (国内+国外)
│   │   ├── outliner.py         # 大纲干骨架生成
│   │   ├── writer_agents.py    # 并行多 Agent 织肉撰写
│   │   ├── editor_room.py      # 红蓝军主编对冲审稿
│   │   └── standalone.py       # 独立工作台
│   │
│   ├── visual_and_layout/      # 【新增】独立模块 3：图文镶嵌与终态排版引擎
│   │   ├── code_illustrator.py # Python/Mermaid 代码动态跑图表截屏
│   │   ├── flux_vision.py      # 调用文生图 API (如 Flux.1) 生成封面与极客插画
│   │   └── mdnice_renderer.py  # 微信公众号专属 CSS Markdown 渲染器
│   │
│   └── publishers/             # 独立模块 4：发布与人工核验终端 (终极卡口)
│       ├── feishu_reviewer.py  # 飞书终审流 (包含成品版 CSS 渲染效果展示)
│       └── wechat_pusher.py    # 微信公众号真机分发
```

---

## ⚙️ 核心解耦机制：可插拔状态机 (Pluggable Settings)

通过全局统一配置文件 `pipeline_config.json` 来控制流水线的流转链路：

```json
{
  "modules": {
    "topic_optimization": {
      "semantic_cluster": true,      // 每天先把同质化新闻打包成一个事件簇
      "red_ocean_probe": false       // 用搜索 API 查同行的撞题率
    },
    "writing_engine": {
      "deep_research": true,         // 外网干货（Brave/Google）
      "domestic_search_engine": true,// 国内情绪/神评（百度/知乎/微信搜）
      "multi_agent_review": false,   // “主编Agent”对抗改稿
      "rag_clone": false             // 文本向量库模仿历史语气
    },
    "visual_formatting": {           // 【新增图文排版区】
      "auto_illustration": true,     // Python 自动跑图表插入段落
      "flux_image_gen": false,       // 是否耗费 API 额度绘制高清氛围配图
      "wechat_css_render": true,     // [关键] 是否套用 mdnice 高级模板输出富文本 HTML
      "title_optimizer": false       // 小模型预测挑选最高点击标题
    },
    "final_delivery": {
      "human_in_the_loop": true,     // 发飞书等主人的"@发布"批条
      "matrix_publisher": false,     // 拆分出小红书/微博短动态版
      "auto_publish_wechat": true    // 取得批条后放行
    }
  }
}
```

---

## 🧭 阶段一至三：全新融合版核心工作流

**【前核：选题入库】**
1. **清洗与红海规避**: 把新闻聚类降噪，并通过“浏览器探针”剔除已被疯狂洗稿的红海议题，留下逆向反转视角的蓝海大纲。

**【中轴：写作与多源事实装载】**
2. **双轨检索**: Brave 搜华尔街研报；百度搜该事件下网民骂的最凶的段子。
3. **并行织肉**: 3个子代理分别承接不同视角的段落撰写，随后接受“咪蒙化”毒舌主编的极限压力盲测退回重写。

**【后处理：降维打击的图文封装 (Visual & Formatting)】**
4. **配分发**: 内容完稿后，交给 `visual_and_layout` 引擎。如果提到财务或算力数据，强行拉起 Python 跑一个实时的图表渲染截屏；给核心段落铺配 `Flux` 级别的文生图；最后调取 `mdnice_renderer` 把原本丑陋的 Markdown 标记转化为精美的微信原生 HTML 富文本代码。

**【末端大闸：防爆防越权 (Human Review)】**
5. **压轴只读投递**: 取消 AI 自由访问公众号接口的权力。包含精美图文排版的终极 HTML 被灌入飞书审批文档，AI 转入挂起装死状态（留存一条看门狗 cron 定时任务）。一旦监测到您的 `[通过/发布]` 密令，开闸放行！
