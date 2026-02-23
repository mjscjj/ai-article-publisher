#!/usr/bin/env python3
"""
教育热点采集脚本
整合多个教育相关数据源
"""

import json
import sys
import argparse
from urllib.request import urlopen, Request
from urllib.parse import quote
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_rss(rss_url, limit=10):
    """获取RSS内容"""
    try:
        req = Request(rss_url, headers=HEADERS)
        with urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
        
        items = []
        # 简单解析 RSS
        item_pattern = r'<item>.*?<title><!\[CDATA\[(.*?)\]\]></title>.*?<link>(.*?)</link>'
        matches = re.findall(item_pattern, content, re.DOTALL)
        
        for title, link in matches[:limit]:
            items.append({
                "title": title.strip(),
                "url": link.strip(),
                "source": "RSS"
            })
        
        # 如果CDATA解析失败，尝试普通解析
        if not items:
            item_pattern = r'<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>'
            matches = re.findall(item_pattern, content, re.DOTALL)
            for title, link in matches[:limit]:
                items.append({
                    "title": title.strip(),
                    "url": link.strip(),
                    "source": "RSS"
                })
        
        return items
    except Exception as e:
        sys.stderr.write(f"RSS获取失败: {e}\n")
        return []

def fetch_rsshub(route, rsshub_base="http://localhost:1200", limit=10):
    """通过RSSHub获取内容"""
    url = f"{rsshub_base}{route}"
    return fetch_rss(url, limit)

def collect_education_news(limit=10):
    """收集教育热点"""
    results = []
    
    # 1. 少数派（学习效率相关）
    sys.stderr.write("[少数派] 获取中...\n")
    items = fetch_rsshub("/sspai/index", limit=limit//2)
    for item in items:
        item["source"] = "少数派"
        item["category"] = "学习方法"
    results.extend(items)
    
    # 2. V2EX（教育/学习相关）
    sys.stderr.write("[V2EX] 获取中...\n")
    items = fetch_rsshub("/v2ex/topics/hot", limit=limit)
    keywords = ["学习", "教育", "AI", "编程", "知识"]
    for item in items:
        if any(k in item["title"] for k in keywords):
            item["source"] = "V2EX"
            item["category"] = "技术教育"
            results.append(item)
    
    # 3. IT之家（教育科技）
    sys.stderr.write("[IT之家] 获取中...\n")
    items = fetch_rsshub("/ithome/ranking/7days", limit=limit//2)
    for item in items:
        item["source"] = "IT之家"
        item["category"] = "教育科技"
    results.extend(items)
    
    # 4. Hacker News（教育/AI）
    sys.stderr.write("[Hacker News] 获取中...\n")
    items = fetch_rsshub("/hackernews/best", limit=limit)
    edu_keywords = ["education", "learn", "AI", "teach", "school", "student"]
    for item in items:
        if any(k.lower() in item["title"].lower() for k in edu_keywords):
            item["source"] = "Hacker News"
            item["category"] = "国际教育"
            results.append(item)
    
    return results[:limit*3]

def collect_psychology_news(limit=10):
    """收集心理学热点"""
    results = []
    
    # 1. 少数派（心理学相关）
    items = fetch_rsshub("/sspai/index", limit=limit)
    keywords = ["心理", "情绪", "焦虑", "成长", "思维"]
    for item in items:
        if any(k in item["title"] for k in keywords):
            item["source"] = "少数派"
            item["category"] = "心理学"
            results.append(item)
    
    # 2. Hacker News（心理学研究）
    items = fetch_rsshub("/hackernews/best", limit=limit)
    keywords = ["psychology", "brain", "mind", "mental", "behavior"]
    for item in items:
        if any(k.lower() in item["title"].lower() for k in keywords):
            item["source"] = "Hacker News"
            item["category"] = "心理学研究"
            results.append(item)
    
    return results[:limit*2]

def collect_learning_methods(limit=10):
    """收集学习方法内容"""
    results = []
    
    # 1. 少数派
    items = fetch_rsshub("/sspai/index", limit=limit)
    keywords = ["学习", "效率", "方法", "技巧", "工具", "知识"]
    for item in items:
        if any(k in item["title"] for k in keywords):
            item["source"] = "少数派"
            item["category"] = "学习方法"
            results.append(item)
    
    # 2. 掘金
    items = fetch_rsshub("/juejin/trending/all/monthly", limit=limit//2)
    for item in items:
        item["source"] = "掘金"
        item["category"] = "编程学习"
    results.extend(items)
    
    return results[:limit*2]

def main():
    parser = argparse.ArgumentParser(description='教育热点采集')
    parser.add_argument('--type', '-t', default='all', 
                       choices=['all', 'education', 'psychology', 'learning'],
                       help='内容类型')
    parser.add_argument('--limit', '-n', type=int, default=10, help='每种类型数量')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有类型')
    args = parser.parse_args()
    
    if args.list:
        print("可用类型:")
        print("  all        - 全部教育内容")
        print("  education  - 教育新闻")
        print("  psychology - 心理学内容")
        print("  learning   - 学习方法")
        return
    
    results = []
    
    if args.type == 'all':
        results.extend(collect_education_news(args.limit))
        results.extend(collect_psychology_news(args.limit))
        results.extend(collect_learning_methods(args.limit))
    elif args.type == 'education':
        results = collect_education_news(args.limit)
    elif args.type == 'psychology':
        results = collect_psychology_news(args.limit)
    elif args.type == 'learning':
        results = collect_learning_methods(args.limit)
    
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
