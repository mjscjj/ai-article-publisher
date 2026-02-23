#!/usr/bin/env python3
"""
扩展数据源系统
支持：直接RSS、自定义爬虫、API接口
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import List, Dict, Optional
from urllib.request import urlopen, Request
from urllib.parse import quote
import hashlib

# 配置
STORAGE_DIR = "/root/.openclaw/workspace-writer/ai-article-publisher/data/hotnews"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml,application/xml,text/xml,*/*"
}

# 扩展数据源 - 直接RSS
DIRECT_RSS_SOURCES = {
    # ===== 教育 =====
    "bbc_education": {
        "name": "BBC教育新闻",
        "platform": "BBC",
        "url": "https://feeds.bbci.co.uk/news/education/rss.xml",
        "category": "教育",
        "type": "rss"
    },
    "inside_higher_ed": {
        "name": "Inside Higher Ed",
        "platform": "IHE",
        "url": "https://www.insidehighered.com/rss.xml",
        "category": "教育",
        "type": "rss"
    },
    "education_next": {
        "name": "Education Next",
        "platform": "Education Next",
        "url": "https://www.educationnext.org/feed/",
        "category": "教育",
        "type": "rss"
    },
    "hechinger": {
        "name": "Hechinger Report",
        "platform": "Hechinger",
        "url": "https://hechingerreport.org/feed/",
        "category": "教育",
        "type": "rss"
    },
    "the_74": {
        "name": "The 74 Million",
        "platform": "The 74",
        "url": "https://www.the74million.org/feed/",
        "category": "教育",
        "type": "rss"
    },
    "stanford_edu": {
        "name": "斯坦福教育学院",
        "platform": "Stanford",
        "url": "https://ed.stanford.edu/rss.xml",
        "category": "教育",
        "type": "rss"
    },
    
    # ===== 心理学/神经科学 =====
    "science_daily_mind": {
        "name": "ScienceDaily心智",
        "platform": "ScienceDaily",
        "url": "https://www.sciencedaily.com/rss/mind_brain.xml",
        "category": "心理学",
        "type": "rss"
    },
    "child_dev_institute": {
        "name": "儿童发展研究所",
        "platform": "CDI",
        "url": "https://childdevelopmentinfo.com/feed/",
        "category": "心理学",
        "type": "rss"
    },
    "child_mind": {
        "name": "Child Mind Institute",
        "platform": "Child Mind",
        "url": "https://childmind.org/feed/",
        "category": "青少年心理",
        "type": "rss"
    },
    "positive_psych": {
        "name": "积极心理学",
        "platform": "PositivePsychology",
        "url": "https://positivepsychology.com/feed/",
        "category": "心理学",
        "type": "rss"
    },
    
    # ===== 个人成长 =====
    "tiny_buddha": {
        "name": "Tiny Buddha",
        "platform": "Tiny Buddha",
        "url": "https://tinybuddha.com/feed/",
        "category": "个人成长",
        "type": "rss"
    },
    "mark_manson": {
        "name": "Mark Manson",
        "platform": "Mark Manson",
        "url": "https://markmanson.net/feed",
        "category": "个人成长",
        "type": "rss"
    },
    "james_clear": {
        "name": "James Clear",
        "platform": "James Clear",
        "url": "https://jamesclear.com/feed",
        "category": "个人成长",
        "type": "rss"
    },
    
    # ===== 科技 =====
    "mit_tech": {
        "name": "MIT科技评论",
        "platform": "MIT",
        "url": "https://www.technologyreview.com/feed/",
        "category": "科技",
        "type": "rss"
    },
    "wired_science": {
        "name": "Wired科学",
        "platform": "Wired",
        "url": "https://www.wired.com/feed/science/rss",
        "category": "科技",
        "type": "rss"
    },
    "ifanr": {
        "name": "爱范儿",
        "platform": "爱范儿",
        "url": "https://www.ifanr.com/feed",
        "category": "科技",
        "type": "rss"
    },
    "techcrunch": {
        "name": "TechCrunch",
        "platform": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "category": "科技",
        "type": "rss"
    },
    
    # ===== 科学研究 =====
    "phys_org": {
        "name": "Phys.org科学",
        "platform": "Phys.org",
        "url": "https://phys.org/rss-feed/",
        "category": "科学研究",
        "type": "rss"
    }
}

# API 数据源
API_SOURCES = {
    # 可以后续添加API支持
}

def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)

def generate_id(title: str, source: str, timestamp: str) -> str:
    """生成唯一ID"""
    content = f"{title}_{source}_{timestamp}"
    return hashlib.md5(content.encode()).hexdigest()[:12]

def fetch_direct_rss(url: str, source_id: str, source_info: Dict) -> List[Dict]:
    """获取直接RSS源"""
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=30) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
        
        items = []
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        
        # 解析 RSS
        # 尝试多种匹配模式
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
        print(f"  [{source_id}] 获取失败: {str(e)[:50]}")
        return []

def test_all_sources() -> Dict[str, int]:
    """测试所有扩展数据源"""
    print("\n" + "=" * 60)
    print("测试扩展数据源")
    print("=" * 60 + "\n")
    
    results = {}
    working_sources = {}
    
    for source_id, source_info in DIRECT_RSS_SOURCES.items():
        print(f"[{source_info['name']}] 测试中...")
        items = fetch_direct_rss(source_info["url"], source_id, source_info)
        
        if items:
            print(f"[{source_info['name']}] ✅ 可用 - {len(items)} 条")
            results[source_id] = len(items)
            working_sources[source_id] = source_info
        else:
            print(f"[{source_info['name']}] ❌ 不可用")
            results[source_id] = 0
    
    print(f"\n{'='*60}")
    print(f"可用数据源: {len(working_sources)}/{len(DIRECT_RSS_SOURCES)}")
    print(f"{'='*60}\n")
    
    # 保存可用源列表
    config_file = os.path.join(STORAGE_DIR, "extended_sources.json")
    ensure_dir(STORAGE_DIR)
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump({
            "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "working_sources": working_sources,
            "total_working": len(working_sources)
        }, f, ensure_ascii=False, indent=2)
    
    return working_sources

def crawl_extended_sources(sources: List[str] = None) -> Dict[str, int]:
    """采集扩展数据源"""
    # 读取可用源
    config_file = os.path.join(STORAGE_DIR, "extended_sources.json")
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            working_sources = config.get("working_sources", {})
    else:
        working_sources = test_all_sources()
    
    if sources:
        working_sources = {k: v for k, v in working_sources.items() if k in sources}
    
    if not working_sources:
        print("无可用的扩展数据源，请先运行测试")
        return {}
    
    print(f"\n{'='*60}")
    print(f"采集扩展数据源 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    results = {}
    all_items = []
    
    for source_id, source_info in working_sources.items():
        print(f"[{source_info['name']}] 采集中...")
        items = fetch_direct_rss(source_info["url"], source_id, source_info)
        
        if items:
            all_items.extend(items)
            print(f"[{source_info['name']}] ✅ 获取 {len(items)} 条")
            results[source_id] = len(items)
        else:
            print(f"[{source_info['name']}] ❌ 获取失败")
            results[source_id] = 0
    
    print(f"\n{'='*60}")
    print(f"采集完成 - 共 {len(all_items)} 条")
    print(f"{'='*60}\n")
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='扩展数据源系统')
    parser.add_argument('--test', '-t', action='store_true', help='测试所有扩展数据源')
    parser.add_argument('--crawl', '-c', action='store_true', help='采集扩展数据源')
    parser.add_argument('--sources', '-s', default='', help='指定数据源（逗号分隔）')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有数据源')
    args = parser.parse_args()
    
    if args.test:
        test_all_sources()
    elif args.crawl:
        sources = args.sources.split(',') if args.sources else None
        crawl_extended_sources(sources)
    elif args.list:
        print("\n扩展数据源列表:")
        print("-" * 60)
        for sid, s in DIRECT_RSS_SOURCES.items():
            print(f"  {sid}: {s['name']} ({s['category']})")
        print("-" * 60)
        print(f"总计: {len(DIRECT_RSS_SOURCES)} 个")
    else:
        # 默认：测试
        test_all_sources()

if __name__ == '__main__':
    main()