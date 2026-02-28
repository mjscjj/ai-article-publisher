#!/usr/bin/env python3
"""
【内网探针】Domestic Sniffer V3 - 直连 API 版
直接使用各平台官方 API，无需 RSSHub 中间层。

数据源:
- 知乎热榜 (官方 API)
- B 站排行 (官方 API)
- 微博热搜 (网页抓取)
- 百度新闻 (爬虫)
- 什么值得买 (需要 Cookie，暂用 RSSHub 备用)
"""

import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any

# === 直连采集器 ===
def fetch_zhihu_data(keyword: str, limit: int = 10) -> List[Dict]:
    """知乎热榜直连"""
    try:
        import sys
        sys.path.insert(0, '/root/.openclaw/workspace-writer/ai-article-publisher/plugins/retrieval')
        from zhihu_direct import search_zhihu_by_keyword
        
        results = search_zhihu_by_keyword(keyword, limit=limit)
        return results
    except Exception as e:
        print(f"[Domestic Sniffer] ⚠️ 知乎直连失败：{e}")
        return []

def fetch_bilibili_data(keyword: str, limit: int = 10) -> List[Dict]:
    """B 站排行直连"""
    try:
        import sys
        sys.path.insert(0, '/root/.openclaw/workspace-writer/ai-article-publisher/plugins/retrieval')
        from bilibili_direct import search_bilibili_by_keyword
        
        results = search_bilibili_by_keyword(keyword, limit=limit)
        return results
    except Exception as e:
        print(f"[Domestic Sniffer] ⚠️ B 站直连失败：{e}")
        return []

def fetch_weibo_data(keyword: str, limit: int = 10) -> List[Dict]:
    """微博热搜直连"""
    try:
        import sys
        sys.path.insert(0, '/root/.openclaw/workspace-writer/ai-article-publisher/plugins/retrieval')
        from weibo_direct import search_weibo_by_keyword
        
        results = search_weibo_by_keyword(keyword, limit=limit)
        return results
    except Exception as e:
        print(f"[Domestic Sniffer] ⚠️ 微博直连失败：{e}")
        return []

def fetch_baidu_news(keyword: str, limit: int = 5) -> List[Dict]:
    """百度新闻 (爬虫)"""
    try:
        import sys
        sys.path.insert(0, '/root/.openclaw/workspace-writer/ai-article-publisher/plugins/autonomous_researcher/providers')
        from baidu_mcp import BaiduProvider
        provider = BaiduProvider()
        results = provider.search(keyword, max_results=limit)
        return results
    except Exception as e:
        print(f"[Domestic Sniffer] ⚠️ 百度爬虫失败：{e}")
        return []


def sniff_domestic_emotions(keyword: str) -> Dict[str, Any]:
    """
    对外统一暴露的主函数：采集国内全网情绪与讨论
    
    Args:
        keyword: 搜索关键词
    
    Returns:
        结构化数据：
        {
            "keyword": "...",
            "zhihu": [...],       # 知乎热榜/相关内容
            "bilibili": [...],    # B 站排行/相关视频
            "weibo": [...],       # 微博热搜/相关话题
            "baidu": [...]        # 百度新闻
        }
    """
    print(f"[Domestic Sniffer V3] 🕵️‍♂️ 正在采集简中互联网关于【{keyword}】的讨论...")
    
    # 并行采集 (简化为串行，实际可用 asyncio)
    zhihu_results = fetch_zhihu_data(keyword, limit=10)
    bilibili_results = fetch_bilibili_data(keyword, limit=10)
    weibo_results = fetch_weibo_data(keyword, limit=10)
    baidu_results = fetch_baidu_news(keyword, limit=5)
    
    emotions = {
        "keyword": keyword,
        "zhihu": zhihu_results,
        "bilibili": bilibili_results,
        "weibo": weibo_results,
        "baidu": baidu_results,
    }
    
    total = len(zhihu_results) + len(bilibili_results) + len(weibo_results) + len(baidu_results)
    print(f"[Domestic Sniffer V3] ✅ 采集完成，共 {total} 条数据")
    
    return emotions


if __name__ == "__main__":
    import sys
    kw = sys.argv[1] if len(sys.argv) > 1 else "AI 教育"
    res = sniff_domestic_emotions(kw)
    
    print(f"\n=== 数据统计 ===")
    print(f"知乎：{len(res['zhihu'])} 条")
    print(f"B 站：{len(res['bilibili'])} 条")
    print(f"微博：{len(res['weibo'])} 条")
    print(f"百度：{len(res['baidu'])} 条")
    
    # 打印示例
    if res['zhihu']:
        print(f"\n知乎示例：{res['zhihu'][0]['title'][:50]}")
    if res['bilibili']:
        print(f"B 站示例：{res['bilibili'][0]['title'][:50]}")
