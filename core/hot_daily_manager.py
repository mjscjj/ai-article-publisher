#!/usr/bin/env python3
"""
【热点数据按天管理】Hot News Daily Manager
按天查询、统计、清理热点数据

使用示例:
    python3 core/hot_daily_manager.py today
    python3 core/hot_daily_manager.py 2026-03-01
    python3 core/hot_daily_manager.py --stats
    python3 core/hot_daily_manager.py --cleanup 30
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hot_database_mysql import HotNewsDatabaseMySQL

def print_header(title: str):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def show_daily_topics(db: HotNewsDatabaseMySQL, date_str: str):
    """显示指定日期的热点"""
    print_header(f"📅 {date_str} 的热点数据")
    
    topics = db.get_hot_topics(crawl_date=date_str, limit=50)
    
    if not topics:
        print("  暂无数据")
        return
    
    print(f"共 {len(topics)} 条热点:\n")
    
    for i, topic in enumerate(topics[:20], 1):
        heat_icon = {
            'explosive': '🔥',
            'hot': '🔥',
            'warm': '🌡️',
            'normal': '📊'
        }.get(topic['heat_level'], '📊')
        
        print(f"{i:2d}. {heat_icon} [{topic['category'] or '综合'}] {topic['title'][:50]}")
        print(f"     来源：{topic['source_name']} | 热度：{float(topic['heat_score']):.1f}")
        
        if topic.get('tags'):
            tags = topic['tags'] if isinstance(topic['tags'], list) else []
            if tags:
                print(f"     标签：{', '.join(tags[:5])}")
        print()
    
    if len(topics) > 20:
        print(f"... 还有 {len(topics) - 20} 条")

def show_stats(db: HotNewsDatabaseMySQL):
    """显示统计数据"""
    print_header("📊 热点数据统计")
    
    # 日期范围
    date_range = db.get_date_range()
    print("日期范围:")
    print(f"  最早日期：{date_range.get('earliest_date', 'N/A')}")
    print(f"  最晚日期：{date_range.get('latest_date', 'N/A')}")
    print(f"  总天数：{date_range.get('date_count', 0)} 天")
    
    # 总体统计
    stats = db.get_statistics(days=30)
    print(f"\n近 30 天统计:")
    print(f"  总热点数：{stats['overall']['total_count']}")
    print(f"  平均热度：{float(stats['overall']['avg_heat']):.1f}")
    print(f"  最高热度：{float(stats['overall']['max_heat']):.1f}")
    print(f"  唯一热点：{stats['overall']['unique_count']}")
    
    # 按分类统计
    print(f"\n按分类统计:")
    for cat in stats['by_category'][:10]:
        print(f"  {cat['category'] or '未分类':10} : {cat['count']:4}条 (平均热度{float(cat['avg_heat']):.1f})")
    
    # 按来源统计
    print(f"\n按来源统计 (TOP10):")
    for src in stats['by_source'][:10]:
        print(f"  {src['name']:20} : {src['count']:4}条")
    
    # 热词统计
    print(f"\n热词 TOP20:")
    for i, kw in enumerate(stats['hot_keywords'][:20], 1):
        print(f"  {i:2d}. {kw['keyword']:15} ({kw['count']}次)")

def show_available_dates(db: HotNewsDatabaseMySQL, limit: int = 30):
    """显示可用日期列表"""
    print_header("📅 可用日期列表")
    
    dates = db.get_available_dates(limit=limit)
    
    if not dates:
        print("  暂无数据")
        return
    
    # 按日期显示热点数量
    from collections import Counter
    date_counts = Counter()
    
    for date_str in dates:
        topics = db.get_hot_topics(crawl_date=date_str, limit=1)
        if topics:
            # 获取该日期的统计
            date_topics = db.get_hot_topics(crawl_date=date_str, limit=1000)
            date_counts[date_str] = len(date_topics)
    
    print(f"{'日期':<12} {'热点数':>8}  {'可视化':<30}")
    print("-" * 50)
    
    for date_str in sorted(date_counts.keys(), reverse=True)[:limit]:
        count = date_counts[date_str]
        bar = "█" * min(20, count // 2)
        print(f"{date_str:<12} {count:>8}  {bar}")

def cleanup_old_data(db: HotNewsDatabaseMySQL, days: int):
    """清理旧数据"""
    print_header(f"🧹 清理{days}天前的数据")
    
    cutoff_date = datetime.now().date() - timedelta(days=days)
    print(f"清理截止日期：{cutoff_date}")
    
    confirm = input(f"\n确认删除 {cutoff_date} 之前的所有数据？(y/N): ")
    if confirm.lower() != 'y':
        print("已取消")
        return
    
    deleted = db.cleanup_old_data(days_to_keep=days)
    print(f"\n✅ 删除了 {deleted} 条旧热点")

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 core/hot_daily_manager.py <日期>       # 查询指定日期 (today/yesterday/2026-03-01)")
        print("  python3 core/hot_daily_manager.py --stats      # 显示统计")
        print("  python3 core/hot_daily_manager.py --dates      # 显示可用日期")
        print("  python3 core/hot_daily_manager.py --cleanup 30 # 清理 30 天前数据")
        print("\n示例:")
        print("  python3 core/hot_daily_manager.py today")
        print("  python3 core/hot_daily_manager.py 2026-03-01")
        sys.exit(1)
    
    # 初始化数据库
    try:
        db = HotNewsDatabaseMySQL()
    except Exception as e:
        print(f"❌ 数据库连接失败：{e}")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    try:
        if arg == '--stats':
            show_stats(db)
        elif arg == '--dates':
            show_available_dates(db)
        elif arg == '--cleanup':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            cleanup_old_data(db, days)
        else:
            # 查询指定日期
            show_daily_topics(db, arg)
    finally:
        db.close()
    
    print()

if __name__ == "__main__":
    main()
