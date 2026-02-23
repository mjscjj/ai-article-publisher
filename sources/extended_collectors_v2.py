#!/usr/bin/env python3
"""
扩展数据源采集器 v2
修复 RSSHub JSON 格式问题，添加更多数据源

作者: AI Article Publisher
创建时间: 2026-02-22
更新时间: 2026-02-23
"""

import json
import time
import hashlib
import urllib.request
import urllib.error
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# ============================================
# RSSHub 数据源 (JSON 格式)
# ============================================

RSSHUB_BASE = "http://localhost:1200"

RSSHUB_SOURCES = {
    # 中文热榜
    "zhihu_hot": {
        "name": "知乎热榜",
        "route": "/zhihu/hot",
        "category": "综合",
        "platform": "知乎"
    },
    "weibo_suggest": {
        "name": "微博热议",
        "route": "/weibo/suggest/hot",
        "category": "综合",
        "platform": "微博"
    },
    "baidu_tieba": {
        "name": "百度贴吧热议",
        "route": "/tieba/hot",
        "category": "综合",
        "platform": "百度"
    },
    "douban_group": {
        "name": "豆瓣小组",
        "route": "/douban/group/explore",
        "category": "综合",
        "platform": "豆瓣"
    },
    "toutiao": {
        "name": "今日头条",
        "route": "/toutiao/hot",
        "category": "综合",
        "platform": "今日头条"
    },
    
    # 科技资讯
    "hackernews_best": {
        "name": "Hacker News",
        "route": "/hackernews/best",
        "category": "科技",
        "platform": "Hacker News"
    },
    "hackernews_top": {
        "name": "HN Top",
        "route": "/hackernews/top",
        "category": "科技",
        "platform": "Hacker News"
    },
    "github_trending": {
        "name": "GitHub Trending",
        "route": "/github/trending/daily",
        "category": "科技",
        "platform": "GitHub"
    },
    "github_trending_python": {
        "name": "GitHub Python",
        "route": "/github/trending/daily/https://github.com/trending/python",
        "category": "科技",
        "platform": "GitHub"
    },
    "v2ex_hot": {
        "name": "V2EX",
        "route": "/v2ex/topics/hot",
        "category": "科技",
        "platform": "V2EX"
    },
    "juejin_hot": {
        "name": "掘金热榜",
        "route": "/juejin/posts/hot",
        "category": "科技",
        "platform": "掘金"
    },
    "ithome_ranking": {
        "name": "IT之家热榜",
        "route": "/ithome/ranking/7days",
        "category": "科技",
        "platform": "IT之家"
    },
    "sspai_index": {
        "name": "少数派",
        "route": "/sspai/index",
        "category": "科技",
        "platform": "少数派"
    },
    "infoq": {
        "name": "InfoQ",
        "route": "/infoq/recommend",
        "category": "科技",
        "platform": "InfoQ"
    },
    
    # 财经
    "36kr_news": {
        "name": "36氪快讯",
        "route": "/36kr/newsflashes",
        "category": "财经",
        "platform": "36氪"
    },
    "wallstreetcn": {
        "name": "华尔街见闻",
        "route": "/wallstreetcn/news/global",
        "category": "财经",
        "platform": "华尔街见闻"
    },
    "caixin": {
        "name": "财新网",
        "route": "/caixin/weekly",
        "category": "财经",
        "platform": "财新"
    },
    
    # 娱乐
    "douban_movie": {
        "name": "豆瓣电影",
        "route": "/douban/movie/playing",
        "category": "娱乐",
        "platform": "豆瓣"
    },
    
    # 国际
    "producthunt": {
        "name": "ProductHunt",
        "route": "/producthunt/today",
        "category": "科技",
        "platform": "ProductHunt"
    },
    "reddit_popular": {
        "name": "Reddit Popular",
        "route": "/reddit/popular",
        "category": "国际",
        "platform": "Reddit"
    },
    "reddit_programming": {
        "name": "Reddit Programming",
        "route": "/reddit/programming",
        "category": "科技",
        "platform": "Reddit"
    },
    
    # 设计
    "behance": {
        "name": "Behance",
        "route": "/behance/collections",
        "category": "设计",
        "platform": "Behance"
    },
    "dribbble": {
        "name": "Dribbble",
        "route": "/dribbble/popular",
        "category": "设计",
        "platform": "Dribbble"
    },
    
    # 学术
    "nature": {
        "name": "Nature",
        "route": "/nature/news",
        "category": "学术",
        "platform": "Nature"
    },
    "science": {
        "name": "Science",
        "route": "/science/news",
        "category": "学术",
        "platform": "Science"
    },
}


def fetch_rsshub_json(route: str) -> Optional[List[Dict]]:
    """从 RSSHub 获取数据 (支持 RSS 和 JSON 格式)"""
    # 先尝试 JSON 格式
    url = f"{RSSHUB_BASE}{route}?format=json"
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return parse_rsshub_items(data, route)
    except Exception as e:
        # JSON 失败，尝试 RSS 格式
        try:
            rss_url = f"{RSSHUB_BASE}{route}"
            req = urllib.request.Request(
                rss_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/rss+xml'
                }
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                xml_content = response.read().decode('utf-8')
                return parse_rsshub_rss(xml_content, route)
        except Exception as e2:
            print(f"  ❌ RSSHub 错误: {route} - {str(e2)[:50]}")
            return None


def parse_rsshub_rss(xml_content: str, route: str) -> List[Dict]:
    """解析 RSSHub 返回的 RSS XML 数据"""
    import xml.etree.ElementTree as ET
    
    items = []
    try:
        root = ET.fromstring(xml_content)
        raw_items = root.findall('.//item')
        
        for item in raw_items:
            try:
                title_elem = item.find('title')
                link_elem = item.find('link')
                
                if title_elem is None:
                    continue
                    
                title = title_elem.text or ''
                
                parsed = {
                    "id": generate_id(title + route),
                    "title": title,
                    "url": link_elem.text if link_elem is not None else '',
                    "source_route": route,
                    "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "crawl_date": datetime.now().strftime('%Y-%m-%d'),
                }
                
                # 提取描述
                desc_elem = item.find('description')
                if desc_elem is not None and desc_elem.text:
                    import re
                    desc = re.sub(r'<[^>]+>', '', desc_elem.text)
                    parsed['description'] = desc[:200]
                
                items.append(parsed)
            except Exception:
                continue
    except Exception as e:
        print(f"  RSS 解析错误: {str(e)[:30]}")
    
    return items


def parse_rsshub_items(data: Dict, route: str) -> List[Dict]:
    """解析 RSSHub 返回的 JSON 数据"""
    items = []
    
    # RSSHub JSON 格式: {item: [...]}
    raw_items = data.get('item', data.get('items', []))
    
    if not raw_items:
        return items
    
    for item in raw_items:
        try:
            title = item.get('title', '')
            if not title:
                continue
                
            parsed = {
                "id": generate_id(title + route),
                "title": title,
                "url": item.get('link', item.get('url', '')),
                "source_route": route,
                "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "crawl_date": datetime.now().strftime('%Y-%m-%d'),
            }
            
            # 提取描述
            desc = item.get('description', item.get('summary', item.get('content', '')))
            if desc:
                # 清理 HTML 标签
                import re
                desc = re.sub(r'<[^>]+>', '', str(desc))
                parsed['description'] = desc[:200]
            
            items.append(parsed)
        except Exception:
            continue
    
    return items


def generate_id(text: str) -> str:
    """生成唯一ID"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:12]


def collect_all_sources() -> Dict[str, Any]:
    """采集所有数据源"""
    results = {
        "stats": {
            "total": 0,
            "success": 0,
            "failed": 0,
        },
        "sources": {},
        "items": [],
        "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"\n{'='*60}")
    print(f"📡 扩展数据源采集")
    print(f"{'='*60}")
    print(f"RSSHub 数据源: {len(RSSHUB_SOURCES)} 个")
    print(f"{'='*60}\n")
    
    total_items = 0
    success_count = 0
    
    for source_id, source_info in RSSHUB_SOURCES.items():
        print(f"[{source_info['category'][:2]}] {source_info['name']}...", end=" ")
        
        items = fetch_rsshub_json(source_info['route'])
        
        if items and len(items) > 0:
            # 添加元数据
            for item in items:
                item['source_name'] = source_info['name']
                item['category'] = source_info['category']
                item['platform'] = source_info['platform']
            
            results['sources'][source_id] = {
                "name": source_info['name'],
                "count": len(items),
                "category": source_info['category'],
                "platform": source_info['platform']
            }
            results['items'].extend(items)
            
            total_items += len(items)
            success_count += 1
            print(f"✅ {len(items)} 条")
        else:
            print("❌ 无数据")
        
        time.sleep(0.3)  # 避免请求过快
    
    results['stats']['total'] = len(RSSHUB_SOURCES)
    results['stats']['success'] = success_count
    results['stats']['failed'] = len(RSSHUB_SOURCES) - success_count
    
    print(f"\n{'='*60}")
    print(f"📊 采集完成")
    print(f"成功: {success_count}/{len(RSSHUB_SOURCES)} 个源")
    print(f"总数据: {total_items} 条")
    print(f"{'='*60}\n")
    
    return results


def save_results(results: Dict, output_dir: str = "data/hotnews"):
    """保存采集结果"""
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/daily", exist_ok=True)
    os.makedirs(f"{output_dir}/by_source", exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 保存到每日文件
    daily_file = f"{output_dir}/daily/{today}_extended.json"
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"📁 每日文件: {daily_file}")
    
    # 更新索引
    index_file = f"{output_dir}/index.json"
    index = {}
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    
    # 更新统计
    if 'extended' not in index:
        index['extended'] = {}
    
    index['extended'][today] = {
        "total_items": len(results['items']),
        "sources": len(results['sources']),
        "crawl_time": results['crawl_time']
    }
    index['last_update'] = results['crawl_time']
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"📁 索引文件: {index_file}")
    
    return daily_file


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 扩展数据源采集器 v2")
    print("="*60)
    
    # 采集数据
    results = collect_all_sources()
    
    # 保存结果
    if results['items']:
        save_results(results)
        print(f"\n✅ 采集完成! 共 {len(results['items'])} 条热点")
    else:
        print("\n⚠️  未采集到数据")


if __name__ == '__main__':
    main()