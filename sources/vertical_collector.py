#!/usr/bin/env python3
"""
垂直领域数据采集器
教育、心理学、科技等专业领域热点

作者: AI Article Publisher
创建时间: 2026-02-23
"""

import json
import time
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional

API_BASE = "http://localhost:6688"

# 垂直领域数据源配置
VERTICAL_SOURCES = {
    # 科技编程
    "github": {"name": "GitHub Trending", "category": "编程", "type": "科技"},
    "hackernews": {"name": "Hacker News", "category": "科技", "type": "国际"},
    "hellogithub": {"name": "HelloGitHub", "category": "开源", "type": "科技"},
    "csdn": {"name": "CSDN", "category": "编程", "type": "科技"},
    "juejin": {"name": "掘金", "category": "编程", "type": "科技"},
    "51cto": {"name": "51CTO", "category": "IT技术", "type": "科技"},
    "nodeseek": {"name": "NodeSeek", "category": "Node.js", "type": "科技"},
    "linuxdo": {"name": "Linux.do", "category": "Linux", "type": "科技"},
    "hostloc": {"name": "HostLoc", "category": "运维", "type": "科技"},
    
    # 游戏
    "gameres": {"name": "游戏葡萄", "category": "游戏行业", "type": "游戏"},
    "yystv": {"name": "游研社", "category": "游戏资讯", "type": "游戏"},
    "lol": {"name": "英雄联盟", "category": "LOL", "type": "游戏"},
    
    # 二次元
    "miyoushe": {"name": "米游社", "category": "米哈游", "type": "二次元"},
    "starrail": {"name": "星穹铁道", "category": "星铁", "type": "二次元"},
    "genshin": {"name": "原神", "category": "原神", "type": "二次元"},
    "honkai": {"name": "崩坏", "category": "崩坏系列", "type": "二次元"},
    
    # 科学科普
    "guokr": {"name": "果壳", "category": "科普", "type": "科学"},
    
    # 阅读消费
    "weread": {"name": "微信读书", "category": "阅读", "type": "文化"},
    "smzdm": {"name": "什么值得买", "category": "消费", "type": "购物"},
    "douban-movie": {"name": "豆瓣电影", "category": "影视", "type": "娱乐"},
    "douban-group": {"name": "豆瓣小组", "category": "社区", "type": "综合"},
    
    # 历史
    "history": {"name": "历史上的今天", "category": "历史", "type": "知识"},
}


def fetch_vertical_source(source_id: str) -> Optional[List[Dict]]:
    """获取垂直领域数据"""
    url = f"{API_BASE}/{source_id}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return parse_items(data, source_id)
    except Exception as e:
        print(f"  ❌ {source_id}: {str(e)[:30]}")
        return None


def parse_items(data: Dict, source_id: str) -> List[Dict]:
    """解析数据"""
    items = []
    raw_items = data.get('data', [])
    
    config = VERTICAL_SOURCES.get(source_id, {})
    
    for item in raw_items:
        try:
            parsed = {
                "id": item.get('id', ''),
                "title": item.get('title', item.get('name', '')),
                "url": item.get('url', ''),
                "source_name": config.get('name', source_id),
                "category": config.get('category', '其他'),
                "source_type": config.get('type', '综合'),
                "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # 热度
            hot = item.get('hot', item.get('view', 0))
            if hot:
                parsed['hot'] = int(hot) if str(hot).isdigit() else 0
            
            # 描述
            desc = item.get('desc', item.get('description', ''))
            if desc:
                parsed['desc'] = str(desc)[:200]
            
            items.append(parsed)
        except Exception:
            continue
    
    return items


def collect_vertical_sources() -> Dict[str, Any]:
    """采集所有垂直领域数据"""
    print(f"\n{'='*60}")
    print(f"📚 垂直领域数据采集")
    print(f"{'='*60}")
    print(f"数据源: {len(VERTICAL_SOURCES)} 个")
    print(f"{'='*60}\n")
    
    results = {
        "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "sources": {},
        "items": [],
        "stats": {
            "total": 0,
            "by_category": {},
            "by_type": {}
        }
    }
    
    total = 0
    for source_id, config in VERTICAL_SOURCES.items():
        cat = config.get('category', '其他')[:4]
        print(f"[{cat}] {config['name']}...", end=" ")
        
        items = fetch_vertical_source(source_id)
        
        if items:
            results['sources'][source_id] = {
                "name": config['name'],
                "count": len(items),
                "category": config['category'],
                "type": config['type']
            }
            results['items'].extend(items)
            
            # 按分类统计
            category = config['category']
            results['stats']['by_category'][category] = results['stats']['by_category'].get(category, 0) + len(items)
            
            # 按类型统计
            stype = config['type']
            results['stats']['by_type'][stype] = results['stats']['by_type'].get(stype, 0) + len(items)
            
            total += len(items)
            print(f"✅ {len(items)} 条")
        else:
            print("❌ 无数据")
        
        time.sleep(0.2)
    
    results['stats']['total'] = total
    
    print(f"\n{'='*60}")
    print(f"📊 采集完成")
    print(f"总数据: {total} 条")
    print(f"分类: {len(results['stats']['by_category'])} 个")
    print(f"{'='*60}\n")
    
    return results


def save_vertical_data(data: Dict, output_dir: str = "data/vertical"):
    """保存垂直领域数据"""
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
    print("📚 垂直领域数据采集器")
    print("="*60)
    
    data = collect_vertical_sources()
    
    if data['items']:
        save_vertical_data(data)
        print(f"\n✅ 垂直领域采集完成! 共 {len(data['items'])} 条")
    else:
        print("\n⚠️  未采集到数据")


if __name__ == '__main__':
    main()