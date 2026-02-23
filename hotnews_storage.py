#!/usr/bin/env python3
"""
热点数据存储系统
结构化存储热点数据，支持索引和查询
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.request import urlopen, Request
from urllib.parse import quote
import re

# 配置
STORAGE_DIR = "/root/.openclaw/workspace-writer/ai-article-publisher/data/hotnews"
RSSHUB_BASE = "http://localhost:1200"

# 数据源配置
SOURCES = {
    # ===== 综合热点 =====
    "weibo": {
        "name": "微博热搜",
        "platform": "微博",
        "url": "/weibo/search/hot",
        "category": "综合"
    },
    "zhihu": {
        "name": "知乎热榜",
        "platform": "知乎",
        "url": "/zhihu/hot",
        "category": "综合"
    },
    "zhihu_daily": {
        "name": "知乎日报",
        "platform": "知乎",
        "url": "/zhihu/daily",
        "category": "精选"
    },
    
    # ===== 科技媒体 =====
    "hackernews": {
        "name": "Hacker News",
        "platform": "Hacker News",
        "url": "/hackernews/best",
        "category": "科技"
    },
    "github": {
        "name": "GitHub Trending",
        "platform": "GitHub",
        "url": "/github/trending/daily",
        "category": "科技"
    },
    "v2ex": {
        "name": "V2EX",
        "platform": "V2EX",
        "url": "/v2ex/topics/hot",
        "category": "科技"
    },
    "sspai": {
        "name": "少数派",
        "platform": "少数派",
        "url": "/sspai/index",
        "category": "科技"
    },
    "ithome": {
        "name": "IT之家",
        "platform": "IT之家",
        "url": "/ithome/ranking/7days",
        "category": "科技"
    },
    "juejin": {
        "name": "掘金",
        "platform": "掘金",
        "url": "/juejin/trending/all/monthly",
        "category": "科技"
    },
    "36kr": {
        "name": "36氪",
        "platform": "36氪",
        "url": "/36kr/news/latest",
        "category": "科技"
    },
    
    # ===== 财经 =====
    "cls": {
        "name": "财联社",
        "platform": "财联社",
        "url": "/cls/telegraph",
        "category": "财经"
    },
    "wallstreetcn": {
        "name": "华尔街见闻",
        "platform": "华尔街见闻",
        "url": "/wallstreetcn/news/global",
        "category": "财经"
    },
    
    # ===== 新闻 =====
    "thepaper": {
        "name": "澎湃新闻",
        "platform": "澎湃新闻",
        "url": "/thepaper/featured",
        "category": "新闻"
    },
    
    # ===== 心理学 =====
    "douban_psychology": {
        "name": "豆瓣心理学",
        "platform": "豆瓣",
        "url": "/douban/group/psychology",
        "category": "心理学"
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def generate_id(title: str, source: str, timestamp: str) -> str:
    """生成唯一ID"""
    content = f"{title}_{source}_{timestamp}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def parse_rss(rss_url: str, source_id: str) -> List[Dict]:
    """解析RSS内容"""
    try:
        full_url = f"{RSSHUB_BASE}{rss_url}"
        req = Request(full_url, headers=HEADERS)
        with urlopen(req, timeout=20) as resp:
            content = resp.read().decode('utf-8')
        
        items = []
        # 解析 RSS item
        item_pattern = r'<item>.*?<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>.*?<link>(.*?)</link>.*?(?:<pubDate>(.*?)</pubDate>)?.*?</item>'
        matches = re.findall(item_pattern, content, re.DOTALL)
        
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        
        for title, link, pubdate in matches:
            title = title.strip()
            link = link.strip()
            
            if not title or title == source_id:
                continue
            
            item = {
                "id": generate_id(title, source_id, timestamp),
                "title": title,
                "url": link,
                "source_id": source_id,
                "source_name": SOURCES[source_id]["name"],
                "platform": SOURCES[source_id]["platform"],
                "category": SOURCES[source_id]["category"],
                "crawl_time": timestamp,
                "crawl_date": date_str,
                "pub_time": pubdate.strip() if pubdate else None
            }
            items.append(item)
        
        return items
    except Exception as e:
        print(f"[{source_id}] 获取失败: {str(e)[:50]}")
        return []


def save_to_daily(items: List[Dict], date_str: str = None):
    """保存到日期文件（按标题去重）"""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 按日期存储
    daily_file = os.path.join(STORAGE_DIR, "daily", f"{date_str}.json")
    ensure_dir(os.path.dirname(daily_file))
    
    # 读取已有数据
    existing = {}
    if os.path.exists(daily_file):
        with open(daily_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    
    # 建立标题索引（用于去重）
    title_to_id = {item["title"]: item_id for item_id, item in existing.items()}
    
    # 合并新数据（按标题去重）
    new_count = 0
    for item in items:
        title = item["title"]
        if title in title_to_id:
            # 已存在，更新 crawl_time 但保留原数据
            existing[title_to_id[title]]["crawl_time"] = item["crawl_time"]
        else:
            # 新热点，添加
            existing[item["id"]] = item
            title_to_id[title] = item["id"]
            new_count += 1
    
    # 保存
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    return new_count


def save_to_source(items: List[Dict], source_id: str):
    """保存到来源索引（按标题去重）"""
    source_file = os.path.join(STORAGE_DIR, "by_source", f"{source_id}.json")
    ensure_dir(os.path.dirname(source_file))
    
    # 读取已有数据
    existing = []
    if os.path.exists(source_file):
        with open(source_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    
    # 建立标题索引
    title_set = {item["title"] for item in existing}
    
    # 合并新数据（按标题去重）
    for item in items:
        if item["title"] not in title_set:
            existing.append(item)
            title_set.add(item["title"])
    
    # 只保留最近 500 条
    existing = existing[-500:]
    
    # 保存
    with open(source_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


def update_index(items: List[Dict]):
    """更新索引"""
    index_file = os.path.join(STORAGE_DIR, "index.json")
    ensure_dir(STORAGE_DIR)
    
    # 读取索引
    index = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_items": 0,
        "sources": {},
        "categories": {},
        "dates": {}
    }
    
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    
    # 更新统计
    for item in items:
        source_id = item["source_id"]
        category = item["category"]
        date = item["crawl_date"]
        
        # 来源统计
        if source_id not in index["sources"]:
            index["sources"][source_id] = {"name": item["source_name"], "count": 0}
        index["sources"][source_id]["count"] += 1
        
        # 分类统计
        if category not in index["categories"]:
            index["categories"][category] = 0
        index["categories"][category] += 1
        
        # 日期统计
        if date not in index["dates"]:
            index["dates"][date] = 0
        index["dates"][date] += 1
    
    index["total_items"] = sum(s["count"] for s in index["sources"].values())
    index["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 保存
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def crawl_all_sources(sources: List[str] = None, include_extended: bool = True) -> Dict[str, int]:
    """采集所有数据源（包括扩展源）"""
    if sources is None:
        sources = list(SOURCES.keys())
    
    print(f"\n{'='*60}")
    print(f"热点采集开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    results = {}
    all_items = []
    total_new = 0
    
    # 1. 采集基础数据源 (RSSHub)
    print("【基础数据源 - RSSHub】")
    print("-" * 40)
    for source_id in sources:
        if source_id not in SOURCES:
            continue
        
        source = SOURCES[source_id]
        print(f"[{source['name']}] 采集中...")
        
        items = parse_rss(source["url"], source_id)
        
        if items:
            new_count = save_to_daily(items)
            save_to_source(items, source_id)
            all_items.extend(items)
            
            print(f"[{source['name']}] ✅ 获取 {len(items)} 条，新增 {new_count} 条")
            results[source_id] = new_count
            total_new += new_count
        else:
            print(f"[{source['name']}] ❌ 获取失败")
            results[source_id] = 0
    
    # 2. 采集扩展数据源（直接RSS）
    if include_extended:
        print(f"\n【扩展数据源 - 直接RSS】")
        print("-" * 40)
        
        extended = get_extended_sources()
        for source_id, source_info in extended.items():
            print(f"[{source_info['name']}] 采集中...")
            items = fetch_extended_rss(source_info["url"], source_id, source_info)
            
            if items:
                new_count = save_to_daily(items)
                save_to_source(items, source_id)
                all_items.extend(items)
                
                print(f"[{source_info['name']}] ✅ 获取 {len(items)} 条，新增 {new_count} 条")
                results[source_id] = new_count
                total_new += new_count
            else:
                print(f"[{source_info['name']}] ❌ 获取失败")
                results[source_id] = 0
    
    # 更新总索引
    if all_items:
        update_index(all_items)
    
    print(f"\n{'='*60}")
    print(f"采集完成 - 共获取 {len(all_items)} 条，新增 {total_new} 条热点")
    print(f"{'='*60}\n")
    
    return results


def get_extended_sources() -> Dict:
    """获取可用的扩展数据源"""
    config_file = os.path.join(STORAGE_DIR, "extended_sources.json")
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("working_sources", {})
    return {}


def fetch_extended_rss(url: str, source_id: str, source_info: Dict) -> List[Dict]:
    """获取扩展RSS源"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/rss+xml,application/xml,text/xml,*/*"
        }
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
        
        items = []
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        
        # 解析 RSS
        patterns = [
            r'<item>.*?<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>.*?<link>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>',
            r'<entry>.*?<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>.*?<link[^>]*href="(.*?)"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                break
        
        for title, link in matches[:30]:
            title = title.strip()
            link = link.strip()
            
            if not title or len(title) < 5:
                continue
            
            item = {
                "id": generate_id(title, source_id, timestamp),
                "title": title,
                "url": link,
                "source_id": source_id,
                "source_name": source_info["name"],
                "platform": source_info["platform"],
                "category": source_info["category"],
                "crawl_time": timestamp,
                "crawl_date": date_str,
                "pub_time": None
            }
            items.append(item)
        
        return items
    except Exception as e:
        return []


def query_by_date(date_str: str) -> List[Dict]:
    """按日期查询"""
    daily_file = os.path.join(STORAGE_DIR, "daily", f"{date_str}.json")
    if os.path.exists(daily_file):
        with open(daily_file, 'r', encoding='utf-8') as f:
            return list(json.load(f).values())
    return []


def query_by_source(source_id: str, limit: int = 50) -> List[Dict]:
    """按来源查询"""
    source_file = os.path.join(STORAGE_DIR, "by_source", f"{source_id}.json")
    if os.path.exists(source_file):
        with open(source_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
            return items[-limit:]
    return []


def query_by_keyword(keyword: str, days: int = 7) -> List[Dict]:
    """按关键词查询"""
    results = []
    keyword_lower = keyword.lower()
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        items = query_by_date(date)
        for item in items:
            if keyword_lower in item["title"].lower():
                results.append(item)
    
    return results


def get_stats() -> Dict:
    """获取统计信息"""
    index_file = os.path.join(STORAGE_DIR, "index.json")
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def cleanup_old_data(days: int = 30) -> Dict:
    """清理旧数据"""
    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")
    
    daily_dir = os.path.join(STORAGE_DIR, "daily")
    removed_files = []
    removed_count = 0
    
    if os.path.exists(daily_dir):
        for filename in os.listdir(daily_dir):
            if filename.endswith(".json"):
                date_str = filename.replace(".json", "")
                if date_str < cutoff_str:
                    filepath = os.path.join(daily_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        removed_count += len(data)
                    os.remove(filepath)
                    removed_files.append(date_str)
    
    print(f"✅ 清理完成: 删除 {len(removed_files)} 天数据，共 {removed_count} 条热点")
    print(f"   清理日期: {', '.join(removed_files[:10])}{'...' if len(removed_files) > 10 else ''}")
    
    return {
        "removed_days": len(removed_files),
        "removed_items": removed_count,
        "dates": removed_files
    }


def generate_daily_report(date_str: str = None) -> Dict:
    """生成每日热点报告"""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    items = query_by_date(date_str)
    
    if not items:
        return {"error": f"无 {date_str} 数据"}
    
    # 统计
    sources = {}
    categories = {}
    keywords = {}
    
    for item in items:
        # 来源统计
        src = item["source_name"]
        sources[src] = sources.get(src, 0) + 1
        
        # 分类统计
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1
        
        # 关键词提取（简单版：提取标题中的中文词）
        title = item["title"]
        # 统计常见词
        for word in ["AI", "科技", "教育", "心理", "学习", "技术", "开发", "数据", "算法", "模型"]:
            if word in title:
                keywords[word] = keywords.get(word, 0) + 1
    
    # 热门标题
    sorted_items = sorted(items, key=lambda x: x.get("crawl_time", ""), reverse=True)
    
    report = {
        "date": date_str,
        "total": len(items),
        "sources": dict(sorted(sources.items(), key=lambda x: -x[1])),
        "categories": dict(sorted(categories.items(), key=lambda x: -x[1])),
        "top_keywords": dict(sorted(keywords.items(), key=lambda x: -x[1])[:10]),
        "latest_5": [{"title": i["title"], "source": i["source_name"]} for i in sorted_items[:5]]
    }
    
    # 打印报告
    print(f"\n{'='*60}")
    print(f"📊 热点日报 - {date_str}")
    print(f"{'='*60}")
    print(f"\n📈 总计: {report['total']} 条热点")
    
    print(f"\n📡 来源分布:")
    for src, count in list(report['sources'].items())[:5]:
        print(f"   {src}: {count} 条")
    
    print(f"\n🏷️ 分类分布:")
    for cat, count in report['categories'].items():
        print(f"   {cat}: {count} 条")
    
    if report['top_keywords']:
        print(f"\n🔑 热门关键词:")
        for kw, count in list(report['top_keywords'].items())[:5]:
            print(f"   {kw}: {count} 次")
    
    print(f"\n📰 最新热点:")
    for i, item in enumerate(report['latest_5'], 1):
        print(f"   {i}. [{item['source']}] {item['title'][:30]}...")
    
    print(f"\n{'='*60}\n")
    
    return report


def retry_failed_sources(failed_sources: List[str], max_retries: int = 3) -> Dict:
    """重试失败的采集"""
    results = {}
    
    for source_id in failed_sources:
        if source_id not in SOURCES:
            continue
        
        source = SOURCES[source_id]
        for attempt in range(max_retries):
            try:
                print(f"[{source['name']}] 重试 {attempt + 1}/{max_retries}...")
                items = parse_rss(source["url"], source_id)
                if items:
                    save_to_daily(items)
                    save_to_source(items, source_id)
                    results[source_id] = len(items)
                    print(f"[{source['name']}] ✅ 重试成功: {len(items)} 条")
                    break
            except Exception as e:
                print(f"[{source['name']}] ❌ 重试失败: {str(e)[:30]}")
                results[source_id] = 0
    
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='热点数据存储系统')
    parser.add_argument('--crawl', '-c', action='store_true', help='采集所有数据源')
    parser.add_argument('--sources', '-s', default='', help='指定数据源（逗号分隔）')
    parser.add_argument('--query-date', '-d', help='按日期查询 (YYYY-MM-DD)')
    parser.add_argument('--query-source', help='按来源查询')
    parser.add_argument('--query-keyword', '-k', help='按关键词查询')
    parser.add_argument('--stats', action='store_true', help='显示统计')
    parser.add_argument('--report', '-r', action='store_true', help='生成日报')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='清理DAYS天前的旧数据')
    parser.add_argument('--retry', action='store_true', help='重试失败的采集')
    args = parser.parse_args()
    
    if args.crawl:
        sources = args.sources.split(',') if args.sources else None
        crawl_all_sources(sources)
    elif args.query_date:
        items = query_by_date(args.query_date)
        print(json.dumps(items, ensure_ascii=False, indent=2))
    elif args.query_source:
        items = query_by_source(args.query_source)
        print(json.dumps(items, ensure_ascii=False, indent=2))
    elif args.query_keyword:
        items = query_by_keyword(args.query_keyword)
        print(json.dumps(items, ensure_ascii=False, indent=2))
    elif args.stats:
        stats = get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    elif args.report:
        generate_daily_report()
    elif args.cleanup:
        cleanup_old_data(args.cleanup)
    elif args.retry:
        # 从日志读取失败的源（简化版：重试所有源）
        crawl_all_sources()
    else:
        # 默认：采集所有
        crawl_all_sources()


if __name__ == '__main__':
    main()