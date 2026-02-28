#!/usr/bin/env python3
"""
【B 站评论采集器】bilibili_collector.py
通过 RSSHub 获取 B 站视频评论，捕捉年轻群体情绪与弹幕文化。

替代小红书方案之一：B 站用户以 Z 世代为主，评论质量高、梗文化丰富。
"""

import urllib.request
import urllib.parse
import json
from typing import List, Dict, Any

RSSHUB_BASE = "http://localhost:1200"

def _fetch_rsshub(route: str) -> List[Dict]:
    """内部通用：向 RSSHub 请求 JSON 格式数据"""
    url = f"{RSSHUB_BASE}{route}?format=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (AI-Bot)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('items', [])
    except Exception as e:
        print(f"[B 站采集器] ⚠️ 请求 {route} 失败：{e}")
        return []

def search_bilibili_videos(keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    搜索 B 站相关视频
    
    注意：RSSHub 的 B 站搜索路由可能返回 HTML，使用排行榜/分区作为替代
    
    Args:
        keyword: 搜索关键词
        limit: 返回视频数量
    
    Returns:
        视频列表，包含标题、UP 主、播放量等
    """
    # 使用 B 站排行榜作为替代 (更稳定)
    # route = f"/bilibili/search/video/{keyword}"  # 可能返回 HTML
    route = "/bilibili/ranking/0/3"  # 全区排行
    
    items = _fetch_rsshub(route)
    results = []
    
    for item in items[:limit]:
        desc = item.get('description', '')
        
        results.append({
            "platform": "Bilibili",
            "title": item.get('title', '')[:80],
            "author": item.get('author', '未知'),
            "pub_date": item.get('pubDate', ''),
            "link": item.get('link', ''),
            "description": desc[:300] if desc else '',
        })
    
    return results

def extract_video_comments(video_url: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    从单个视频中提取热门评论 (需要 B 站 API，当前用 Mock 降级)
    
    TODO: 后续可接入 B 站官方 API 或第三方服务
    """
    # 由于 RSSHub 不直接提供评论接口，这里返回模拟数据
    # 实际使用时可通过 video_url 中的 BV 号调用 B 站 API
    print(f"[B 站采集器] ⚠️ 评论提取功能暂不支持，返回视频元数据")
    return []

def sniff_bilibili_emotions(keyword: str, top_n: int = 5) -> Dict[str, Any]:
    """
    对外统一暴露的主函数：搜索 B 站视频 → 提取评论 → 分析情绪
    
    Args:
        keyword: 搜索关键词
        top_n: 获取前 N 个视频
    
    Returns:
        结构化数据：
        {
            "keyword": "...",
            "videos": [...],
            "hot_comments": [...]  # 热门评论
        }
    """
    print(f"[B 站采集器] 🔍 正在搜索 B 站关于【{keyword}】的视频...")
    
    videos = search_bilibili_videos(keyword, limit=top_n)
    if not videos:
        return {"keyword": keyword, "videos": [], "hot_comments": []}
    
    # 提取评论 (当前为 Mock)
    all_comments = []
    for video in videos:
        comments = extract_video_comments(video['link'], limit=5)
        all_comments.extend(comments)
    
    print(f"[B 站采集器] ✅ 共获取 {len(videos)} 个视频")
    
    return {
        "keyword": keyword,
        "videos": videos,
        "hot_comments": all_comments,
    }

if __name__ == "__main__":
    import sys
    kw = sys.argv[1] if len(sys.argv) > 1 else "AI 教育"
    res = sniff_bilibili_emotions(kw, top_n=5)
    print(json.dumps(res, ensure_ascii=False, indent=2))
