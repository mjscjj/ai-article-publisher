#!/usr/bin/env python3
"""
【什么值得买采集器】smzdm_collector.py
通过 RSSHub 获取什么值得买的爆料和评论，捕捉消费决策与避坑指南。

替代小红书方案之二：SMZDM 用户以理性消费者为主，评论真实、干货多。
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
        print(f"[什么值得买采集器] ⚠️ 请求 {route} 失败：{e}")
        return []

def search_smzdm_deals(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    搜索什么值得买的爆料/文章
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量
    
    Returns:
        爆料列表，包含标题、价格、评论数等
    """
    encoded_kw = urllib.parse.quote(keyword)
    route = f"/smzdm/keyword/{encoded_kw}"
    
    items = _fetch_rsshub(route)
    results = []
    
    for item in items[:limit]:
        desc = item.get('description', '')
        
        results.append({
            "platform": "SMZDM",
            "title": item.get('title', '')[:100],
            "price": _extract_price(desc),
            "pub_date": item.get('pubDate', ''),
            "link": item.get('link', ''),
            "description": desc[:400] if desc else '',
        })
    
    return results

def _extract_price(text: str) -> str:
    """从描述中提取价格信息"""
    import re
    match = re.search(r'[\u00a5¥]\s*(\d+(?:\.\d+)?)', text)
    if match:
        return f"¥{match.group(1)}"
    return ""

def sniff_smzdm_opinions(keyword: str, top_n: int = 10) -> Dict[str, Any]:
    """
    对外统一暴露的主函数：搜索爆料 → 提取评论观点
    
    Args:
        keyword: 搜索关键词
        top_n: 获取前 N 条爆料
    
    Returns:
        结构化数据：
        {
            "keyword": "...",
            "deals": [...],
            "opinions": [...]  # 用户观点/避坑指南
        }
    """
    print(f"[什么值得买采集器] 🔍 正在搜索关于【{keyword}】的爆料和评测...")
    
    deals = search_smzdm_deals(keyword, limit=top_n)
    if not deals:
        return {"keyword": keyword, "deals": [], "opinions": []}
    
    # 从爆料描述中提取用户观点 (简化版，实际可抓取评论)
    opinions = []
    for deal in deals:
        desc = deal.get('description', '')
        if desc:
            # 提取关键观点句
            opinions.append({
                "source": "SMZDM",
                "content": desc[:200],
                "type": "爆料/评测",
            })
    
    print(f"[什么值得买采集器] ✅ 共获取 {len(deals)} 条爆料")
    
    return {
        "keyword": keyword,
        "deals": deals,
        "opinions": opinions,
    }

if __name__ == "__main__":
    import sys
    kw = sys.argv[1] if len(sys.argv) > 1 else "AI 学习机"
    res = sniff_smzdm_opinions(kw, top_n=10)
    print(json.dumps(res, ensure_ascii=False, indent=2))
