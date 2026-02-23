#!/usr/bin/env python3
"""
选题深度分析器
为每个选题提供具体的写作分析，帮助用户判断是否值得写

作者: AI Article Publisher
创建时间: 2026-02-22
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# 配置
CONFIG = {
    "user_domains": ["教育", "心理学", "AI", "科技", "个人成长"],
    "min_hotness": 100,  # 最小热度阈值
}


def analyze_topic_deeply(topic: Dict, user_domains: List[str] = None) -> Dict:
    """
    深度分析单个选题
    
    返回:
    - 是否值得写
    - 为什么值得/不值得
    - 写作难度评估
    - 具体建议
    """
    user_domains = user_domains or CONFIG["user_domains"]
    
    title = topic.get("title", "")
    source = topic.get("source_name", topic.get("source", ""))
    category = topic.get("category", "")
    
    analysis = {
        "title": title,
        "source": source,
        "category": category,
        "worth_writing": False,
        "reasons": [],
        "concerns": [],
        "suggestions": [],
        "score": 0,
    }
    
    # 1. 检查是否与用户领域相关
    domain_match = False
    matched_domains = []
    
    domain_keywords = {
        "教育": ["教育", "学校", "学生", "老师", "教学", "学习", "课程", "大学", "高考", "考研"],
        "心理学": ["心理", "情绪", "压力", "焦虑", "认知", "大脑", "神经", "记忆", "思维", "行为"],
        "AI": ["AI", "人工智能", "机器学习", "GPT", "Claude", "LLM", "深度学习", "算法", "模型"],
        "科技": ["科技", "技术", "互联网", "软件", "硬件", "编程", "代码", "开发", "产品"],
        "个人成长": ["成长", "学习", "效率", "习惯", "时间", "目标", "成功", "失败", "改变"],
    }
    
    for domain, keywords in domain_keywords.items():
        if domain in user_domains:
            for kw in keywords:
                if kw.lower() in title.lower():
                    matched_domains.append(domain)
                    break
    
    if matched_domains:
        domain_match = True
        analysis["matched_domains"] = matched_domains
        analysis["reasons"].append(f"✅ 匹配你的领域: {', '.join(matched_domains)}")
        analysis["score"] += 20
    else:
        analysis["concerns"].append("❌ 与你的专业领域不太匹配")
    
    # 2. 检查选题类型
    topic_type = detect_topic_type(title)
    analysis["topic_type"] = topic_type
    
    if topic_type == "热点事件":
        analysis["reasons"].append("✅ 热点事件，有时效性")
        analysis["suggestions"].append("建议 24-48 小时内发布")
        analysis["score"] += 15
    elif topic_type == "知识科普":
        analysis["reasons"].append("✅ 知识科普类，长尾价值高")
        analysis["suggestions"].append("可以深度挖掘，不受时效限制")
        analysis["score"] += 25
    elif topic_type == "观点争议":
        analysis["reasons"].append("✅ 有争议性，容易引发讨论")
        analysis["score"] += 20
    elif topic_type == "娱乐八卦":
        analysis["concerns"].append("⚠️ 娱乐八卦类，竞争激烈")
        analysis["suggestions"].append("需要独特角度才能脱颖而出")
    elif topic_type == "纯新闻":
        analysis["concerns"].append("⚠️ 纯新闻类，缺乏深度")
        analysis["suggestions"].append("建议找角度做深度解读")
    
    # 3. 检查写作难度
    difficulty = assess_writing_difficulty(title, category)
    analysis["difficulty"] = difficulty
    
    if difficulty == "低":
        analysis["reasons"].append("✅ 写作难度低，容易上手")
        analysis["score"] += 10
    elif difficulty == "高":
        analysis["concerns"].append("⚠️ 写作难度高，需要专业知识")
        analysis["suggestions"].append("建议先做资料收集")
    
    # 4. 检查独特性机会
    uniqueness = check_uniqueness(title, category)
    analysis["uniqueness"] = uniqueness
    
    if uniqueness == "高":
        analysis["reasons"].append("✅ 独特性高，竞争少")
        analysis["score"] += 15
    elif uniqueness == "低":
        analysis["concerns"].append("⚠️ 同类选题多，竞争激烈")
        analysis["suggestions"].append("需要找差异化角度")
    
    # 5. 最终判断
    analysis["score"] = min(analysis["score"], 100)
    
    if analysis["score"] >= 60:
        analysis["worth_writing"] = True
        if analysis["score"] >= 80:
            analysis["recommendation"] = "强烈推荐"
        elif analysis["score"] >= 70:
            analysis["recommendation"] = "推荐"
        else:
            analysis["recommendation"] = "可以写"
    else:
        analysis["recommendation"] = "不太推荐"
    
    return analysis


def detect_topic_type(title: str) -> str:
    """检测选题类型"""
    
    # 热点事件
    hot_keywords = ["热搜", "热榜", "最新", "突发", "刚刚", "今天", "昨日"]
    for kw in hot_keywords:
        if kw in title:
            return "热点事件"
    
    # 知识科普
    science_keywords = ["研究", "发现", "科学", "原理", "机制", "如何", "为什么", "什么是"]
    for kw in science_keywords:
        if kw in title:
            return "知识科普"
    
    # 观点争议
    debate_keywords = ["争议", "质疑", "反对", "支持", "应该", "不该", "对错"]
    for kw in debate_keywords:
        if kw in title:
            return "观点争议"
    
    # 娱乐八卦
    entertainment_keywords = ["明星", "演员", "歌手", "电影", "电视剧", "综艺", "恋情", "分手"]
    for kw in entertainment_keywords:
        if kw in title:
            return "娱乐八卦"
    
    # 纯新闻
    news_keywords = ["宣布", "发布", "通报", "报道", "消息称"]
    for kw in news_keywords:
        if kw in title:
            return "纯新闻"
    
    return "其他"


def assess_writing_difficulty(title: str, category: str) -> str:
    """评估写作难度"""
    
    # 高难度关键词
    hard_keywords = ["研究", "实验", "数据", "分析", "技术细节", "算法", "原理"]
    hard_count = sum(1 for kw in hard_keywords if kw in title)
    
    # 低难度关键词
    easy_keywords = ["推荐", "分享", "体验", "感受", "故事", "观点", "方法"]
    easy_count = sum(1 for kw in easy_keywords if kw in title)
    
    if hard_count >= 2:
        return "高"
    elif easy_count >= 2:
        return "低"
    else:
        return "中"


def check_uniqueness(title: str, category: str) -> str:
    """检查独特性"""
    
    # 通用选题（竞争大）
    generic_patterns = [
        "如何", "怎么", "什么", "为什么",  # 太通用
        "盘点", "推荐", "合集",  # 内容农场常用
    ]
    
    # 专业选题（竞争小）
    professional_patterns = [
        "研究", "实验", "数据", "分析",  # 需要专业背景
        "对比", "评测", "深度",  # 需要投入时间
    ]
    
    generic_count = sum(1 for p in generic_patterns if p in title)
    professional_count = sum(1 for p in professional_patterns if p in title)
    
    if professional_count >= 2:
        return "高"
    elif generic_count >= 2:
        return "低"
    else:
        return "中"


def generate_analysis_report(analyses: List[Dict]) -> str:
    """生成分析报告"""
    
    lines = [
        "=" * 70,
        "选题深度分析报告",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"分析数量: {len(analyses)} 个选题",
        "=" * 70,
        "",
    ]
    
    # 分类统计
    worth_writing = [a for a in analyses if a["worth_writing"]]
    not_recommended = [a for a in analyses if not a["worth_writing"]]
    
    lines.append(f"📊 统计:")
    lines.append(f"  ✅ 值得写: {len(worth_writing)} 个")
    lines.append(f"  ❌ 不太推荐: {len(not_recommended)} 个")
    lines.append("")
    
    # 推荐选题
    if worth_writing:
        lines.append("=" * 70)
        lines.append("🔥 值得写的选题")
        lines.append("=" * 70)
        lines.append("")
        
        for i, a in enumerate(sorted(worth_writing, key=lambda x: x["score"], reverse=True), 1):
            lines.append(f"【{i}】{a['title']}")
            lines.append(f"    来源: {a['source']} | 分类: {a['category']}")
            lines.append(f"    评分: {a['score']} | {a['recommendation']}")
            lines.append(f"    类型: {a.get('topic_type', '未知')} | 难度: {a.get('difficulty', '未知')} | 独特性: {a.get('uniqueness', '未知')}")
            lines.append("")
            
            if a.get("reasons"):
                lines.append("    ✅ 优势:")
                for reason in a["reasons"]:
                    lines.append(f"       {reason}")
                lines.append("")
            
            if a.get("concerns"):
                lines.append("    ⚠️ 注意:")
                for concern in a["concerns"]:
                    lines.append(f"       {concern}")
                lines.append("")
            
            if a.get("suggestions"):
                lines.append("    💡 建议:")
                for suggestion in a["suggestions"]:
                    lines.append(f"       {suggestion}")
                lines.append("")
            
            lines.append("-" * 70)
            lines.append("")
    
    # 不推荐选题
    if not_recommended:
        lines.append("=" * 70)
        lines.append("❌ 不太推荐的选题 (仅供参考)")
        lines.append("=" * 70)
        lines.append("")
        
        for a in not_recommended[:5]:  # 只显示前5个
            lines.append(f"  • {a['title']}")
            lines.append(f"    原因: {a['concerns'][0] if a.get('concerns') else '综合评分较低'}")
            lines.append("")
    
    return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='选题深度分析器')
    parser.add_argument('--input', '-i', help='输入JSON文件路径')
    parser.add_argument('--top', '-n', type=int, default=20, help='分析数量')
    parser.add_argument('--domains', '-d', default='教育,心理学,AI,科技,个人成长', help='用户关注领域')
    args = parser.parse_args()
    
    user_domains = [d.strip() for d in args.domains.split(',')]
    
    # 加载数据
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        topics = list(data.values()) if isinstance(data, dict) else data
    else:
        print("请指定输入文件")
        return
    
    # 分析选题
    print(f"\n正在分析 {min(len(topics), args.top)} 个选题...")
    
    analyses = []
    for i, topic in enumerate(topics[:args.top]):
        analysis = analyze_topic_deeply(topic, user_domains)
        analyses.append(analysis)
    
    # 生成报告
    report = generate_analysis_report(analyses)
    print(report)


if __name__ == '__main__':
    main()
