#!/usr/bin/env python3
"""
【B 站直连采集器】bilibili_direct.py
直接调用 B 站排行榜 API，无需 RSSHub 中间层。

API: https://api.bilibili.com/x/web-interface/ranking/v2
"""

import urllib.request
import json
from typing import List, Dict, Any

BILIBILI_RANKING_API = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all&ps=20"

def fetch_bilibili_ranking(limit: int = 20) -> List[Dict[str, Any]]:
    """
    获取 B 站全站排行榜
    
    Args:
        limit: 返回数量 (最大 100)
    
    Returns:
        排行榜列表，每项包含：
        - title: 视频标题
        - author: UP 主
        - url: 视频链接
        - play_count: 播放量
        - like_count: 点赞数
        - coin_count: 投币数
        - danmaku_count: 弹幕数
    """
    req = urllib.request.Request(
        BILIBILI_RANKING_API,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.bilibili.com',
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('code') != 0:
                print(f"    [B 站直连] ⚠️ API 返回错误：{data.get('message', '')}")
                return []
            
            items = data.get('data', {}).get('list', [])
            
            results = []
            for item in items[:limit]:
                results.append({
                    "platform": "Bilibili",
                    "title": item.get('title', '')[:100],
                    "author": item.get('owner', {}).get('name', '未知'),
                    "url": item.get('short_link_v2', '') or f"https://b23.tv/{item.get('bvid', '')}",
                    "play_count": item.get('stat', {}).get('view', 0),
                    "like_count": item.get('stat', {}).get('like', 0),
                    "coin_count": item.get('stat', {}).get('coin', 0),
                    "danmaku_count": item.get('stat', {}).get('danmaku', 0),
                    "duration": item.get('duration', 0),
                })
            
            print(f"    [B 站直连] ✅ 获取 {len(results)} 条排行")
            return results
            
    except Exception as e:
        print(f"    [B 站直连] ⚠️ 请求失败：{e}")
        return []

def search_bilibili_by_keyword(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    根据关键词搜索 B 站视频 (简化版：从排行榜中过滤)
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量
    
    Returns:
        相关内容列表
    """
    ranking = fetch_bilibili_ranking(limit=50)
    
    # 简单关键词匹配 (中文不需要 lower())
    filtered = [
        item for item in ranking
        if keyword in item['title']
    ][:limit]
    
    # 如果没有精确匹配，返回排行榜前 N 条作为降级
    if not filtered:
        filtered = ranking[:limit]
        print(f"    [B 站直连] ⚠️ 无精确匹配，返回排行 Top{limit}")
    else:
        print(f"    [B 站直连] ✅ 匹配 {len(filtered)} 条相关内容")
    
    return filtered

if __name__ == "__main__":
    # 测试
    results = fetch_bilibili_ranking(limit=10)
    print(json.dumps(results[:3], ensure_ascii=False, indent=2))
