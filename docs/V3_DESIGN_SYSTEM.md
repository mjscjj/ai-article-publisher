# V3 设计系统文档

> 创建时间：2026-03-02  
> 版本：v3.0.0  
> 状态：✅ 已完成

---

## 📚 目录

1. [设计 Token](#设计-token)
2. [配色方案](#配色方案)
3. [字体系统](#字体系统)
4. [间距系统](#间距系统)
5. [组件库](#组件库)
6. [使用指南](#使用指南)

---

## 🎨 设计 Token

### 文件位置

```
frontend/css/v3-design-tokens.css
```

### 核心内容

设计 Token 已包含:
- ✅ 配色方案 (主色/辅助色/中性色)
- ✅ 字体系统 (6 级字号/4 级字重)
- ✅ 间距系统 (4px 基准，13 级间距)
- ✅ 圆角系统 (9 级圆角)
- ✅ 阴影系统 (7 级阴影)
- ✅ 动画系统 (过渡时间/缓动函数/关键帧)
- ✅ 断点系统 (5 级响应式断点)
- ✅ Z-Index 层级
- ✅ 透明度
- ✅ 暗色模式支持

---

## 🌈 配色方案

### 主色调 - 蓝色

| Token | 值 | 预览 |
|-------|-----|------|
| `--primary-50` | #eff6ff | 🟦 |
| `--primary-500` | #3b82f6 | 🟦 |
| `--primary-600` | #2563eb | 🟦 |
| `--primary-700` | #1d4ed8 | 🟦 |

### 辅助色

| 颜色 | Token | 值 | 用途 |
|------|-------|-----|------|
| 成功 | `--success-500` | #22c55e | 成功状态/确认按钮 |
| 警告 | `--warning-500` | #f59e0b | 警告提示/注意 |
| 危险 | `--danger-500` | #ef4444 | 错误/删除操作 |
| 紫色 | `--purple-500` | #a855f7 | 特殊功能/VIP |

### 中性色

| Token | 值 | 用途 |
|-------|-----|------|
| `--gray-50` | #f9fafb | 背景色 |
| `--gray-100` | #f3f4f6 | 分割线 |
| `--gray-500` | #6b7280 | 次要文本 |
| `--gray-900` | #111827 | 主要文本 |

---

## 📝 字体系统

### 字号

| Token | 值 | 像素 | 用途 |
|-------|-----|------|------|
| `--text-xs` | 0.75rem | 12px | 标签/注释 |
| `--text-sm` | 0.875rem | 14px | 辅助文本 |
| `--text-base` | 1rem | 16px | 正文 |
| `--text-lg` | 1.125rem | 18px | 小标题 |
| `--text-xl` | 1.25rem | 20px | 中标题 |
| `--text-2xl` | 1.5rem | 24px | 大标题 |
| `--text-3xl` | 1.875rem | 30px | 超大标题 |
| `--text-4xl` | 2.25rem | 36px | 页面标题 |

### 字重

| Token | 值 | 用途 |
|-------|-----|------|
| `--font-normal` | 400 | 正文 |
| `--font-medium` | 500 | 强调文本 |
| `--font-semibold` | 600 | 小标题 |
| `--font-bold` | 700 | 大标题 |

---

## 📏 间距系统

**基准**: 4px

| Token | 值 | 像素 | 用途 |
|-------|-----|------|------|
| `--spacing-1` | 0.25rem | 4px | 最小间距 |
| `--spacing-2` | 0.5rem | 8px | 紧凑间距 |
| `--spacing-3` | 0.75rem | 12px | 标准间距 |
| `--spacing-4` | 1rem | 16px | 常用间距 |
| `--spacing-6` | 1.5rem | 24px | 大间距 |
| `--spacing-8` | 2rem | 32px | 超大间距 |

---

## 🧩 组件库

### 按钮

```html
<!-- 主按钮 -->
<button class="btn btn-primary">主要按钮</button>

<!-- 次要按钮 -->
<button class="btn btn-secondary">次要按钮</button>

<!-- 危险按钮 -->
<button class="btn btn-danger">危险按钮</button>

<!-- 尺寸 -->
<button class="btn btn-sm">小按钮</button>
<button class="btn btn-lg">大按钮</button>
```

### 卡片

```html
<div class="card">
  <div class="card-header">标题</div>
  <div class="card-body">内容</div>
</div>
```

### 表单

```html
<input class="input" type="text" placeholder="请输入...">
<select class="select">...</select>
<textarea class="textarea"></textarea>
```

### 导航

```html
<nav class="navbar">
  <div class="navbar-brand">Logo</div>
  <div class="navbar-menu">菜单</div>
</nav>

<aside class="sidebar">
  <ul class="sidebar-menu">...</ul>
</aside>
```

---

## 📖 使用指南

### 1. 引入设计 Token

```html
<link rel="stylesheet" href="css/v3-design-tokens.css">
```

### 2. 使用 CSS 变量

```css
.my-component {
  background-color: var(--primary-500);
  color: var(--text-base);
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}
```

### 3. 响应式设计

```css
@media (min-width: var(--breakpoint-md)) {
  .my-component {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }
}
```

### 4. 暗色模式

```css
@media (prefers-color-scheme: dark) {
  .my-component {
    background-color: var(--gray-800);
    color: var(--gray-100);
  }
}
```

---

## 🎯 最佳实践

### 1. 一致性

- 始终使用设计 Token，不要硬编码颜色/间距
- 遵循组件库的使用规范
- 保持交互模式一致

### 2. 可访问性

- 确保对比度达标 (WCAG 2.1 AA)
- 添加 aria-label 属性
- 支持键盘导航

### 3. 性能

- 使用 CSS 变量减少重复代码
- 合理使用动画 (避免过多过渡)
- 压缩 CSS 文件

### 4. 维护性

- 注释清晰的代码
- 遵循命名规范
- 及时更新文档

---

## 🔗 相关文件

- `frontend/css/v3-design-tokens.css` - 设计 Token
- `frontend/css/v3-unified.css` - 统一样式
- `frontend/js/v3-common.js` - 公共 JS
- `frontend/components/` - 组件库

---

*设计系统已完成，可立即使用* ✅
