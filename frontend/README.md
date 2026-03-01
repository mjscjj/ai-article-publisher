# V3 前端使用指南

> 创建时间：2026-03-02  
> 版本：v3.0.0  
> 状态：✅ 已完成

---

## 📚 目录结构

```
frontend/
├── css/
│   ├── v3-design-tokens.css      # 设计 Token (7.4KB)
│   ├── v3-unified.css            # 统一样式 (19KB)
│   └── v3-unified-v2.css         # 整合样式 (新增)
├── js/
│   ├── v3-common.js              # 公共 JS (18KB)
│   ├── components-loader.js      # 组件加载器 (新增)
│   └── portal.js                 # 门户逻辑 (22KB)
├── components/
│   ├── navbar.html               # 统一导航栏 (16KB)
│   ├── sidebar.html              # 统一侧边栏 (15KB)
│   └── breadcrumb.html           # 面包屑导航 (13KB)
├── templates/
│   └── page-template.html        # 标准页面模板 (新增)
├── v3_portal_v2.html             # 统一门户 (89KB)
├── v3_hotnews_center_v2.html     # 热点中心 (58KB)
├── v3_topic_intelligence_v2.html # 智能选题
├── v3_evaluation_v2.html         # 工作评价
├── v3_work_review_v2.html        # 工作 Review
├── v3_data_dashboard_v2.html     # 数据看板
├── v3_user_center_v2.html        # 用户中心
├── v3_publish_center_v2.html     # 自动发布
├── v3_coordinator_v2.html        # 项目协调者
├── v3_workflow_v2.html           # 工作流引擎
└── v3_writing_factory_v2.html    # 写作工厂
```

---

## 🎨 设计系统

### 设计 Token

位置：`css/v3-design-tokens.css`

包含:
- ✅ 配色方案 (主色/辅助色/中性色)
- ✅ 字体系统 (8 级字号/4 级字重)
- ✅ 间距系统 (13 级，4px 基准)
- ✅ 圆角系统 (9 级圆角)
- ✅ 阴影系统 (7 级阴影)
- ✅ 动画系统
- ✅ 响应式断点 (5 级)
- ✅ 暗色模式支持

### 使用方式

```css
.my-component {
  background-color: var(--primary-500);
  color: var(--text-base);
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}
```

---

## 🧩 组件库

### 统一导航栏

位置：`components/navbar.html`

功能:
- Logo + 品牌名
- 全局搜索框 (Ctrl+K)
- 模块切换菜单 (11 个模块)
- 通知中心
- 用户菜单 (头像/设置/退出)
- 主题切换 (明/暗)

### 统一侧边栏

位置：`components/sidebar.html`

功能:
- 主菜单导航
- 收藏功能
- 最近访问记录
- 快捷操作
- 系统状态展示
- 可折叠设计

### 面包屑导航

位置：`components/breadcrumb.html`

功能:
- 层级展示
- 快速跳转
- 当前位置指示
- 刷新/分享/收藏操作

---

## 📄 页面模板

### 使用标准模板

位置：`templates/page-template.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>页面标题 - V3 统一门户</title>
    <link rel="stylesheet" href="../css/v3-design-tokens.css">
    <link rel="stylesheet" href="../css/v3-unified.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
</head>
<body>
    <!-- 页面内容 -->
</body>
</html>
```

### 使用组件加载器

```html
<script src="../js/components-loader.js"></script>
<script>
  loadComponents({
    title: '页面标题',
    breadcrumbs: ['首页', '当前页面']
  });
</script>
```

---

## ⌨️ 快捷键系统

| 快捷键 | 功能 |
|--------|------|
| `Alt+1~9` | 切换模块 |
| `Alt+H` | 返回首页 |
| `Alt+S` | 折叠侧边栏 |
| `Ctrl+K` | 聚焦搜索 |
| `F5` | 刷新数据 |
| `Esc` | 关闭弹窗 |

---

## 🌙 主题系统

### 切换主题

```javascript
// 自动切换
toggleTheme();

// 手动设置
localStorage.setItem('theme', 'dark'); // 或 'light'
```

### 暗色模式 CSS

```css
@media (prefers-color-scheme: dark) {
  :root {
    --gray-50: #111827;
    --gray-900: #f9fafb;
  }
}
```

---

## 📱 响应式设计

### 断点

| 断点 | 宽度 | 设备 |
|------|------|------|
| `--breakpoint-sm` | 640px | 手机横屏 |
| `--breakpoint-md` | 768px | 平板 |
| `--breakpoint-lg` | 1024px | 桌面 |
| `--breakpoint-xl` | 1280px | 大桌面 |
| `--breakpoint-2xl` | 1536px | 超大桌面 |

### 使用方式

```css
@media (min-width: var(--breakpoint-md)) {
  .my-component {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }
}
```

---

## 🧪 测试

### 运行测试

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher
python3 tests/browser/browser_e2e_test.py
python3 tests/browser/mobile_test.py
python3 tests/browser/accessibility_test.py
python3 tests/browser/compatibility_test.py
```

### 测试结果

| 测试类型 | 通过率 | 状态 |
|----------|--------|------|
| E2E 测试 | 100% (18/18) | ✅ |
| 移动端测试 | 100% (5/5) | ✅ |
| 无障碍测试 | 86.7% (13/15) | ✅ |
| 兼容性测试 | 100% (Chrome/Firefox) | ✅ |

---

## 📖 最佳实践

### 1. 使用设计 Token

```css
/* ✅ 推荐 */
color: var(--primary-500);

/* ❌ 不推荐 */
color: #3b82f6;
```

### 2. 使用组件

```html
<!-- ✅ 推荐 -->
<nav class="navbar">...</nav>

<!-- ❌ 不推荐 -->
<nav class="custom-nav">...</nav>
```

### 3. 响应式设计

```css
/* ✅ 推荐：移动优先 */
.my-component {
  display: block;
}

@media (min-width: 768px) {
  .my-component {
    display: grid;
  }
}
```

### 4. 可访问性

```html
<!-- ✅ 推荐 -->
<button aria-label="关闭对话框">✕</button>

<!-- ❌ 不推荐 -->
<button>✕</button>
```

---

## 🔗 相关文档

- [V3_DESIGN_SYSTEM.md](../docs/V3_DESIGN_SYSTEM.md) - 设计系统文档
- [V3_UNIFIED_DEPLOYMENT.md](../docs/V3_UNIFIED_DEPLOYMENT.md) - 部署文档
- [FRONTEND_DESIGN_REVIEW.md](../docs/FRONTEND_DESIGN_REVIEW.md) - 设计审查

---

*前端系统已完成，可立即使用* ✅
