#!/usr/bin/env python3
"""
测试所有采集器
"""

import sys
import json
sys.path.insert(0, '/root/.openclaw/workspace-writer/ai-article-publisher')

def test_baidu():
    print("\n=== 测试百度 Provider ===")
    from plugins.autonomous_researcher.providers.baidu_mcp import BaiduProvider
    provider = BaiduProvider()
    results = provider.search("AI 教育", max_results=5)
    print(f"结果数：{len(results)}")
    for r in results[:3]:
        print(f"  - {r.get('title', '')[:50]}")
    return results

def test_bilibili():
    print("\n=== 测试 B 站采集器 ===")
    from plugins.retrieval.bilibili_collector import sniff_bilibili_emotions
    result = sniff_bilibili_emotions("AI 教育", top_n=5)
    print(f"视频数：{len(result.get('videos', []))}")
    for v in result.get('videos', [])[:3]:
        print(f"  - {v.get('title', '')[:50]}")
    return result

def test_smzdm():
    print("\n=== 测试什么值得买采集器 ===")
    from plugins.retrieval.smzdm_collector import sniff_smzdm_opinions
    result = sniff_smzdm_opinions("AI 学习机", top_n=5)
    print(f"爆料数：{len(result.get('deals', []))}")
    for d in result.get('deals', [])[:3]:
        print(f"  - {d.get('title', '')[:50]}")
    return result

def test_domestic_sniffer():
    print("\n=== 测试 Domestic Sniffer V2 ===")
    from plugins.retrieval.domestic_sniffer import sniff_domestic_emotions
    result = sniff_domestic_emotions("AI 教育")
    print(f"微博评论：{len(result.get('weibo_comments', []))} 条")
    print(f"知乎辩论：{len(result.get('zhihu_debates', []))} 条")
    print(f"B 站视频：{len(result.get('bilibili_comments', []))} 条")
    print(f"什么值得买：{len(result.get('smzdm_opinions', []))} 条")
    print(f"百度新闻：{len(result.get('baidu_news', []))} 条")
    return result

if __name__ == "__main__":
    test_baidu()
    test_bilibili()
    test_smzdm()
    test_domestic_sniffer()
    print("\n✅ 测试完成")
