#!/usr/bin/env python3
"""
【微博直连采集器】weibo_direct.py
使用 curl_cffi 绕过反爬，获取微博热搜。

备用方案：使用微博开放平台 API (需要 AppKey)
"""

import json
from typing import List, Dict, Any

try:
    from curl_cffi import requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False
    import urllib.request

WEIBO_HOT_API = "https://s.weibo.com/top/summary"

def fetch_weibo_hot(limit: int = 20) -> List[Dict[str, Any]]:
    """
    获取微博热搜榜
    """
    if not HAS_CURL_CFFI:
        print("    [微博直连] ⚠️ curl_cffi 未安装，降级使用 urllib")
        return _fetch_weibo_urllib(limit)
    
    try:
        # 使用 curl_cffi 模拟真实浏览器
        response = requests.get(
            WEIBO_HOT_API,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            },
            impersonate='chrome120',  # 关键：模拟 Chrome 120
            timeout=15,
        )
        
        html = response.text
        return _parse_weibo_html(html, limit)
        
    except Exception as e:
        print(f"    [微博直连] ⚠️ 请求失败：{e}")
        return _fetch_weibo_urllib(limit)

def _fetch_weibo_urllib(limit: int) -> List[Dict]:
    """降级方案：使用 urllib"""
    try:
        req = urllib.request.Request(
            WEIBO_HOT_API,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return _parse_weibo_html(html, limit)
    except Exception as e:
        print(f"    [微博直连] ⚠️ urllib 也失败：{e}")
        # 最终降级：返回 Mock 数据
        return _get_weibo_mock(limit)

def _parse_weibo_html(html: str, limit: int) -> List[Dict]:
    """解析微博 HTML"""
    import re
    
    # 调试：保存 HTML
    # with open('/tmp/weibo.html', 'w') as f: f.write(html)
    
    # 微博热搜结构：<td class="td-02"><a href="...">标题</a></td>
    pattern = r'<td class="td-02">\s*<a\s+href="([^"]+)"[^>]*>([^<]+)</a>'
    matches = re.findall(pattern, html, re.S)
    
    results = []
    for i, (url, title) in enumerate(matches[:limit]):
        if url.startswith('/'):
            url = f"https://s.weibo.com{url}"
        
        results.append({
            "platform": "Weibo",
            "title": title.strip(),
            "url": url,
            "rank": i + 1,
        })
    
    if results:
        print(f"    [微博直连] ✅ 获取 {len(results)} 条热搜")
    else:
        print(f"    [微博直连] ⚠️ 解析失败，使用 Mock 数据")
        return _get_weibo_mock(limit)
    
    return results

def _get_weibo_mock(limit: int) -> List[Dict]:
    """
    Mock 数据 (当真实请求失败时)
    实际使用时应接入微博开放平台 API
    """
    # 这些是常见的热搜话题类型
    mock_topics = [
        "AI 技术最新突破",
        "教育数字化转型",
        "大模型应用落地",
        "科技创新政策",
        "人工智能伦理",
        "智慧校园建设",
        "教育公平讨论",
        "科技人才培养",
        "数字经济趋势",
        "互联网 + 教育",
    ]
    
    results = []
    for i in range(min(limit, len(mock_topics))):
        results.append({
            "platform": "Weibo",
            "title": mock_topics[i],
            "url": f"https://s.weibo.com/weibo?q={mock_topics[i]}",
            "rank": i + 1,
            "is_mock": True,
        })
    
    print(f"    [微博直连] ⚠️ 返回 {len(results)} 条 Mock 数据")
    return results

def search_weibo_by_keyword(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """根据关键词搜索微博"""
    hot_list = fetch_weibo_hot(limit=50)
    
    # 关键词匹配
    filtered = [
        item for item in hot_list
        if keyword in item['title']
    ][:limit]
    
    if not filtered:
        filtered = hot_list[:limit]
        print(f"    [微博直连] ⚠️ 无精确匹配，返回热搜 Top{limit}")
    else:
        print(f"    [微博直连] ✅ 匹配 {len(filtered)} 条相关内容")
    
    return filtered

if __name__ == "__main__":
    results = fetch_weibo_hot(limit=10)
    print(json.dumps(results[:3], ensure_ascii=False, indent=2))
