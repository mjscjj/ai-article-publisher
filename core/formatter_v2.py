#!/usr/bin/env python3
"""
【V2 排版模块】Visual Formatter
将 Markdown 转为带内联 CSS 样式的微信公众号合规 HTML，
模拟 mdnice 或 135editor 的精美排版效果。
"""
import os
import sys
import re

def markdown_to_html_simple(md_text):
    # 极简正则替换，将 MD 转为带样式的 HTML
    # 替换标题
    md_text = re.sub(r'^### (.*)', r'<h3 style="font-size:16px; font-weight:bold; color:#f05050; margin:20px 0 10px; border-bottom: 1px dashed #f05050; padding-bottom: 5px;">\1</h3>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^## (.*)', r'<h2 style="font-size:18px; font-weight:bold; color:#fff; background-color:#333; padding:8px 15px; border-radius:4px; margin:25px 0 15px; display:inline-block;">\1</h2><br/>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^# (.*)', r'<h1 style="font-size:22px; font-weight:900; color:#111; text-align:center; margin-bottom:30px; line-height:1.4;">\1</h1>', md_text, flags=re.MULTILINE)
    
    # 替换加粗
    md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#d32f2f; font-weight:bold;">\1</strong>', md_text)
    
    # 替换列表
    md_text = re.sub(r'^- (.*)', r'<li style="margin-bottom:8px; line-height:1.7;">\1</li>', md_text, flags=re.MULTILINE)
    # 给连续的 li 加上 ul 外套 (简易版处理)
    md_text = re.sub(r'(<li.*?>.*?</li>\n)+', lambda m: f'<ul style="padding-left:20px; color:#555;">\n{m.group(0)}</ul>\n', md_text)
    
    # 替换段落 (排除已经带有html标签的行)
    lines = md_text.split('\n')
    out_lines = []
    for line in lines:
        if line.strip() == '':
            out_lines.append('<br/>')
        elif not line.strip().startswith('<'):
            out_lines.append(f'<p style="font-size:15px; color:#3e3e3e; line-height:1.8; margin-bottom:15px; letter-spacing:1px; text-align:justify;">{line}</p>')
        else:
            out_lines.append(line)
            
    return '\n'.join(out_lines)

def run_formatter():
    in_path = "/root/.openclaw/workspace-writer/ai-article-publisher/data/article_reviewed_v2.md"
    out_path = "/root/.openclaw/workspace-writer/ai-article-publisher/data/article_final.html"
    
    if not os.path.exists(in_path):
        print("❌ 找不到定稿文件", in_path)
        return
        
    with open(in_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
        
    html_content = markdown_to_html_simple(md_text)
    
    # 外层包装
    final_html = f"""
    <section style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 15px; background-color: #fcfcfc;">
        <section style="background-color: #fff; padding: 25px 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 5px solid #d32f2f;">
            {html_content}
            <br/>
            <p style="text-align:center; font-size:12px; color:#999; margin-top:30px;">
                本文由 AI Article Publisher 全自动引擎采编生成，主笔：V2 大模型
            </p>
        </section>
    </section>
    """
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    print(f"✅ 内联CSS排版包装完毕！生成的富文本HTML已就绪: {out_path}")

if __name__ == "__main__":
    run_formatter()
