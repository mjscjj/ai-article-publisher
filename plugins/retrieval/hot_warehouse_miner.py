#!/usr/bin/env python3
"""
【热点聚能挖掘器】hot_warehouse_miner.py
纯离线：从本地 data/hotnews/daily/ 的 unified 仓库中筛选关键词命中的热点记录。
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

BASE_DIR = Path(__file__).resolve().parents[2]
DAILY_DIR = BASE_DIR / "data" / "hotnews" / "daily"


def _safe_float(val: Any) -> float:
    try:
        return float(val)
    except Exception:
        return 0.0


def _load_unified_items(date_str: str) -> list[dict]:
    file_path = DAILY_DIR / f"{date_str}_unified.json"
    if not file_path.exists():
        return []
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    if isinstance(data, dict):
        items = data.get("items", [])
        return items if isinstance(items, list) else []
    if isinstance(data, list):
        return data
    return []


def _match_title(title: str, keywords: Iterable[str]) -> bool:
    if not title:
        return False
    lower_title = title.lower()
    for kw in keywords:
        if kw and kw.lower() in lower_title:
            return True
    return False


def mine_local_warehouse(keywords: list[str], top_n: int = 15) -> list[dict]:
    """
    从本地仓库中挖掘热点：
    - 读取今日与昨日 unified.json
    - 标题命中任意关键词则入围
    - 输出 platform/title/url/score
    - 按 score 降序排序
    """
    if not keywords:
        return []

    today = datetime.now().date()
    dates = [today, today - timedelta(days=1)]

    candidates: list[dict] = []
    for d in dates:
        date_str = d.strftime("%Y-%m-%d")
        items = _load_unified_items(date_str)
        for item in items:
            title = str(item.get("title", ""))
            if _match_title(title, keywords):
                candidates.append(
                    {
                        "platform": item.get("platform", ""),
                        "title": title,
                        "url": item.get("url", ""),
                        "score": item.get("score", 0),
                    }
                )

    candidates.sort(key=lambda x: _safe_float(x.get("score")), reverse=True)
    return candidates[: max(top_n, 0)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="本地热点仓库挖掘器")
    parser.add_argument(
        "--keys",
        type=str,
        default="",
        help="关键词串，空格分隔，如: 'AI 大模型 苹果'",
    )
    parser.add_argument("--top", type=int, default=15, help="返回条数")
    args = parser.parse_args()

    keywords = [k.strip() for k in args.keys.split() if k.strip()]
    results = mine_local_warehouse(keywords, top_n=args.top)
    print(json.dumps(results, ensure_ascii=False, indent=2))
