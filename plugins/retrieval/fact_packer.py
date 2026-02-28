#!/usr/bin/env python3
"""
【资料洗练打包机】Fact Packer
调度内外双轨雷达，将得到的所有“硬数据”和“软情绪”融合入一个高质量、零废话的上下文包 (Fact-Pack)，供写作大模型吃透。
"""

import json
from domestic_sniffer import sniff_domestic_emotions
from global_searcher import fetch_global_facts

def build_fact_pack(topic_title: str) -> dict:
    """组合内外情报库为大模型食粮"""
    print("="*60)
    print(f"📦 Fact-Pack 处理器启动: 为《{topic_title}》打包全网素材")
    print("="*60)
    
    global_facts = fetch_global_facts(topic_title)
    domestic_emotions = sniff_domestic_emotions(topic_title)
    
    fact_pack = {
        "metadata": {
            "topic": topic_title,
            "status": "ready"
        },
        "hard_facts_global": global_facts,
        "soft_emotions_domestic": domestic_emotions
    }
    
    print(f"✅ Fact-Pack 生成完毕! (共融合外网资讯 {len(global_facts)} 条，国内双端情绪数据池)")
    return fact_pack

if __name__ == "__main__":
    import sys
    kw = sys.argv[1] if len(sys.argv) > 1 else "大模型算力内卷"
    res = build_fact_pack(kw)
    # 不打印太长的详细信息了
    print("Test build complete.")
