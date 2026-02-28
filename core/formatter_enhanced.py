#!/usr/bin/env python3
"""
【增强型 HTML 排版器】Enhanced HTML Formatter
支持多种微信公众号排版风格，可配置主题色、字体、间距等

风格模板:
1. 极客风 (黑白 + 代码块)
2. 商务风 (深蓝 + 简洁)
3. 文艺风 (暖色 + 引用)
4. 新闻风 (红黑 + 粗体)
"""

import re
import html
from typing import Dict, List

# 排版风格配置
STYLES = {
    "geek": {
        "name": "极客风",
        "primary_color": "#000000",
        "secondary_color": "#666666",
        "accent_color": "#007AFF",
        "bg_color": "#f8f9fa",
        "code_bg": "#f6f8fa",
        "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace",
        "blockquote_border": "#007AFF",
    },
    "business": {
        "name": "商务风",
        "primary_color": "#1a1a1a",
        "secondary_color": "#4a4a4a",
        "accent_color": "#003366",
        "bg_color": "#ffffff",
        "code_bg": "#f5f5f5",
        "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto",
        "blockquote_border": "#003366",
    },
    "literary": {
        "name": "文艺风",
        "primary_color": "#2c2c2c",
        "secondary_color": "#6b6b6b",
        "accent_color": "#b85c38",
        "bg_color": "#faf8f5",
        "code_bg": "#f9f6f2",
        "font_family": "Georgia, 'Times New Roman', serif",
        "blockquote_border": "#b85c38",
    },
    "news": {
        "name": "新闻风",
        "primary_color": "#000000",
        "secondary_color": "#333333",
        "accent_color": "#c41e3a",
        "bg_color": "#ffffff",
        "code_bg": "#f8f8f8",
        "font_family": "-apple-system, BlinkMacSystemFont, 'Microsoft YaHei'",
        "blockquote_border": "#c41e3a",
    },
}

def markdown_to_html_enhanced(markdown: str, style: str = "business") -> str:
    """
    增强型 Markdown 转 HTML
    支持多种排版风格
    """
    if style not in STYLES:
        style = "business"
    
    s = STYLES[style]
    
    # 基础 HTML 转义
    html_content = html.escape(markdown)
    
    # 标题处理
    html_content = re.sub(
        r'^### (.+)$',
        rf'<h3 style="font-size: 18px; font-weight: 600; color: {s["primary_color"]}; margin: 24px 0 12px; padding-left: 12px; border-left: 4px solid {s["accent_color"]};">\1</h3>',
        html_content,
        flags=re.M
    )
    html_content = re.sub(
        r'^## (.+)$',
        rf'<h2 style="font-size: 20px; font-weight: 600; color: {s["primary_color"]}; margin: 28px 0 14px; padding-left: 14px; border-left: 5px solid {s["accent_color"]};">\1</h2>',
        html_content,
        flags=re.M
    )
    html_content = re.sub(
        r'^# (.+)$',
        rf'<h1 style="font-size: 24px; font-weight: 700; color: {s["primary_color"]}; margin: 32px 0 16px; text-align: center;">\1</h1>',
        html_content,
        flags=re.M
    )
    
    # 粗体
    html_content = re.sub(
        r'\*\*(.+?)\*\*',
        rf'<strong style="font-weight: 600; color: {s["primary_color"]};">\1</strong>',
        html_content
    )
    
    # 斜体
    html_content = re.sub(
        r'\*(.+?)\*',
        r'<em style="font-style: italic;">\1</em>',
        html_content
    )
    
    # 引用
    html_content = re.sub(
        r'^&gt; (.+)$',
        rf'<blockquote style="margin: 16px 0; padding: 12px 16px; background: {s["bg_color"]}; border-left: 4px solid {s["blockquote_border"]}; color: {s["secondary_color"]}; font-size: 15px; line-height: 1.6;">\1</blockquote>',
        html_content,
        flags=re.M
    )
    
    # 代码块
    html_content = re.sub(
        r'```(\w*)\n(.+?)```',
        rf'<div style="margin: 16px 0; padding: 16px; background: {s["code_bg"]}; border-radius: 6px; overflow-x: auto; font-family: monospace; font-size: 13px; line-height: 1.5;"><code>\2</code></div>',
        html_content,
        flags=re.S
    )
    
    # 行内代码
    html_content = re.sub(
        r'`(.+?)`',
        rf'<code style="padding: 2px 6px; background: {s["code_bg"]}; border-radius: 3px; font-family: monospace; font-size: 13px;">\1</code>',
        html_content
    )
    
    # 链接
    accent = s["accent_color"]
    html_content = re.sub(
        r'\[(.+?)\]\((.+?)\)',
        rf'<a href="\2" style="color: {accent}; text-decoration: underline;">\1</a>',
        html_content
    )
    
    # 段落
    paragraphs = html_content.split('\n\n')
    formatted_paras = []
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<h') and not para.startswith('<blockquote'):
            formatted_paras.append(
                f'<p style="margin: 16px 0; line-height: 1.8; color: {s["primary_color"]}; font-size: 15px; text-align: justify;">{para}</p>'
            )
        else:
            formatted_paras.append(para)
    
    html_content = '\n'.join(formatted_paras)
    
    # 包装为微信兼容的完整 HTML
    final_html = f'''
<section style="box-sizing: border-box; font-family: {s["font_family"]}; padding: 16px; background-color: {s["bg_color"]};">
    <section style="background-color: #fff; padding: 24px 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
        {html_content}
        <br/>
        <p style="text-align:center; font-size:12px; color:#999; margin-top:32px; border-top: 1px solid #eee; padding-top: 12px;">
            主笔：OpenClaw AI · 排版风格：{s["name"]}
        </p>
    </section>
</section>
'''
    return final_html


def test_formatter():
    """测试排版器"""
    test_md = """# AI 正在重塑教育

## 现状与触发

本周，**教育部发布**《人工智能 + 教育》指导意见。

> 人工智能将成为重塑教育格局的关键变量

## 核心矛盾

程序员失业论调再起，但专家李政涛表示：

`AI 不会取代教师，但会重新定义教学`

### 数据支撑

- 2025 年 AI 教育市场规模达 1000 亿
- 60% 高校已开设 AI 相关课程

```python
print("Hello AI Education")
```

[阅读全文](https://example.com)
"""
    
    print("测试排版风格:")
    for style_key in STYLES:
        html = markdown_to_html_enhanced(test_md, style_key)
        print(f"\n{STYLES[style_key]['name']}: {len(html)} 字符")
    
    # 保存商务风示例
    html = markdown_to_html_enhanced(test_md, "business")
    with open("data/formatter_test.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✅ 示例已保存：data/formatter_test.html")


if __name__ == "__main__":
    test_formatter()
