#!/usr/bin/env python3
"""
热点展示页面截图脚本
"""

import subprocess
import time
import os

output_dir = '/root/.openclaw/workspace-writer/ai-article-publisher/output'
os.makedirs(output_dir, exist_ok=True)

# 使用 playwright 命令行截图
cmd = [
    'python3', '-m', 'playwright', 'screenshot',
    '--browser', 'chromium',
    '--viewport-size', '1920,1080',
    '--full-page',
    'http://localhost:3000/hot-news-dashboard.html',
    f'{output_dir}/hot_news_page.png'
]

print("正在截图热点展示页面...")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ 截图成功：{output_dir}/hot_news_page.png")
    print(f"文件大小：{os.path.getsize(f'{output_dir}/hot_news_page.png') / 1024:.1f} KB")
else:
    print(f"❌ 截图失败：{result.stderr}")
