# 📅 AI Article Publisher V2 - 执行路线清单 (Implementation Checklist)

> **当前阶段**: Sprint 1 - 模块真枪实弹填充 (API 与核心引擎)

---

## 🏃‍♂️ 任务区：排版及发单卡口 (`visual_and_layout` & `publishers`) (候场中)

### [✅ 已完成] 🎯 行动任务 C: 微信排版转换 (`mdnice_renderer.py`)
*   引入轻量级 CSS。把普通 Markdown 转变为带有排版皮肤的 HTML 富文本。

### 🎯 行动任务 D: 飞书审阅流卡口 (`feishu_reviewer.py`)
*   对接 `feishu_doc` API，完成飞书文档撰写及 `cron` 发起等待校验。
