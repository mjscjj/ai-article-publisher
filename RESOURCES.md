# AI Article Publisher - 资源清单

> 收集的相关项目、插件、技能和教程

---

## 🦞 OpenClaw 相关项目

### Channel Plugins (渠道插件)

#### 1. wemp - 微信公众号 AI 助手插件
- **仓库**: https://github.com/IanShaw027/wemp
- **Stars**: 4
- **语言**: TypeScript
- **更新**: 12 days ago
- **功能**:
  - 📨 消息收发（文本、语音、图片）
  - 🤖 双 Agent 模式（客服 Agent + 完整 Agent）
  - 🔗 跨渠道配对（通过 Telegram 等解锁完整功能）
  - 📋 自定义菜单管理
  - 🔐 安全模式（AES 加密）
  - ⚡ 客服消息接口（无 5 秒超时限制）
- **安装**:
  ```bash
  cd ~/.openclaw/extensions
  git clone https://github.com/IanShaw027/wemp.git wemp
  cd wemp && npm install && npm run build
  openclaw gateway restart
  ```

---

### Skills (技能)

#### 2. wemp-operator - 公众号自动化运营
- **仓库**: https://github.com/IanShaw027/wemp-operator
- **Stars**: 21 ⭐ 最推荐
- **语言**: JavaScript
- **更新**: 18 days ago
- **功能**:
  - 📝 内容采集 - 20+ 数据源（HN、V2EX、36Kr、微博等）
  - 📊 数据分析 - 日报/周报自动生成
  - 💬 互动管理 - 评论检查、智能回复
  - 🔌 70 个微信公众号 API
- **数据源**:
  - 科技: hackernews, github, v2ex, sspai, juejin, ithome, producthunt
  - 中文热点: weibo, zhihu, baidu, douyin, bilibili, toutiao
  - 财经: 36kr, wallstreetcn, cls
- **安装**:
  ```bash
  openclaw skill install IanShaw027/wemp-operator
  ```
- **使用**:
  ```
  帮我采集今天的 AI 热点
  生成公众号日报
  检查公众号新评论
  ```

#### 3. wechat-article-skill - 公众号文章创作
- **仓库**: https://github.com/MaydayV/wechat-article-skill
- **Stars**: 0
- **语言**: Python
- **更新**: yesterday
- **功能**:
  - ✍️ AI 文章创作（一句话主题生成完整文章）
  - 📝 公众号排版（内联 CSS HTML）
  - 🎨 封面风格系统（4 种风格 × 6 套配色）
  - 👀 发布前预览确认
  - 🚀 草稿推送
- **封面风格**:
  - minimal-grid (极简网格)
  - card-editorial (编辑卡片)
  - diagonal-motion (斜切动势)
  - soft-gradient (柔和渐变)
- **安装**:
  ```bash
  git clone https://github.com/MaydayV/wechat-article-skill ~/.openclaw/workspace/skills/wechat-article-skill
  ```

#### 4. wechat-publisher - Markdown 发布工具
- **仓库**: https://github.com/yuejiangli/wechat-publisher
- **Stars**: 0
- **语言**: Python
- **更新**: 6 days ago
- **功能**:
  - 上传图片到微信 CDN
  - Markdown 转 HTML（公众号兼容）
  - 上传文章到草稿箱
- **脚本**:
  - `get_token.py` - 获取 access token
  - `upload_thumb.py` - 上传封面图
  - `upload_img.py` - 上传正文图片
  - `md_to_html.py` - Markdown 转 HTML
  - `upload_draft.py` - 上传草稿

#### 5. wechat_mp_publish - Node.js 发布工具
- **仓库**: https://github.com/godrealms/wechat_mp_publish
- **Stars**: 0
- **语言**: Node.js
- **更新**: 11 days ago
- **功能**:
  - 上传封面图
  - Markdown 生成草稿
  - 手动确认后发布
  - 查询发布状态

#### 6. wechat-mp-writer-skill-mxx - 写作助手
- **仓库**: https://github.com/mxx1111/wechat-mp-writer-skill-mxx
- **Stars**: 0
- **语言**: -
- **更新**: 18 minutes ago
- **功能**:
  - 热点选题建议
  - 文章撰写（多种风格）
  - AI 去味润色
  - 配图建议

#### 7. wechat-mp-publisher - MCP 发布工具
- **仓库**: https://github.com/lynnlni/wechat-mp-publisher
- **Stars**: 0
- **语言**: -
- **更新**: 2 hours ago
- **功能**: Publish Markdown to WeChat Official Account via remote MCP

---

## 🤖 独立项目（非 OpenClaw）

### wechat-auto - 多 Agent 公众号自动化系统
- **仓库**: https://github.com/ffan008/wechat-auto
- **Stars**: 1
- **语言**: Python
- **更新**: 14 days ago
- **技术栈**:
  - LangGraph (Agent 框架)
  - Claude 3.5 Sonnet (AI 模型)
  - FastAPI (Web 框架)
  - PostgreSQL + Redis (存储)
  - Celery (任务队列)
  - WeChatPy (微信 SDK)
- **Agent 架构**:
  - Coordinator Agent - 主控路由
  - Chat Agent - 智能对话
  - Content Agent - 内容生成
  - Analytics Agent - 数据分析
  - Scheduler Agent - 定时任务
- **功能**:
  - AI 内容生成（大纲、正文、标题）
  - A/B 测试标题优化
  - 实时意图识别
  - FAQ 知识库
  - 用户画像构建
  - 定时发布
  - 数据洞察报告

---

## 📚 相关教程/文档

### OpenClaw 官方
- [OpenClaw 文档](https://docs.openclaw.ai)
- [Cron Jobs](https://docs.openclaw.ai/automation/cron-jobs.md) - 定时任务
- [Webhooks](https://docs.openclaw.ai/automation/webhook.md) - 外部触发
- [ClawHub](https://clawhub.com) - 技能市场

### 微信公众号
- [微信公众平台](https://mp.weixin.qq.com)
- [开发文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)

---

## 📊 项目对比矩阵

| 项目 | 热点收集 | AI写作 | 发布 | 数据分析 | 推荐度 |
|------|:--------:|:------:|:----:|:--------:|:------:|
| wemp | ❌ | ❌ | ❌ | ❌ | ⭐⭐⭐⭐ |
| wemp-operator | ✅ | ❌ | ❌ | ✅ | ⭐⭐⭐⭐⭐ |
| wechat-article-skill | ❌ | ✅ | ✅ | ❌ | ⭐⭐⭐⭐ |
| wechat-publisher | ❌ | ❌ | ✅ | ❌ | ⭐⭐⭐ |
| wechat-auto | ❌ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ |

---

## 🎯 推荐组合

**最佳组合（全流程）:**
```
wemp (消息收发)
+ wemp-operator (热点采集 + 数据分析)
+ wechat-article-skill (AI写作 + 封面 + 发布)
```

---

*最后更新: 2026-02-21*