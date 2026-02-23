#!/usr/bin/env python3
"""
智能选题评分系统
基于热点内容、用户偏好、竞品分析进行选题推荐
"""

import json
import sys
import argparse
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from urllib.request import urlopen, Request
from urllib.parse import quote

# 默认权重配置
DEFAULT_WEIGHTS = {
    "热度": 0.30,
    "时效": 0.20,
    "受众匹配": 0.25,
    "竞争": 0.15,
    "难度": 0.10
}

def calculate_hotness_score(item: Dict, max_score: int = 100) -> float:
    """计算热度分 (0-100)"""
    score_str = item.get("score", "")
    
    # 提取数字
    numbers = re.findall(r'\d+', str(score_str))
    if not numbers:
        return 50.0  # 默认中等热度
    
    num = int(numbers[0])
    
    # 归一化到 0-100
    # 微博/知乎热度通常几千到几百万
    if num >= 1000000:  # 100万+
        return 100.0
    elif num >= 100000:  # 10万+
        return 90.0
    elif num >= 10000:   # 1万+
        return 80.0
    elif num >= 1000:    # 1000+
        return 70.0
    elif num >= 100:     # 100+
        return 60.0
    else:
        return 50.0

def calculate_timeliness_score(publish_time: str, now: datetime = None) -> float:
    """计算时效分 (0-100)"""
    if not publish_time:
        return 50.0
    
    now = now or datetime.now()
    
    # 尝试解析时间
    try:
        # 常见格式
        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"]:
            try:
                pub_date = datetime.strptime(publish_time[:10], fmt[:10])
                break
            except:
                continue
        else:
            return 50.0
        
        days_diff = (now - pub_date).days
        
        if days_diff <= 0:  # 今天
            return 100.0
        elif days_diff == 1:  # 昨天
            return 90.0
        elif days_diff <= 3:  # 3天内
            return 80.0
        elif days_diff <= 7:  # 一周内
            return 70.0
        elif days_diff <= 30:  # 一月内
            return 50.0
        else:
            return 30.0
    except:
        return 50.0

def calculate_audience_match(title: str, keywords: List[str]) -> float:
    """计算受众匹配分 (0-100)"""
    if not keywords:
        return 50.0
    
    title_lower = title.lower()
    match_count = sum(1 for kw in keywords if kw.lower() in title_lower)
    
    if match_count >= 3:
        return 100.0
    elif match_count == 2:
        return 85.0
    elif match_count == 1:
        return 70.0
    else:
        return 40.0

def calculate_competition_score(title: str) -> float:
    """计算竞争分 (0-100)
    低竞争 = 高分，高竞争 = 低分
    """
    # 基于标题长度和关键词判断
    # 越通用的标题竞争越大
    
    # 通用词（竞争大）
    generic_words = ["如何", "什么", "为什么", "怎样", "方法", "技巧"]
    match_generic = sum(1 for w in generic_words if w in title)
    
    # 专业词（竞争小）
    professional_words = ["AI", "LLM", "心理学", "神经", "认知", "深度"]
    match_pro = sum(1 for w in professional_words if w in title)
    
    if match_pro >= 2:
        return 85.0  # 专业内容竞争小
    elif match_pro == 1:
        return 75.0
    elif match_generic >= 2:
        return 40.0  # 通用内容竞争大
    else:
        return 60.0

def calculate_difficulty_score(title: str, content: str = "") -> float:
    """计算写作难度分 (0-100)
    低难度 = 高分，高难度 = 低分
    """
    # 基于标题长度和关键词判断
    
    # 高难度关键词
    hard_keywords = ["研究", "实验", "数据", "分析", "原理", "机制"]
    match_hard = sum(1 for w in hard_keywords if w in title)
    
    # 低难度关键词
    easy_keywords = ["推荐", "分享", "体验", "感受", "故事", "观点"]
    match_easy = sum(1 for w in easy_keywords if w in title)
    
    if match_easy >= 2:
        return 85.0  # 易写
    elif match_easy == 1:
        return 75.0
    elif match_hard >= 2:
        return 40.0  # 难写
    else:
        return 60.0

def score_topic(
    item: Dict, 
    user_keywords: List[str] = None,
    weights: Dict[str, float] = None
) -> Dict:
    """对单个选题进行评分"""
    
    weights = weights or DEFAULT_WEIGHTS
    user_keywords = user_keywords or []
    
    title = item.get("title", "")
    
    scores = {
        "热度": calculate_hotness_score(item),
        "时效": calculate_timeliness_score(item.get("time", "")),
        "受众匹配": calculate_audience_match(title, user_keywords),
        "竞争": calculate_competition_score(title),
        "难度": calculate_difficulty_score(title)
    }
    
    # 加权总分
    total = sum(scores[k] * weights[k] for k in scores)
    
    return {
        "title": title,
        "url": item.get("url", ""),
        "source": item.get("source", ""),
        "scores": scores,
        "weights": weights,
        "total": round(total, 1),
        "recommendation": get_recommendation(total)
    }

def get_recommendation(score: float) -> str:
    """根据分数给出推荐"""
    if score >= 80:
        return "强烈推荐"
    elif score >= 70:
        return "推荐"
    elif score >= 60:
        return "可以考虑"
    elif score >= 50:
        return "一般"
    else:
        return "不推荐"

def rank_topics(
    items: List[Dict],
    user_keywords: List[str] = None,
    weights: Dict[str, float] = None,
    top_n: int = 10
) -> List[Dict]:
    """对选题列表进行排序"""
    
    scored = [score_topic(item, user_keywords, weights) for item in items]
    
    # 按总分降序排序
    ranked = sorted(scored, key=lambda x: x["total"], reverse=True)
    
    return ranked[:top_n]

def generate_topic_report(ranked: List[Dict], output_format: str = "text") -> str:
    """生成选题报告"""
    
    if output_format == "json":
        return json.dumps(ranked, ensure_ascii=False, indent=2)
    
    # 文本格式
    lines = [
        "=" * 60,
        "智能选题推荐报告",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        ""
    ]
    
    for i, topic in enumerate(ranked, 1):
        lines.append(f"【{i}】{topic['title']}")
        lines.append(f"    来源: {topic['source']}")
        lines.append(f"    总分: {topic['total']} ({topic['recommendation']})")
        lines.append(f"    热度: {topic['scores']['热度']:.0f} | 时效: {topic['scores']['时效']:.0f} | 匹配: {topic['scores']['受众匹配']:.0f}")
        lines.append(f"    URL: {topic['url'][:50]}...")
        lines.append("")
    
    lines.extend([
        "=" * 60,
        "评分说明:",
        "- 热度 (30%): 文章热榜排名、阅读量",
        "- 时效 (20%): 发布时间新鲜度",
        "- 匹配 (25%): 与用户关注领域的匹配度",
        "- 竞争 (15%): 竞争激烈程度 (低竞争=高分)",
        "- 难度 (10%): 写作难度 (低难度=高分)",
        "",
        "推荐等级:",
        "- 80+ : 强烈推荐",
        "- 70+ : 推荐",
        "- 60+ : 可以考虑",
        "- 50+ : 一般",
        "- <50 : 不推荐",
        "=" * 60
    ])
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='智能选题评分系统')
    parser.add_argument('--input', '-i', help='输入JSON文件路径')
    parser.add_argument('--keywords', '-k', default='', help='用户关注关键词（逗号分隔）')
    parser.add_argument('--output', '-o', default='text', choices=['text', 'json'], help='输出格式')
    parser.add_argument('--top', '-n', type=int, default=10, help='输出数量')
    args = parser.parse_args()
    
    # 解析关键词
    user_keywords = [k.strip() for k in args.keywords.split(',') if k.strip()]
    
    # 读取输入
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            items = json.load(f)
    else:
        # 示例数据
        items = [
            {
                "title": "AI 编程助手对比：Claude vs GPT-4",
                "source": "少数派",
                "url": "https://example.com/1",
                "score": "10万阅读",
                "time": "2026-02-21"
            },
            {
                "title": "如何提高学习效率？5个实用方法",
                "source": "知乎",
                "url": "https://example.com/2",
                "score": "5000赞同",
                "time": "2026-02-20"
            },
            {
                "title": "心理学研究：压力与认知的关系",
                "source": "豆瓣",
                "url": "https://example.com/3",
                "score": "100回复",
                "time": "2026-02-19"
            }
        ]
    
    # 评分排序
    ranked = rank_topics(items, user_keywords, top_n=args.top)
    
    # 输出报告
    report = generate_topic_report(ranked, args.output)
    print(report)

if __name__ == '__main__':
    main()
