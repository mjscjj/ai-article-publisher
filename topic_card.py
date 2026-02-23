#!/usr/bin/env python3
"""
选题卡片生成器
以卡片形式展示选题分析结果，一目了然

作者: AI Article Publisher
"""

import json
import sys
import time
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from topic_analyzer import analyze_topic

def generate_topic_cards(
    topics: list,
    user_profile: dict,
    top_n: int = 6,
) -> list:
    """生成选题卡片"""
    
    results = []
    
    for i, topic in enumerate(topics[:top_n * 2]):
        print(f"[{i+1}/{min(len(topics), top_n*2)}] 分析中...", end='\r')
        
        result = analyze_topic(topic, user_profile)
        
        if 'error' not in result:
            results.append({
                'topic': topic,
                'analysis': result
            })
        
        time.sleep(1)  # 避免频率限制
        
        if len(results) >= top_n:
            break
    
    # 按评分排序
    results.sort(key=lambda x: x['analysis'].get('overall_score', 0), reverse=True)
    
    return results


def print_card(item: dict, index: int):
    """打印单张卡片"""
    
    topic = item['topic']
    analysis = item['analysis']
    
    score = analysis.get('overall_score', 0)
    rec = analysis.get('recommendation', '')
    
    # 卡片顶部
    if score >= 85:
        border = '🔥'
        color = '强烈推荐'
    elif score >= 75:
        border = '✅'
        color = '推荐'
    else:
        border = '💡'
        color = '可以考虑'
    
    title = topic.get('title', '')[:68]
    
    print('┌' + '─' * 76 + '┐')
    print(f'│ {border} 【{index}】{title:<68} │')
    print('├' + '─' * 76 + '┤')
    
    # 来源和分类
    source = topic.get('source_name', topic.get('source', ''))
    category = topic.get('category', '')
    line = f'📰 {source} | 分类: {category}'
    print(f'│ {line:<74} │')
    print('├' + '─' * 76 + '┤')
    
    # 评分
    dims = analysis.get('dimensions', {})
    score_line = f'📊 综合评分: {score} | {color}'
    print(f'│ {score_line:<74} │')
    
    dim_line = (f'   新闻:{dims.get("news_value", 0):>2}/10  '
                f'匹配:{dims.get("user_match", 0):>2}/10  '
                f'竞争:{dims.get("competition", 0):>2}/10  '
                f'难度:{dims.get("difficulty", 0):>2}/10  '
                f'效果:{dims.get("expected_impact", 0):>2}/10')
    print(f'│ {dim_line:<74} │')
    print('├' + '─' * 76 + '┤')
    
    # 分析
    analysis_text = analysis.get('analysis', '')[:72]
    print(f'│ 💭 {analysis_text:<72} │')
    print('├' + '─' * 76 + '┤')
    
    # 写作角度
    angles = analysis.get('writing_angles', [])
    if angles:
        angle = angles[0]
        angle_text = angle.get('angle', '')[:66]
        print(f'│ ✍️  角度: {angle_text:<66} │')
        title_text = angle.get('title', '')[:70]
        print(f'│    📌 {title_text:<70} │')
    print('├' + '─' * 76 + '┤')
    
    # 风险
    risks = analysis.get('risks', [])
    if risks:
        risk_text = risks[0][:68]
        print(f'│ ⚠️  风险: {risk_text:<68} │')
    else:
        print('│ ⚠️  风险: 无明显风险' + ' ' * 56 + '│')
    
    print('└' + '─' * 76 + '┘')
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='选题卡片生成器')
    parser.add_argument('--input', '-i', help='输入JSON文件路径')
    parser.add_argument('--top', '-n', type=int, default=6, help='卡片数量')
    parser.add_argument('--domains', '-d', default='教育,心理学,AI', help='用户关注领域')
    args = parser.parse_args()
    
    # 检查 API Key
    if not os.environ.get('OPENROUTER_API_KEY'):
        print('❌ 请设置环境变量 OPENROUTER_API_KEY')
        return
    
    user_profile = {
        'domains': [d.strip() for d in args.domains.split(',')],
        'style': '深度分析',
        'audience': '职场人士',
    }
    
    # 加载数据
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        topics = list(data.values()) if isinstance(data, dict) else data
    else:
        print('请指定输入文件')
        return
    
    # 筛选有价值的选题
    valuable_topics = []
    for topic in topics:
        cat = topic.get('category', '')
        if cat in ['科技', '心理学', '教育', '个人成长', '科学研究']:
            title = topic.get('title', '')
            # 有价值的关键词
            interesting = ['AI', 'brain', 'exercise', 'Alzheimer', 'language', 
                          'energy', 'purpose', 'local', 'talent', 'boring', 
                          'Agent', 'learning', 'cognitive', 'stress', 'mental']
            if any(kw.lower() in title.lower() for kw in interesting):
                valuable_topics.append(topic)
    
    print()
    print('╔' + '═' * 76 + '╗')
    print('║' + '智能选题卡片'.center(74) + '║')
    print('║' + f'筛选后候选: {len(valuable_topics)} 个 | 生成卡片: {args.top} 张'.center(74) + '║')
    print('╚' + '═' * 76 + '╝')
    print()
    
    # 生成卡片
    results = generate_topic_cards(valuable_topics, user_profile, args.top)
    
    # 打印卡片
    for i, item in enumerate(results, 1):
        print_card(item, i)
    
    # 成本说明
    print('╔' + '═' * 76 + '╗')
    print('║' + '💰 成本说明: 所有分析使用免费模型 (step-3.5-flash-free) 总成本: $0'.center(74) + '║')
    print('╚' + '═' * 76 + '╝')


if __name__ == '__main__':
    main()
