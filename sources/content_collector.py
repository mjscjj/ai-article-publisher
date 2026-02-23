#!/usr/bin/env python3
"""
图文内容采集器
采集热门图文内容：豆瓣、简书、知乎专栏等

作者: AI Article Publisher
创建时间: 2026-02-23
"""

import json
import time
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional

API_BASE = "http://localhost:6688"

# 图文平台配置
IMAGE_TEXT_PLATFORMS = {
    "douban-group": {
        "name": "豆瓣小组",
        "category": "社区讨论",
        "type": "图文"
    },
    "douban-movie": {
        "name": "豆瓣电影",
        "category": "影视评论",
        "type": "图文"
    },
    "zhihu": {
        "name": "知乎热榜",
        "category": "问答讨论",
        "type": "图文"
    },
    "zhihu-daily": {
        "name": "知乎日报",
        "category": "精选内容",
        "type": "图文"
    },
    "jianshu": {
        "name": "简书",
        "category": "文章创作",
        "type": "图文"
    },
    "guokr": {
        "name": "果壳",
        "category": "科学科普",
        "type": "图文"
    },
    "sspai": {
        "name": "少数派",
        "category": "科技数码",
        "type": "图文"
    }
}


def fetch_platform_content(platform: str) -> Optional[List[Dict]]:
    """获取平台图文内容"""
    url = f"{API_BASE}/{platform}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))
            return parse_content_items(data, platform)
    except Exception as e:
        print(f"  ❌ {platform}: {str(e)[:30]}")
        return None


def parse_content_items(data: Dict, platform: str) -> List[Dict]:
    """解析图文内容"""
    items = []
    raw_items = data.get('data', [])
    
    config = IMAGE_TEXT_PLATFORMS.get(platform, {})
    
    for item in raw_items:
        try:
            content = {
                "id": item.get('id', ''),
                "title": item.get('title', item.get('name', '')),
                "url": item.get('url', ''),
                "platform": config.get('name', platform),
                "category": config.get('category', '图文'),
                "content_type": config.get('type', '图文'),
                "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # 作者
            author = item.get('author', item.get('source', ''))
            content['author'] = author if isinstance(author, str) else str(author)
            
            # 热度/互动
            hot = item.get('hot', item.get('view', item.get('like', 0)))
            if hot:
                content['hot'] = int(hot) if str(hot).isdigit() else 0
            
            # 描述/摘要
            desc = item.get('desc', item.get('description', item.get('summary', '')))
            if desc:
                content['summary'] = desc[:200]
            
            # 封面图
            cover = item.get('pic', item.get('cover', item.get('image', '')))
            if cover:
                content['cover'] = cover
            
            items.append(content)
        except Exception:
            continue
    
    return items


def collect_all_content() -> Dict[str, Any]:
    """采集所有图文平台"""
    print(f"\n{'='*60}")
    print(f"📝 图文内容采集")
    print(f"{'='*60}\n")
    
    results = {
        "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "platforms": {},
        "contents": [],
        "stats": {
            "total": 0,
            "by_platform": {},
            "by_category": {}
        }
    }
    
    total = 0
    for platform_id, config in IMAGE_TEXT_PLATFORMS.items():
        print(f"[{config['category']}] {config['name']}...", end=" ")
        
        items = fetch_platform_content(platform_id)
        
        if items:
            results['platforms'][platform_id] = {
                "name": config['name'],
                "count": len(items),
                "category": config['category']
            }
            results['contents'].extend(items)
            results['stats']['by_platform'][config['name']] = len(items)
            
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
    print(f"总内容: {total} 条")
    for cat, count in results['stats']['by_category'].items():
        print(f"  {cat}: {count} 条")
    print(f"{'='*60}\n")
    
    return results


def save_content_data(data: Dict, output_dir: str = "data/contents"):
    """保存图文数据"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = f"{output_dir}/{today}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"📁 数据已保存: {output_file}")
    return output_file


def main():
    """主函数"""
    print("\n" + "="*60)
    print("📝 图文内容采集器")
    print("="*60)
    
    data = collect_all_content()
    
    if data['contents']:
        save_content_data(data)
        print(f"\n✅ 图文采集完成! 共 {len(data['contents'])} 条")
    else:
        print("\n⚠️  未采集到数据")


if __name__ == '__main__':
    main()