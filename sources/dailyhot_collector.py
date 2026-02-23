#!/usr/bin/env python3
"""
DailyHotApi 数据采集器
基于 https://github.com/imsyy/DailyHotApi

API 文档: https://api-hot.imsyy.top/
支持平台: 40+ 个国内热门平台

作者: AI Article Publisher
创建时间: 2026-02-23
"""

import json
import time
import hashlib
import urllib.request
import urllib.error
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

# ============================================
# DailyHotApi 配置
# ============================================

# API 基础地址 (本地部署)
API_BASE = "http://localhost:6688"

# 支持的平台列表 (55 平台)
PLATFORMS = {
    # 视频平台
    "bilibili": {"name": "B站热门", "category": "视频", "platform": "B站"},
    "acfun": {"name": "AcFun", "category": "视频", "platform": "AcFun"},
    "douyin": {"name": "抖音热点", "category": "视频", "platform": "抖音"},
    "kuaishou": {"name": "快手热点", "category": "视频", "platform": "快手"},
    
    # 社交媒体
    "weibo": {"name": "微博热搜", "category": "综合", "platform": "微博"},
    "zhihu": {"name": "知乎热榜", "category": "综合", "platform": "知乎"},
    "zhihu-daily": {"name": "知乎日报", "category": "精选", "platform": "知乎"},
    "baidu": {"name": "百度热搜", "category": "综合", "platform": "百度"},
    "tieba": {"name": "百度贴吧", "category": "综合", "platform": "百度"},
    
    # 豆瓣
    "douban-movie": {"name": "豆瓣电影", "category": "娱乐", "platform": "豆瓣"},
    "douban-group": {"name": "豆瓣小组", "category": "综合", "platform": "豆瓣"},
    
    # 科技资讯
    "sspai": {"name": "少数派", "category": "科技", "platform": "少数派"},
    "ithome": {"name": "IT之家", "category": "科技", "platform": "IT之家"},
    "ithome-xijiayi": {"name": "IT之家喜加一", "category": "游戏", "platform": "IT之家"},
    "juejin": {"name": "掘金热榜", "category": "科技", "platform": "掘金"},
    "csdn": {"name": "CSDN", "category": "科技", "platform": "CSDN"},
    "51cto": {"name": "51CTO", "category": "科技", "platform": "51CTO"},
    "nodeseek": {"name": "NodeSeek", "category": "科技", "platform": "NodeSeek"},
    "coolapk": {"name": "酷安", "category": "科技", "platform": "酷安"},
    "geekpark": {"name": "极客公园", "category": "科技", "platform": "极客公园"},
    "ifanr": {"name": "爱范儿", "category": "科技", "platform": "爱范儿"},
    "dgtle": {"name": "数字尾巴", "category": "科技", "platform": "数字尾巴"},
    "linuxdo": {"name": "Linux.do", "category": "科技", "platform": "Linux.do"},
    
    # 财经
    "36kr": {"name": "36氪", "category": "财经", "platform": "36氪"},
    "huxiu": {"name": "虎嗅", "category": "财经", "platform": "虎嗅"},
    
    # 新闻
    "thepaper": {"name": "澎湃新闻", "category": "新闻", "platform": "澎湃"},
    "toutiao": {"name": "今日头条", "category": "新闻", "platform": "今日头条"},
    "qq-news": {"name": "腾讯新闻", "category": "新闻", "platform": "腾讯"},
    "sina": {"name": "新浪网", "category": "新闻", "platform": "新浪"},
    "sina-news": {"name": "新浪新闻", "category": "新闻", "platform": "新浪"},
    "netease-news": {"name": "网易新闻", "category": "新闻", "platform": "网易"},
    
    # 国际科技
    "hackernews": {"name": "Hacker News", "category": "国际", "platform": "HN"},
    "github": {"name": "GitHub", "category": "国际", "platform": "GitHub"},
    "producthunt": {"name": "ProductHunt", "category": "国际", "platform": "PH"},
    "nytimes": {"name": "纽约时报", "category": "国际", "platform": "NYT"},
    
    # 论坛社区
    "ngabbs": {"name": "NGA论坛", "category": "社区", "platform": "NGA"},
    "hostloc": {"name": "全球主机交流", "category": "技术", "platform": "HostLoc"},
    "v2ex": {"name": "V2EX", "category": "技术", "platform": "V2EX"},
    "newsmth": {"name": "水木社区", "category": "社区", "platform": "SMTH"},
    "hupu": {"name": "虎扑", "category": "体育", "platform": "虎扑"},
    "52pojie": {"name": "吾爱破解", "category": "技术", "platform": "吾爱"},
    
    # 游戏
    "gameres": {"name": "游戏葡萄", "category": "游戏", "platform": "游戏葡萄"},
    "yystv": {"name": "游研社", "category": "游戏", "platform": "游研社"},
    "lol": {"name": "英雄联盟", "category": "游戏", "platform": "LOL"},
    
    # 二次元
    "miyoushe": {"name": "米游社", "category": "二次元", "platform": "米游社"},
    "starrail": {"name": "星穹铁道", "category": "二次元", "platform": "星铁"},
    "genshin": {"name": "原神", "category": "二次元", "platform": "原神"},
    "honkai": {"name": "崩坏", "category": "二次元", "platform": "崩坏"},
    
    # 其他
    "jianshu": {"name": "简书", "category": "阅读", "platform": "简书"},
    "guokr": {"name": "果壳", "category": "科学", "platform": "果壳"},
    "smzdm": {"name": "什么值得买", "category": "消费", "platform": "值得买"},
    "weread": {"name": "微信读书", "category": "阅读", "platform": "微信读书"},
    "hellogithub": {"name": "HelloGitHub", "category": "开源", "platform": "GitHub"},
    "history": {"name": "历史上的今天", "category": "历史", "platform": "历史"},
}


def fetch_platform(platform_id: str) -> Optional[List[Dict]]:
    """从 DailyHotApi 获取平台数据"""
    url = f"{API_BASE}/{platform_id}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Referer': 'https://hot.imsyy.top/'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return parse_api_response(data, platform_id)
    except Exception as e:
        print(f"  ❌ 错误: {str(e)[:50]}")
        return None


def parse_api_response(data: Dict, platform_id: str) -> List[Dict]:
    """解析 DailyHotApi 响应"""
    items = []
    
    # DailyHotApi 格式: {code: 200, message: 'success', data: [...]}
    if isinstance(data, dict):
        raw_items = data.get('data', data.get('result', []))
    else:
        raw_items = data
    
    if not raw_items:
        return items
    
    for item in raw_items:
        try:
            # 提取标题
            title = item.get('title', item.get('name', ''))
            if not title:
                continue
            
            # 清理标题
            title = clean_text(title)
            
            parsed = {
                "id": generate_id(title + platform_id),
                "title": title,
                "url": item.get('url', item.get('link', '')),
                "source_id": platform_id,
                "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "crawl_date": datetime.now().strftime('%Y-%m-%d'),
            }
            
            # 提取热度
            hot = item.get('hot', item.get('hotScore', item.get('view', 0)))
            if hot:
                parsed['score'] = str(hot)
            
            # 提取描述
            desc = item.get('desc', item.get('description', item.get('summary', '')))
            if desc:
                parsed['description'] = clean_text(desc)[:200]
            
            # 提取封面
            cover = item.get('pic', item.get('cover', item.get('image', '')))
            if cover:
                parsed['cover'] = cover
            
            # 提取作者
            author = item.get('author', item.get('source', ''))
            if author:
                parsed['author'] = author
            
            items.append(parsed)
        except Exception:
            continue
    
    return items


def clean_text(text: str) -> str:
    """清理文本"""
    if not text:
        return ""
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', str(text))
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def generate_id(text: str) -> str:
    """生成唯一ID"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:12]


def collect_all_platforms() -> Dict[str, Any]:
    """采集所有平台数据"""
    results = {
        "stats": {
            "total_platforms": len(PLATFORMS),
            "success": 0,
            "failed": 0,
            "total_items": 0
        },
        "platforms": {},
        "items": [],
        "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "api_source": "DailyHotApi"
    }
    
    print(f"\n{'='*60}")
    print(f"🔥 DailyHotApi 数据采集")
    print(f"{'='*60}")
    print(f"平台数量: {len(PLATFORMS)} 个")
    print(f"API 地址: {API_BASE}")
    print(f"{'='*60}\n")
    
    total_items = 0
    success_count = 0
    
    for platform_id, platform_info in PLATFORMS.items():
        print(f"[{platform_info['category'][:2]}] {platform_info['name']}...", end=" ")
        
        items = fetch_platform(platform_id)
        
        if items and len(items) > 0:
            # 添加元数据
            for item in items:
                item['source_name'] = platform_info['name']
                item['category'] = platform_info['category']
                item['platform'] = platform_info['platform']
            
            results['platforms'][platform_id] = {
                "name": platform_info['name'],
                "count": len(items),
                "category": platform_info['category'],
                "platform": platform_info['platform']
            }
            results['items'].extend(items)
            
            total_items += len(items)
            success_count += 1
            print(f"✅ {len(items)} 条")
        else:
            print("❌ 无数据")
        
        time.sleep(0.3)  # 避免请求过快
    
    results['stats']['success'] = success_count
    results['stats']['failed'] = len(PLATFORMS) - success_count
    results['stats']['total_items'] = total_items
    
    print(f"\n{'='*60}")
    print(f"📊 采集完成")
    print(f"成功: {success_count}/{len(PLATFORMS)} 个平台")
    print(f"总数据: {total_items} 条热点")
    print(f"{'='*60}\n")
    
    return results


def save_results(results: Dict, output_dir: str = "data/hotnews"):
    """保存采集结果"""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/daily", exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 保存每日文件
    daily_file = f"{output_dir}/daily/{today}_dailyhot.json"
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"📁 每日文件: {daily_file}")
    
    # 更新索引
    index_file = f"{output_dir}/index.json"
    index = {}
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    
    if 'dailyhot' not in index:
        index['dailyhot'] = {}
    
    index['dailyhot'][today] = {
        "total_items": len(results['items']),
        "platforms": len(results['platforms']),
        "success_rate": f"{results['stats']['success']}/{results['stats']['total_platforms']}",
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
    print("🔥 DailyHotApi 数据采集器")
    print("="*60)
    
    results = collect_all_platforms()
    
    if results['items']:
        save_results(results)
        print(f"\n✅ 采集完成! 共 {len(results['items'])} 条热点")
    else:
        print("\n⚠️  未采集到数据")


if __name__ == '__main__':
    main()