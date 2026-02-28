#!/usr/bin/env python3
"""
【知乎直连采集器】zhihu_direct.py
直接调用知乎热榜 API，无需 RSSHub 中间层。

API: https://www.zhihu.com/api/v3/feed/topstory/hot
"""

import urllib.request
import json
from typing import List, Dict, Any

ZHIHU_HOT_API = "https://www.zhihu.com/api/v3/feed/topstory/hot?limit=20"

def fetch_zhihu_hot(limit: int = 20) -> List[Dict[str, Any]]:
    """
    获取知乎热榜
    
    Args:
        limit: 返回数量 (最大 50)
    
    Returns:
        热榜列表，每项包含：
        - title: 问题标题
        - excerpt: 问题简介
        - url: 问题链接
        - answer_count: 回答数
        - follower_count: 关注人数
        - hot_score: 热度值
    """
    req = urllib.request.Request(
        ZHIHU_HOT_API,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            targets = data.get('data', [])
            
            results = []
            for item in targets[:limit]:
                target = item.get('target', {})
                if not target:
                    continue
                
                results.append({
                    "platform": "Zhihu",
                    "title": target.get('title', '')[:100],
                    "excerpt": target.get('excerpt', '')[:200],
                    "url": f"https://www.zhihu.com/question/{target.get('id', '')}",
                    "answer_count": target.get('answer_count', 0),
                    "follower_count": target.get('follower_count', 0),
                    "hot_score": target.get('hot', 0),
                })
            
            print(f"    [知乎直连] ✅ 获取 {len(results)} 条热榜")
            return results
            
    except Exception as e:
        print(f"    [知乎直连] ⚠️ 请求失败：{e}")
        return []

def search_zhihu_by_keyword(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    根据关键词搜索知乎内容 (简化版：从热榜中过滤)
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量
    
    Returns:
        相关内容列表
    """
    hot_list = fetch_zhihu_hot(limit=50)
    
    # 简单关键词匹配 (中文不需要 lower())
    filtered = [
        item for item in hot_list
        if keyword in item['title'] or keyword in item['excerpt']
    ][:limit]
    
    # 如果没有精确匹配，返回热榜前 N 条作为降级
    if not filtered:
        filtered = hot_list[:limit]
        print(f"    [知乎直连] ⚠️ 无精确匹配，返回热榜 Top{limit}")
    else:
        print(f"    [知乎直连] ✅ 匹配 {len(filtered)} 条相关内容")
    
    return filtered

if __name__ == "__main__":
    # 测试
    results = fetch_zhihu_hot(limit=10)
    print(json.dumps(results[:3], ensure_ascii=False, indent=2))
