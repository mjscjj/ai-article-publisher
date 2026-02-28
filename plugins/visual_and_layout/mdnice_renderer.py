# -*- coding: utf-8 -*-
"""
mdnice_renderer.py

将原生 Markdown 渲染为适合微信公众号发布的 HTML（仅使用 Inline CSS）。
"""

from __future__ import annotations

import re
import subprocess
import sys
from typing import Dict


def _ensure_markdown_installed() -> bool:
    """Ensure `markdown` package is available. Install silently if missing."""
    try:
        import markdown  # noqa: F401
        return True
    except Exception:
        # silent install
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "markdown", "-q"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            import markdown  # noqa: F401
            return True
        except Exception:
            return False


def _basic_markdown_to_html(md: str) -> str:
    """Very lightweight Markdown fallback (headings, blockquote, lists, bold, paragraphs)."""
    html_lines = []
    lines = md.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:].strip()}</h1>")
            i += 1
            continue
        if line.startswith("## "):
            html_lines.append(f"<h2>{line[3:].strip()}</h2>")
            i += 1
            continue
        if line.startswith("> "):
            # collect contiguous blockquote lines
            block = []
            while i < len(lines) and lines[i].startswith("> "):
                block.append(lines[i][2:].strip())
                i += 1
            html_lines.append(f"<blockquote>{' '.join(block)}</blockquote>")
            continue
        if line.startswith("- ") or line.startswith("* "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("* ")):
                items.append(lines[i][2:].strip())
                i += 1
            lis = "".join([f"<li>{item}</li>" for item in items])
            html_lines.append(f"<ul>{lis}</ul>")
            continue
        # paragraph
        html_lines.append(f"<p>{line.strip()}</p>")
        i += 1

    html = "".join(html_lines)
    # bold
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    return html


def _inline_style(html: str, tag: str, style: str) -> str:
    """Add inline style for all occurrences of a tag."""
    # If tag already has style attr, append; else insert
    pattern = re.compile(rf"<{tag}(\s[^>]*)?>", re.IGNORECASE)

    def repl(match: re.Match) -> str:
        attrs = match.group(1) or ""
        if "style=" in attrs.lower():
            # append to existing style
            attrs = re.sub(
                r"style=\"([^\"]*)\"",
                lambda m: f"style=\"{m.group(1).rstrip(';')}; {style}\"",
                attrs,
                flags=re.IGNORECASE,
            )
            return f"<{tag}{attrs}>"
        else:
            return f"<{tag}{attrs} style=\"{style}\">"

    return pattern.sub(repl, html)


def render_to_wechat_html(markdown_text: str) -> str:
    """
    Convert Markdown text to WeChat-friendly HTML with inline CSS.
    """
    has_md = _ensure_markdown_installed()
    if has_md:
        import markdown  # type: ignore

        # Basic markdown to HTML
        html = markdown.markdown(
            markdown_text,
            extensions=["extra", "sane_lists"],
        )
    else:
        # fallback minimal parser if markdown lib is unavailable
        html = _basic_markdown_to_html(markdown_text)

    # Styles (geek + business tone)
    styles: Dict[str, str] = {
        "h1": "font-size: 26px; font-weight: 700; color: #111111; margin: 24px 0 12px; letter-spacing: 1px;",
        "h2": "font-size: 20px; font-weight: 700; color: #0f62fe; margin: 20px 0 10px; padding-bottom: 6px; border-bottom: 2px solid #0f62fe; letter-spacing: 0.8px;",
        "p": "line-height: 1.75; letter-spacing: 1.5px; font-size: 15px; color: #333333; margin: 10px 0;",
        "blockquote": "border-left: 4px solid #0f62fe; background: #f5f7fa; padding: 10px 14px; margin: 12px 0; color: #555555;",
        "strong": "color: #0f62fe; font-weight: 700;",
        "ul": "padding-left: 20px; margin: 10px 0; color: #333333;",
        "ol": "padding-left: 20px; margin: 10px 0; color: #333333;",
        "li": "line-height: 1.7; letter-spacing: 1px; font-size: 15px; color: #333333; margin: 6px 0;",
        "a": "color: #0f62fe; text-decoration: none;",
        "code": "font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; background: #f2f4f8; padding: 2px 4px; border-radius: 3px; font-size: 13px;",
        "pre": "background: #0d1117; color: #c9d1d9; padding: 12px; border-radius: 6px; overflow-x: auto; line-height: 1.6;",
    }

    for tag, style in styles.items():
        html = _inline_style(html, tag, style)

    # Wrap content for overall typography control
    wrapper_style = (
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC', 'Hiragino Sans GB', "
        "'Microsoft YaHei', sans-serif; "
        "padding: 4px 2px;"
    )

    return f"<section style=\"{wrapper_style}\">{html}</section>"


if __name__ == "__main__":
    demo_md = """
# AI 文章发布器 V2

## 视觉与排版模块

> 这是一个引用区块，用于强调关键观点。

本文支持 **加粗强调**，并包含列表：

- 方案 A：快速上线
- 方案 B：兼容扩展
- 方案 C：稳定可控

再来一段普通正文，测试行距与字距效果。
"""

    result = render_to_wechat_html(demo_md)
    print(result[:500])
