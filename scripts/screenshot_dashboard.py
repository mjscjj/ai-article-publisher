#!/usr/bin/env python3
"""
使用 Playwright 截取热点展示页面
"""

from playwright.sync_api import sync_playwright
import time

def screenshot_hot_news():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        # 访问页面
        print("正在访问热点展示页面...")
        page.goto('http://localhost:3000/hot-news-dashboard.html', wait_until='networkidle')
        
        # 等待内容加载
        time.sleep(3)
        
        # 截图
        print("正在截图...")
        page.screenshot(
            path='/root/.openclaw/workspace-writer/ai-article-publisher/output/hot_news_dashboard.png',
            full_page=True
        )
        
        print("✅ 截图已保存：output/hot_news_dashboard.png")
        
        # 关闭浏览器
        browser.close()

if __name__ == "__main__":
    try:
        screenshot_hot_news()
    except Exception as e:
        print(f"❌ 截图失败：{e}")
        import traceback
        traceback.print_exc()
