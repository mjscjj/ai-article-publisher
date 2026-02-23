#!/usr/bin/env python3
"""
统一数据采集入口
整合 RSSHub + DailyHotApi 所有数据源

作者: AI Article Publisher
创建时间: 2026-02-23
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入采集器
try:
    from dailyhot_collector import collect_all_platforms as collect_dailyhot
    from dailyhot_collector import PLATFORMS as DAILYHOT_PLATFORMS
    DAILYHOT_AVAILABLE = True
except ImportError:
    DAILYHOT_AVAILABLE = False
    print("⚠️  DailyHotApi 采集器不可用")

try:
    from extended_collectors_v2 import collect_all_sources as collect_rsshub
    from extended_collectors_v2 import RSSHUB_SOURCES
    RSSHUB_AVAILABLE = True
except ImportError:
    RSSHUB_AVAILABLE = False
    print("⚠️  RSSHub 采集器不可用")


def merge_results(dailyhot_data: Dict, rsshub_data: Dict) -> Dict:
    """合并两个采集器的结果"""
    merged = {
        "stats": {
            "total_items": 0,
            "platforms": 0,
            "dailyhot_items": 0,
            "rsshub_items": 0,
        },
        "platforms": {},
        "items": [],
        "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    # 合并 DailyHotApi 数据
    if dailyhot_data and dailyhot_data.get('items'):
        merged['items'].extend(dailyhot_data['items'])
        merged['stats']['dailyhot_items'] = len(dailyhot_data['items'])
        for pid, pinfo in dailyhot_data.get('platforms', {}).items():
            merged['platforms'][f"dailyhot_{pid}"] = pinfo
    
    # 合并 RSSHub 数据
    if rsshub_data and rsshub_data.get('items'):
        merged['items'].extend(rsshub_data['items'])
        merged['stats']['rsshub_items'] = len(rsshub_data['items'])
        for sid, sinfo in rsshub_data.get('sources', {}).items():
            merged['platforms'][f"rsshub_{sid}"] = sinfo
    
    merged['stats']['total_items'] = len(merged['items'])
    merged['stats']['platforms'] = len(merged['platforms'])
    
    return merged


def deduplicate_items(items: List[Dict]) -> List[Dict]:
    """基于标题去重"""
    seen = set()
    unique = []
    for item in items:
        title = item.get('title', '')
        if title and title not in seen:
            seen.add(title)
            unique.append(item)
    return unique


def save_unified_data(data: Dict, output_dir: str = "data/hotnews"):
    """保存统一数据"""
    os.makedirs(f"{output_dir}/daily", exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 保存每日合并数据
    daily_file = f"{output_dir}/daily/{today}_unified.json"
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📁 每日文件: {daily_file}")
    
    # 更新索引
    index_file = f"{output_dir}/index.json"
    index = {}
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    
    # 更新统计
    index['unified'] = {
        today: {
            "total_items": data['stats']['total_items'],
            "platforms": data['stats']['platforms'],
            "dailyhot_items": data['stats']['dailyhot_items'],
            "rsshub_items": data['stats']['rsshub_items'],
            "crawl_time": data['crawl_time']
        }
    }
    index['last_update'] = data['crawl_time']
    index['total_items'] = index.get('total_items', 0) + data['stats']['total_items']
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"📁 索引文件: {index_file}")
    
    return daily_file


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 统一数据采集器")
    print("="*60)
    print(f"DailyHotApi: {'✅ 可用' if DAILYHOT_AVAILABLE else '❌ 不可用'}")
    print(f"RSSHub: {'✅ 可用' if RSSHUB_AVAILABLE else '❌ 不可用'}")
    print("="*60 + "\n")
    
    dailyhot_data = {}
    rsshub_data = {}
    
    # 采集 DailyHotApi
    if DAILYHOT_AVAILABLE:
        print("\n📡 采集 DailyHotApi 数据源...")
        print(f"平台数量: {len(DAILYHOT_PLATFORMS)}")
        dailyhot_data = collect_dailyhot()
    
    # 采集 RSSHub
    if RSSHUB_AVAILABLE:
        print("\n📡 采集 RSSHub 数据源...")
        print(f"数据源数量: {len(RSSHUB_SOURCES)}")
        rsshub_data = collect_rsshub()
    
    # 合并数据
    print("\n📊 合并数据...")
    merged = merge_results(dailyhot_data, rsshub_data)
    
    # 去重
    print(f"去重前: {len(merged['items'])} 条")
    merged['items'] = deduplicate_items(merged['items'])
    merged['stats']['total_items'] = len(merged['items'])
    print(f"去重后: {len(merged['items'])} 条")
    
    # 保存
    if merged['items']:
        save_unified_data(merged)
        print(f"\n✅ 采集完成!")
        print(f"总数据: {merged['stats']['total_items']} 条")
        print(f"平台数: {merged['stats']['platforms']} 个")
    else:
        print("\n⚠️  未采集到数据")


if __name__ == '__main__':
    main()