#!/usr/bin/env python3
"""
AI Article Publisher - 完整工作流
整合热点采集 → 智能选题 → 内容创作（复用 wechat-article-skill）
"""

import json
import sys
import argparse
import subprocess
from datetime import datetime
from typing import List, Dict

# 导入选题评分模块
sys.path.insert(0, '/root/.openclaw/workspace-writer/ai-article-publisher')
from topic_scorer import rank_topics, generate_topic_report

# 数据源脚本路径
FETCH_NEWS_SCRIPT = "/root/.openclaw/workspace/skills/wemp-operator/scripts/content/fetch_news.py"
RSSHUB_BASE = "http://localhost:1200"

def collect_hot_news(sources: List[str], limit: int = 10) -> List[Dict]:
    """采集热点新闻"""
    print(f"[采集] 从 {len(sources)} 个数据源采集热点...")
    
    all_items = []
    
    for source in sources:
        try:
            cmd = ["python3", FETCH_NEWS_SCRIPT, "--source", source, "--limit", str(limit)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                items = json.loads(result.stdout)
                all_items.extend(items)
                print(f"  [{source}] 获取 {len(items)} 条")
            else:
                print(f"  [{source}] 失败: {result.stderr[:50]}")
        except Exception as e:
            print(f"  [{source}] 错误: {str(e)[:50]}")
    
    print(f"[采集] 共获取 {len(all_items)} 条热点")
    return all_items

def select_best_topics(items: List[Dict], keywords: List[str], top_n: int = 5) -> List[Dict]:
    """智能选题"""
    print(f"\n[选题] 评分并筛选前 {top_n} 个选题...")
    
    ranked = rank_topics(items, keywords, top_n=top_n)
    
    print(f"\n推荐选题:")
    for i, topic in enumerate(ranked, 1):
        print(f"  {i}. {topic['title'][:40]}... ({topic['total']}分 - {topic['recommendation']})")
    
    return ranked

def generate_article_prompt(topic: Dict, style: str = "技术干货") -> str:
    """生成文章创作提示（用于 wechat-article-skill）"""
    
    prompt = f"""请根据以下选题创作一篇公众号文章：

选题：{topic['title']}
来源：{topic['source']}
原文链接：{topic['url']}

写作风格：{style}
要求：
1. 标题：吸引眼球，20字以内
2. 摘要：概括要点，100字以内
3. 正文：1500-2500字，结构清晰
4. 结构：开场引入 → 3-5个核心观点 → 总结与行动建议

请开始创作。"""
    
    return prompt

def create_workflow_report(
    topics: List[Dict],
    keywords: List[str],
    sources: List[str]
) -> str:
    """生成工作流报告"""
    
    lines = [
        "╔" + "═" * 58 + "╗",
        "║" + " AI Article Publisher - 工作流报告".center(56) + "║",
        "║" + f" {datetime.now().strftime('%Y-%m-%d %H:%M')}".center(56) + "║",
        "╠" + "═" * 58 + "╣",
        "║ 配置信息" + " " * 48 + "║",
        "╟" + "─" * 58 + "╢",
        f"║ 关注领域: {', '.join(keywords) if keywords else '未指定'}".ljust(59) + "║",
        f"║ 数据源: {', '.join(sources)}".ljust(59) + "║",
        "╠" + "═" * 58 + "╣",
        "║ 推荐选题".center(56) + "║",
        "╟" + "─" * 58 + "╢",
    ]
    
    for i, topic in enumerate(topics, 1):
        title = topic['title'][:35] + "..." if len(topic['title']) > 35 else topic['title']
        lines.append(f"║ {i}. {title}".ljust(59) + "║")
        lines.append(f"║    来源: {topic['source']} | 分数: {topic['total']} | {topic['recommendation']}".ljust(59) + "║")
        lines.append("║" + " " * 58 + "║")
    
    lines.extend([
        "╠" + "═" * 58 + "╣",
        "║ 下一步操作".center(56) + "║",
        "╟" + "─" * 58 + "╢",
        "║ 1. 选择一个选题进行创作".ljust(59) + "║",
        "║ 2. 运行: openclaw agent --message '创作文章...'" .ljust(59) + "║",
        "║ 3. 使用 wechat-article-skill 生成并发布".ljust(59) + "║",
        "╚" + "═" * 58 + "╝",
    ])
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='AI Article Publisher 工作流')
    parser.add_argument('--sources', '-s', default='weibo,zhihu,hackernews,github',
                       help='数据源（逗号分隔）')
    parser.add_argument('--keywords', '-k', default='', 
                       help='关注关键词（逗号分隔）')
    parser.add_argument('--top', '-n', type=int, default=5, help='选题数量')
    parser.add_argument('--output', '-o', default='report', 
                       choices=['report', 'json', 'prompt'],
                       help='输出格式')
    args = parser.parse_args()
    
    # 解析参数
    sources = [s.strip() for s in args.sources.split(',')]
    keywords = [k.strip() for k in args.keywords.split(',') if k.strip()]
    
    print("=" * 60)
    print("AI Article Publisher - 完整工作流")
    print("=" * 60)
    
    # 1. 采集热点
    items = collect_hot_news(sources, limit=10)
    
    if not items:
        print("\n[错误] 未采集到任何内容")
        return
    
    # 2. 智能选题
    topics = select_best_topics(items, keywords, args.top)
    
    # 3. 输出结果
    if args.output == 'json':
        print(json.dumps(topics, ensure_ascii=False, indent=2))
    elif args.output == 'prompt':
        # 输出第一个选题的创作提示
        if topics:
            print(generate_article_prompt(topics[0]))
    else:
        # 输出完整报告
        print("\n" + create_workflow_report(topics, keywords, sources))
    
    # 保存结果
    output_file = f"/root/.openclaw/workspace-writer/ai-article-publisher/output/topics_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)
    print(f"\n[保存] 结果已保存到: {output_file}")

if __name__ == '__main__':
    main()
