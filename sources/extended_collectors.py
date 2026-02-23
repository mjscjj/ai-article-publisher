#!/usr/bin/env python3
"""
扩展数据源采集器
包含: RSSHub 扩展、DailyHotApi、热词、视频热门等

作者: AI Article Publisher
创建时间: 2026-02-22
"""

import json
import time
import hashlib
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Dict, Any, Optional

# ============================================
# RSSHub 扩展数据源
# ============================================

RSSHUB_BASE = "http://localhost:1200"

RSSHUB_EXTENDED_SOURCES = {
    # 视频平台
    "bilibili_hot": {
        "name": "B站热门",
        "route": "/bilibili/ranking/0/0/0/0/0",
        "category": "视频",
        "platform": "B站"
    },
    "bilibili_anime": {
        "name": "B站动画热门",
        "route": "/bilibili/ranking/1/0/0/0/0",
        "category": "视频",
        "platform": "B站"
    },
    "bilibili_music": {
        "name": "B站音乐热门",
        "route": "/bilibili/ranking/3/0/0/0/0",
        "category": "视频",
        "platform": "B站"
    },
    "bilibili_game": {
        "name": "B站游戏热门",
        "route": "/bilibili/ranking/4/0/0/0/0",
        "category": "视频",
        "platform": "B站"
    },
    "bilibili_tech": {
        "name": "B站科技热门",
        "route": "/bilibili/ranking/188/0/0/0/0",
        "category": "科技",
        "platform": "B站"
    },
    "douyin_hot": {
        "name": "抖音热点",
        "route": "/douyin/hot",
        "category": "视频",
        "platform": "抖音"
    },
    "kuaishou_hot": {
        "name": "快手热门",
        "route": "/kuaishou/hot",
        "category": "视频",
        "platform": "快手"
    },
    "youtube_trending": {
        "name": "YouTube热门",
        "route": "/youtube/trending",
        "category": "视频",
        "platform": "YouTube"
    },
    
    # 图文平台
    "xiaohongshu_hot": {
        "name": "小红书热门",
        "route": "/xiaohongshu/hot",
        "category": "图文",
        "platform": "小红书"
    },
    
    # 国际热点
    "twitter_trends": {
        "name": "Twitter热点",
        "route": "/twitter/trends",
        "category": "国际",
        "platform": "Twitter"
    },
    "reddit_hot": {
        "name": "Reddit热门",
        "route": "/reddit/hot",
        "category": "国际",
        "platform": "Reddit"
    },
    "producthunt_today": {
        "name": "ProductHunt今日",
        "route": "/producthunt/today",
        "category": "科技",
        "platform": "ProductHunt"
    },
    "instagram_popular": {
        "name": "Instagram热门",
        "route": "/instagram/popular",
        "category": "图文",
        "platform": "Instagram"
    },
    
    # 更多中文热点
    "toutiao_hot": {
        "name": "今日头条热点",
        "route": "/toutiao/hot",
        "category": "综合",
        "platform": "今日头条"
    },
    "baidu_tieba_hot": {
        "name": "百度贴吧热议",
        "route": "/tieba/hot",
        "category": "综合",
        "platform": "百度"
    },
    "douban_movie_hot": {
        "name": "豆瓣电影热门",
        "route": "/douban/movie/playing",
        "category": "娱乐",
        "platform": "豆瓣"
    },
    "douban_book_hot": {
        "name": "豆瓣新书",
        "route": "/douban/book/latest",
        "category": "阅读",
        "platform": "豆瓣"
    },
    "douban_group_hot": {
        "name": "豆瓣小组热门",
        "route": "/douban/group/hot",
        "category": "综合",
        "platform": "豆瓣"
    },
    
    # 科技资讯
    "techcrunch": {
        "name": "TechCrunch",
        "route": "/techcrunch",
        "category": "科技",
        "platform": "TechCrunch"
    },
    "theverge": {
        "name": "The Verge",
        "route": "/theverge",
        "category": "科技",
        "platform": "The Verge"
    },
    "wired": {
        "name": "Wired",
        "route": "/wired",
        "category": "科技",
        "platform": "Wired"
    },
    
    # 财经
    "wallstreet_cn": {
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
}

# ============================================
# DailyHotApi 数据源
# ============================================

DAILYHOT_BASE = "https://api.v3.iowiki.cn/api"

DAILYHOT_SOURCES = {
    "weibo": {
        "name": "微博热搜",
        "endpoint": "/weibo",
        "category": "综合",
        "platform": "微博"
    },
    "zhihu": {
        "name": "知乎热榜",
        "endpoint": "/zhihu",
        "category": "综合",
        "platform": "知乎"
    },
    "douyin": {
        "name": "抖音热点",
        "endpoint": "/douyin",
        "category": "视频",
        "platform": "抖音"
    },
    "bilibili": {
        "name": "B站热门",
        "endpoint": "/bilibili",
        "category": "视频",
        "platform": "B站"
    },
    "toutiao": {
        "name": "今日头条",
        "endpoint": "/toutiao",
        "category": "综合",
        "platform": "今日头条"
    },
    "baidu": {
        "name": "百度热搜",
        "endpoint": "/baidu",
        "category": "综合",
        "platform": "百度"
    },
    "zhihu_daily": {
        "name": "知乎日报",
        "endpoint": "/zhihu-daily",
        "category": "精选",
        "platform": "知乎"
    },
    "weixin": {
        "name": "微信热门",
        "endpoint": "/weixin",
        "category": "综合",
        "platform": "微信"
    },
    "baidu_tieba": {
        "name": "百度贴吧",
        "endpoint": "/baidu-tieba",
        "category": "综合",
        "platform": "百度"
    },
    "netease_news": {
        "name": "网易新闻",
        "endpoint": "/netease-news",
        "category": "新闻",
        "platform": "网易"
    },
    "tencent_news": {
        "name": "腾讯新闻",
        "endpoint": "/tencent-news",
        "category": "新闻",
        "platform": "腾讯"
    },
}


def fetch_rsshub(route: str) -> Optional[List[Dict]]:
    """从 RSSHub 获取数据"""
    url = f"{RSSHUB_BASE}{route}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return parse_rsshub_items(data, route)
    except Exception as e:
        print(f"RSSHub 请求失败: {route} - {e}")
        return None


def parse_rsshub_items(data: Dict, route: str) -> List[Dict]:
    """解析 RSSHub 返回的数据"""
    items = []
    
    # RSSHub 返回格式可能是 {item: [...]} 或直接 [...]
    if isinstance(data, dict):
        raw_items = data.get('item', data.get('items', []))
    else:
        raw_items = data
    
    for item in raw_items:
        try:
            parsed = {
                "id": generate_id(item.get('link', item.get('title', ''))),
                "title": item.get('title', ''),
                "url": item.get('link', item.get('url', '')),
                "source": route,
                "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "crawl_date": datetime.now().strftime('%Y-%m-%d'),
            }
            
            # 提取描述
            if 'description' in item:
                parsed['description'] = item['description'][:200]
            elif 'summary' in item:
                parsed['description'] = item['summary'][:200]
            elif 'content' in item:
                parsed['description'] = item['content'][:200]
            
            items.append(parsed)
        except Exception as e:
            print(f"解析 RSSHub 项目失败: {e}")
            continue
    
    return items


def fetch_dailyhot(endpoint: str) -> Optional[List[Dict]]:
    """从 DailyHotApi 获取数据"""
    url = f"{DAILYHOT_BASE}{endpoint}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return parse_dailyhot_items(data, endpoint)
    except Exception as e:
        print(f"DailyHotApi 请求失败: {endpoint} - {e}")
        return None


def parse_dailyhot_items(data: Dict, endpoint: str) -> List[Dict]:
    """解析 DailyHotApi 返回的数据"""
    items = []
    
    # DailyHotApi 返回格式: {code: 200, message: '', data: [...]}
    if isinstance(data, dict):
        raw_items = data.get('data', data.get('result', []))
    else:
        raw_items = data
    
    for item in raw_items:
        try:
            parsed = {
                "id": generate_id(item.get('url', item.get('title', ''))),
                "title": item.get('title', item.get('name', '')),
                "url": item.get('url', item.get('link', '')),
                "source": endpoint,
                "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "crawl_date": datetime.now().strftime('%Y-%m-%d'),
            }
            
            # 提取热度
            if 'hot' in item:
                parsed['score'] = str(item['hot'])
            elif 'hotScore' in item:
                parsed['score'] = str(item['hotScore'])
            
            # 提取描述
            if 'desc' in item:
                parsed['description'] = item['desc'][:200]
            elif 'description' in item:
                parsed['description'] = item['description'][:200]
            
            items.append(parsed)
        except Exception as e:
            print(f"解析 DailyHot 项目失败: {e}")
            continue
    
    return items


def generate_id(text: str) -> str:
    """生成唯一ID"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:12]


def collect_all_sources() -> Dict[str, List[Dict]]:
    """采集所有数据源"""
    results = {}
    
    print(f"\n{'='*60}")
    print(f"扩展数据源采集")
    print(f"{'='*60}")
    print(f"RSSHub 扩展源: {len(RSSHUB_EXTENDED_SOURCES)} 个")
    print(f"DailyHotApi 源: {len(DAILYHOT_SOURCES)} 个")
    print(f"{'='*60}\n")
    
    # 采集 RSSHub 扩展源
    rsshub_count = 0
    for source_id, source_info in RSSHUB_EXTENDED_SOURCES.items():
        print(f"[RSSHub] {source_info['name']}...", end=" ")
        items = fetch_rsshub(source_info['route'])
        if items:
            results[source_id] = items
            rsshub_count += len(items)
            print(f"✅ {len(items)} 条")
        else:
            print("❌ 失败")
        time.sleep(0.5)  # 避免请求过快
    
    # 采集 DailyHotApi 源
    dailyhot_count = 0
    for source_id, source_info in DAILYHOT_SOURCES.items():
        print(f"[DailyHot] {source_info['name']}...", end=" ")
        items = fetch_dailyhot(source_info['endpoint'])
        if items:
            results[source_id] = items
            dailyhot_count += len(items)
            print(f"✅ {len(items)} 条")
        else:
            print("❌ 失败")
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"采集完成!")
    print(f"RSSHub: {rsshub_count} 条")
    print(f"DailyHot: {dailyhot_count} 条")
    print(f"总计: {rsshub_count + dailyhot_count} 条")
    print(f"{'='*60}\n")
    
    return results


def main():
    """主函数"""
    results = collect_all_sources()
    
    # 保存结果
    output_file = f"data/extended_sources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存: {output_file}")


if __name__ == '__main__':
    main()