#!/usr/bin/env python3
"""
热词采集器
采集各平台热搜热词，生成热词云

作者: AI Article Publisher
创建时间: 2026-02-23
"""

import json
import time
import urllib.request
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any

# DailyHotApi 本地地址
API_BASE = "http://localhost:6688"


def fetch_hotwords(platform: str) -> List[str]:
    """获取平台热词"""
    url = f"{API_BASE}/{platform}"
    words = []
    
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            items = data.get('data', [])
            for item in items:
                title = item.get('title', item.get('name', ''))
                if title:
                    # 提取关键词
                    words.extend(extract_keywords(title))
    except Exception as e:
        print(f"  {platform}: 错误 - {str(e)[:30]}")
    
    return words


def extract_keywords(title: str) -> List[str]:
    """从标题提取关键词"""
    # 简单分词：按空格和标点分割
    import re
    # 移除标点
    title = re.sub(r'[，。！？、；：""''【】（）\s]+', ' ', title)
    # 分词
    words = title.split()
    # 过滤短词
    words = [w for w in words if len(w) >= 2]
    return words


def generate_wordcloud(words: List[str], top: int = 50) -> List[Dict]:
    """生成热词云"""
    counter = Counter(words)
    return [{"word": word, "count": count} 
            for word, count in counter.most_common(top)]


def collect_all_hotwords() -> Dict[str, Any]:
    """采集所有平台热词"""
    platforms = [
        "weibo",      # 微博热搜
        "zhihu",      # 知乎热榜
        "baidu",      # 百度热搜
        "douyin",     # 抖音热点
        "bilibili",   # B站热门
        "toutiao",    # 今日头条
        "tieba",      # 百度贴吧
    ]
    
    print(f"\n{'='*60}")
    print(f"🔥 热词采集")
    print(f"{'='*60}\n")
    
    all_words = []
    platform_words = {}
    
    for platform in platforms:
        print(f"采集 {platform}...", end=" ")
        words = fetch_hotwords(platform)
        if words:
            all_words.extend(words)
            platform_words[platform] = len(words)
            print(f"✅ {len(words)} 个词")
        else:
            print("❌ 无数据")
        time.sleep(0.3)
    
    # 生成热词云
    wordcloud = generate_wordcloud(all_words, top=100)
    
    result = {
        "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_words": len(all_words),
        "unique_words": len(set(all_words)),
        "platform_stats": platform_words,
        "wordcloud": wordcloud[:50],
        "all_words": all_words
    }
    
    print(f"\n{'='*60}")
    print(f"📊 热词统计")
    print(f"总词数: {result['total_words']}")
    print(f"独立词: {result['unique_words']}")
    print(f"{'='*60}\n")
    
    return result


def save_hotwords(data: Dict, output_dir: str = "data/hotwords"):
    """保存热词数据"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = f"{output_dir}/{today}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"📁 热词已保存: {output_file}")
    return output_file


def print_top_words(wordcloud: List[Dict], top: int = 20):
    """打印热门词汇"""
    print(f"\n🔥 TOP {top} 热词:")
    print("-" * 40)
    for i, item in enumerate(wordcloud[:top], 1):
        bar = "█" * min(item['count'], 20)
        print(f"{i:2}. {item['word']:<15} {item['count']:>3} {bar}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔥 热词采集器")
    print("="*60)
    
    # 采集热词
    data = collect_all_hotwords()
    
    # 打印热门词汇
    print_top_words(data['wordcloud'])
    
    # 保存
    save_hotwords(data)
    
    print("\n✅ 热词采集完成!")


if __name__ == '__main__':
    main()