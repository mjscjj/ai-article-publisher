#!/usr/bin/env python3
"""
【小红书 MCP 客户端】xiaohongshu_mcp_client.py
通过 HTTP API 调用 xiaohongshu-mcp 服务，获取高赞笔记与神评论。

部署参考：https://github.com/xpzouying/xiaohongshu-mcp
- Docker: docker run -p 8333:8333 xpzouying/xiaohongshu-mcp
- 或直接运行二进制文件

MCP 功能:
- search_notes: 搜索笔记
- get_note_detail: 获取帖子详情 (含评论)
- list_notes: 获取推荐列表
"""

import urllib.request
import urllib.parse
import json
from typing import Optional, List, Dict, Any

# 默认 MCP 服务地址 (根据实际部署修改)
MCP_BASE_URL = "http://localhost:8333"

def _call_mcp_api(method: str, params: dict) -> Optional[dict]:
    """内部通用：调用 MCP HTTP API"""
    url = f"{MCP_BASE_URL}/{method}"
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(params).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"[Xiaohongshu MCP] ⚠️ 调用 {method} 失败：{e}")
        return None

def search_notes(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    搜索小红书笔记
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量限制
    
    Returns:
        笔记列表，每项包含：
        - note_id: 笔记 ID
        - title: 标题
        - desc: 描述
        - user: 用户信息
        - xsec_token: 安全令牌 (用于获取详情)
    """
    result = _call_mcp_api("search", {"keyword": keyword})
    if not result or "data" not in result:
        return []
    
    notes = result["data"][:limit]
    return [
        {
            "note_id": n.get("id", ""),
            "title": n.get("title", "")[:50],
            "desc": n.get("desc", "")[:200],
            "user": n.get("user", {}),
            "xsec_token": n.get("xsec_token", ""),
            "like_count": n.get("interact_info", {}).get("liked_count", 0),
            "collect_count": n.get("interact_info", {}).get("collected_count", 0),
            "comment_count": n.get("interact_info", {}).get("comment_count", 0),
        }
        for n in notes
    ]

def get_note_detail(note_id: str, xsec_token: str) -> Optional[Dict[str, Any]]:
    """
    获取笔记详情 (含评论)
    
    Args:
        note_id: 笔记 ID
        xsec_token: 安全令牌 (从搜索结果中获取)
    
    Returns:
        笔记详情，包含：
        - title: 标题
        - desc: 正文
        - images: 图片链接列表
        - comments: 评论列表 (含子评论)
    """
    result = _call_mcp_api("get_note_detail", {
        "note_id": note_id,
        "xsec_token": xsec_token
    })
    if not result or "data" not in result:
        return None
    
    data = result["data"]
    return {
        "title": data.get("title", ""),
        "desc": data.get("desc", ""),
        "images": data.get("image_list", []),
        "like_count": data.get("interact_info", {}).get("liked_count", 0),
        "comments": data.get("comments", []),
    }

def extract_hot_comments(note_details: Dict[str, Any], limit: int = 5) -> List[Dict[str, str]]:
    """
    从高赞笔记中提取神评论
    
    Args:
        note_details: 笔记详情 (来自 get_note_detail)
        limit: 返回评论数量
    
    Returns:
        评论列表，每项包含：
        - content: 评论内容
        - like_count: 点赞数
        - user: 用户名
    """
    comments = note_details.get("comments", [])
    # 按点赞数排序
    sorted_comments = sorted(
        comments,
        key=lambda c: c.get("like_count", 0) + c.get("sub_comment_count", 0) * 2,
        reverse=True
    )
    
    return [
        {
            "content": c.get("content", "")[:300],
            "like_count": c.get("like_count", 0),
            "user": c.get("user_info", {}).get("nickname", "匿名用户"),
        }
        for c in sorted_comments[:limit]
    ]

def sniff_xiaohongshu(keyword: str, top_n: int = 3, comments_per_note: int = 5) -> Dict[str, Any]:
    """
    对外统一暴露的主函数：搜素关键词 → 获取 Top N 笔记 → 提取神评论
    
    Args:
        keyword: 搜索关键词
        top_n: 获取前 N 篇笔记
        comments_per_note: 每篇笔记提取多少条评论
    
    Returns:
        结构化数据：
        {
            "keyword": "...",
            "notes": [...],
            "hot_comments": [...]  # 所有笔记的神评论合并
        }
    """
    print(f"[Xiaohongshu MCP] 🔍 正在搜索小红书关于【{keyword}】的高赞笔记...")
    
    # Step 1: 搜索笔记
    notes = search_notes(keyword, limit=top_n)
    if not notes:
        return {"keyword": keyword, "notes": [], "hot_comments": []}
    
    # Step 2: 获取每篇笔记的详情和评论
    all_hot_comments = []
    for note in notes:
        print(f"  └─ 获取笔记详情：{note['title']}")
        detail = get_note_detail(note["note_id"], note["xsec_token"])
        if detail:
            hot_comments = extract_hot_comments(detail, limit=comments_per_note)
            all_hot_comments.extend(hot_comments)
            # 把评论附加到笔记对象上
            note["hot_comments"] = hot_comments
    
    print(f"[Xiaohongshu MCP] ✅ 共获取 {len(all_hot_comments)} 条神评论")
    
    return {
        "keyword": keyword,
        "notes": notes,
        "hot_comments": all_hot_comments,
    }

if __name__ == "__main__":
    import sys
    kw = sys.argv[1] if len(sys.argv) > 1 else "AI 教育"
    res = sniff_xiaohongshu(kw, top_n=3, comments_per_note=5)
    print(json.dumps(res, ensure_ascii=False, indent=2))
