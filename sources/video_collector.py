#!/usr/bin/env python3
"""
视频热门内容采集器
采集 B站、抖音、快手等平台热门视频详情

作者: AI Article Publisher
创建时间: 2026-02-23
"""

import json
import time
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional

API_BASE = "http://localhost:6688"

# 视频平台配置
VIDEO_PLATFORMS = {
    "bilibili": {
        "name": "B站",
        "category": "长视频",
        "fields": ["title", "url", "author", "view", "danmaku", "like"]
    },
    "douyin": {
        "name": "抖音", 
        "category": "短视频",
        "fields": ["title", "url", "author", "hot"]
    },
    "kuaishou": {
        "name": "快手",
        "category": "短视频", 
        "fields": ["title", "url", "author", "hot"]
    },
    "acfun": {
        "name": "AcFun",
        "category": "长视频",
        "fields": ["title", "url", "author"]
    }
}


def fetch_video_hot(platform: str) -> Optional[List[Dict]]:
    """获取平台热门视频"""
    url = f"{API_BASE}/{platform}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))
            return parse_video_items(data, platform)
    except Exception as e:
        print(f"  ❌ {platform}: {str(e)[:30]}")
        return None


def parse_video_items(data: Dict, platform: str) -> List[Dict]:
    """解析视频数据"""
    items = []
    raw_items = data.get('data', [])
    
    config = VIDEO_PLATFORMS.get(platform, {})
    
    for item in raw_items:
        try:
            video = {
                "id": item.get('id', ''),
                "title": item.get('title', item.get('name', '')),
                "url": item.get('url', ''),
                "platform": config.get('name', platform),
                "category": config.get('category', '视频'),
                "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # 作者
            author = item.get('author', item.get('owner', {}))
            if isinstance(author, dict):
                author = author.get('name', author.get('nick', ''))
            video['author'] = author
            
            # 播放量/热度
            hot = item.get('hot', item.get('view', item.get('play', 0)))
            if hot:
                video['hot'] = int(hot) if str(hot).isdigit() else 0
            
            # 其他数据
            if 'like' in item:
                video['like'] = item['like']
            if 'danmaku' in item:
                video['danmaku'] = item['danmaku']
            if 'cover' in item:
                video['cover'] = item['cover']
            if 'desc' in item:
                video['desc'] = item['desc'][:200]
            
            items.append(video)
        except Exception:
            continue
    
    return items


def collect_all_videos() -> Dict[str, Any]:
    """采集所有视频平台"""
    print(f"\n{'='*60}")
    print(f"🎬 视频热门采集")
    print(f"{'='*60}\n")
    
    results = {
        "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "platforms": {},
        "videos": [],
        "stats": {
            "total": 0,
            "by_platform": {},
            "by_category": {}
        }
    }
    
    total = 0
    for platform_id, config in VIDEO_PLATFORMS.items():
        print(f"[{config['category']}] {config['name']}...", end=" ")
        
        items = fetch_video_hot(platform_id)
        
        if items:
            results['platforms'][platform_id] = {
                "name": config['name'],
                "count": len(items),
                "category": config['category']
            }
            results['videos'].extend(items)
            results['stats']['by_platform'][config['name']] = len(items)
            
            # 按分类统计
            cat = config['category']
            results['stats']['by_category'][cat] = results['stats']['by_category'].get(cat, 0) + len(items)
            
            total += len(items)
            print(f"✅ {len(items)} 条")
        else:
            print("❌ 无数据")
        
        time.sleep(0.3)
    
    results['stats']['total'] = total
    
    print(f"\n{'='*60}")
    print(f"📊 采集完成")
    print(f"总视频: {total} 条")
    for cat, count in results['stats']['by_category'].items():
        print(f"  {cat}: {count} 条")
    print(f"{'='*60}\n")
    
    return results


def analyze_hot_videos(videos: List[Dict], top: int = 20) -> List[Dict]:
    """分析热门视频排行"""
    # 按热度排序
    sorted_videos = sorted(
        videos, 
        key=lambda x: x.get('hot', 0), 
        reverse=True
    )
    return sorted_videos[:top]


def save_video_data(data: Dict, output_dir: str = "data/videos"):
    """保存视频数据"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = f"{output_dir}/{today}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"📁 数据已保存: {output_file}")
    return output_file


def print_top_videos(videos: List[Dict], top: int = 10):
    """打印热门视频榜"""
    hot_videos = analyze_hot_videos(videos, top)
    
    print(f"\n🔥 TOP {top} 热门视频:")
    print("-" * 60)
    for i, v in enumerate(hot_videos, 1):
        hot = v.get('hot', 0)
        hot_str = f"{hot//10000}万" if hot >= 10000 else str(hot)
        print(f"{i:2}. [{v['platform']}] {v['title'][:30]:<30} 🔥{hot_str}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🎬 视频热门内容采集器")
    print("="*60)
    
    # 采集视频数据
    data = collect_all_videos()
    
    if data['videos']:
        # 打印热门视频
        print_top_videos(data['videos'])
        
        # 保存数据
        save_video_data(data)
        
        print(f"\n✅ 视频采集完成! 共 {len(data['videos'])} 条")
    else:
        print("\n⚠️  未采集到视频数据")


if __name__ == '__main__':
    main()