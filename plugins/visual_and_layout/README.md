# 🎨 Visual & Layout (纯函数排版器)

> 独立的排版渲染微服务，它不在乎文章内容，只负责皮囊。

## 对外接口 (Facade API)
### `render_to_wechat_html(markdown_text: str) -> str`
- **输入**: 任意来源的规整 Markdown 字符串。
- **输出**: 注入了定型 CSS Inline 表现样式的微信公众号底包 HTML 字符串。
