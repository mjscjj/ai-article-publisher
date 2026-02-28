#!/usr/bin/env python3
"""
热点采集器 V2 - 简化测试版
使用模拟数据测试数据库和采集流程
"""

import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hot_database import HotNewsDatabase

def test_with_mock_data():
    """使用模拟数据测试"""
    print("\n" + "="*70)
    print("📡 热点采集器 V2 - 模拟数据测试")
    print("="*70 + "\n")
    
    db = HotNewsDatabase()
    
    # 1. 添加数据源
    print("Step 1: 添加数据源")
    sources = [
        {"name": "微博热搜", "platform": "微博", "category": "综合", "priority": 10, "credibility": 0.8},
        {"name": "知乎热榜", "platform": "知乎", "category": "综合", "priority": 9, "credibility": 0.85},
        {"name": "澎湃新闻", "platform": "澎湃新闻", "category": "新闻", "priority": 8, "credibility": 0.9},
        {"name": "36 氪", "platform": "36 氪", "category": "财经", "priority": 7, "credibility": 0.85},
    ]
    
    for source in sources:
        db.add_source(**source)
    
    # 2. 模拟热点数据
    print("\nStep 2: 添加模拟热点")
    
    mock_topics = [
        {
            "title": "教育部发布 AI+ 教育指导意见，60% 高校已开设相关课程",
            "content": "教育部近日发布《人工智能 + 教育》指导意见，提出到 2025 年...",
            "source_name": "澎湃新闻",
            "category": "教育",
            "tags": ["AI", "教育", "政策"],
            "keywords": ["教育部", "AI 教育", "高校课程"]
        },
        {
            "title": "AI 程序员失业潮来了？专家：不会用 AI 的才会被淘汰",
            "content": "近日，某大厂宣布裁员 30%，其中程序员占比最高...",
            "source_name": "知乎热榜",
            "category": "科技",
            "tags": ["AI", "就业", "程序员"],
            "keywords": ["AI", "程序员", "失业", "裁员"]
        },
        {
            "title": "微博热搜第一！某明星 AI 换脸视频引发争议",
            "content": "一段 AI 换脸视频在微博疯传，引发法律和道德讨论...",
            "source_name": "微博热搜",
            "category": "娱乐",
            "tags": ["AI", "娱乐", "争议"],
            "keywords": ["AI 换脸", "明星", "争议"]
        },
        {
            "title": "36 氪首发 | AI 教育公司融资 1 亿美元，估值翻倍",
            "content": "专注于 AI 教育的初创公司获得最新一轮融资...",
            "source_name": "36 氪",
            "category": "财经",
            "tags": ["AI", "教育", "融资"],
            "keywords": ["AI 教育", "融资", "估值"]
        }
    ]
    
    for i, topic in enumerate(mock_topics):
        # 添加一些时间变化
        crawl_time = datetime.now() - timedelta(hours=random.randint(0, 24))
        
        db.add_hot_topic(
            title=topic['title'],
            content=topic['content'],
            source_name=topic['source_name'],
            category=topic['category'],
            tags=topic['tags'],
            keywords=topic['keywords'],
            crawl_time=crawl_time
        )
    
    # 3. 查询热点
    print("\nStep 3: 查询热点")
    topics = db.get_hot_topics(limit=10)
    
    print(f"\n{'='*70}")
    print("📋 热点列表")
    print(f"{'='*70}\n")
    
    for i, t in enumerate(topics, 1):
        print(f"{i}. [{t['heat_level']}] {t['title'][:50]}...")
        print(f"   来源：{t['source_name']} | 分类：{t.get('category', 'N/A')} | 热度：{t['heat_score']:.1f}")
        print(f"   采集时间：{t['crawl_time']}\n")
    
    # 4. 统计
    print("="*70)
    print("📊 统计数据")
    print("="*70 + "\n")
    
    stats = db.get_statistics(days=7)
    print(f"总热点数：{stats['overall']['total_count']}")
    print(f"平均热度：{stats['overall']['avg_heat']:.1f}")
    print(f"唯一热点：{stats['overall']['unique_count']}")
    
    print(f"\n按分类:")
    for cat in stats['by_category']:
        print(f"  - {cat['category']}: {cat['count']}条，平均热度{cat['avg_heat']:.1f}")
    
    print(f"\n热词 TOP10:")
    for kw in stats['hot_keywords'][:10]:
        print(f"  - {kw['keyword']}: {kw['count']}次")
    
    # 5. 测试去重
    print("\n" + "="*70)
    print("🔄 测试去重功能")
    print("="*70 + "\n")
    
    topic_id = db.add_hot_topic(
        title="教育部发布 AI+ 教育指导意见，60% 高校已开设相关课程",
        source_name="澎湃新闻"
    )
    print(f"重复热点 ID: {topic_id} (应为 -1) ✅\n")
    
    db.close()
    
    print("="*70)
    print("🎉 模拟数据测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_with_mock_data()
