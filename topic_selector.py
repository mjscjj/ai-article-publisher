#!/usr/bin/env python3
"""
智能选题选择器
统一入口，整合基础评分 + 趋势分析 + LLM 分析

⚠️ 成本控制配置
================
LLM 调用: OpenRouter DeepSeek R1 免费模型
模型: openrouter/deepseek/deepseek-r1-0528:free
费用: $0 (完全免费)

趋势预测: 简单规则模型 (本地计算)
费用: $0 (完全免费)

总成本: $0

作者: AI Article Publisher
创建时间: 2026-02-22
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

# 导入子模块
from topic_scorer import score_topic, rank_topics as base_rank
from trend_analyzer import analyze_topic_trend, batch_analyze_trends
from topic_analyzer import analyze_topic, rank_topics as llm_rank, OPENROUTER_API_KEY

# ============================================
# 成本控制配置
# ============================================
# 所有组件均免费

SELECTOR_CONFIG = {
    "name": "topic_selector",
    "version": "1.0.0",
    "components": {
        "base_scorer": {"model": "rules", "cost": "$0"},
        "trend_analyzer": {"model": "simple_rules", "cost": "$0"},
        "llm_analyzer": {"model": "step-3.5-flash-free", "cost": "$0"},
    },
    "total_cost": "$0",
    
    # 权重配置
    "weights": {
        "base_score": 0.3,      # 基础评分权重
        "trend_score": 0.3,     # 趋势评分权重
        "llm_score": 0.4,       # LLM 评分权重
    },
}


def load_topics_from_file(filepath: str) -> List[Dict]:
    """从文件加载选题"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 支持多种格式
    if isinstance(data, dict):
        if "items" in data:
            return list(data["items"].values())
        else:
            return list(data.values())
    elif isinstance(data, list):
        return data
    else:
        return []


def calculate_final_score(
    base_score: float,
    trend_score: float,
    llm_score: float,
    weights: Dict = None,
) -> float:
    """
    计算最终综合评分
    
    公式: final = base * w1 + trend * w2 + llm * w3
    """
    weights = weights or SELECTOR_CONFIG["weights"]
    
    # 归一化到 0-100
    base_normalized = min(base_score, 100)
    trend_normalized = min(trend_score, 100)
    llm_normalized = min(llm_score, 100)
    
    final = (
        base_normalized * weights["base_score"] +
        trend_normalized * weights["trend_score"] +
        llm_normalized * weights["llm_score"]
    )
    
    return round(final, 1)


def select_topics(
    topics: List[Dict],
    user_profile: Dict = None,
    top_n: int = 10,
    use_llm: bool = True,
    verbose: bool = True,
) -> List[Dict]:
    """
    智能选题选择
    
    Args:
        topics: 候选选题列表
        user_profile: 用户画像
        top_n: 返回数量
        use_llm: 是否使用 LLM 分析
        verbose: 是否打印详细信息
    
    Returns:
        排序后的选题列表
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"智能选题选择器 v{SELECTOR_CONFIG['version']}")
        print(f"{'='*70}")
        print(f"候选选题: {len(topics)} 个")
        print(f"返回数量: {top_n} 个")
        print(f"使用 LLM: {'是' if use_llm else '否'}")
        print(f"")
        print(f"组件配置:")
        print(f"  - 基础评分: {SELECTOR_CONFIG['components']['base_scorer']['model']} (免费)")
        print(f"  - 趋势分析: {SELECTOR_CONFIG['components']['trend_analyzer']['model']} (免费)")
        if use_llm:
            print(f"  - LLM分析: {SELECTOR_CONFIG['components']['llm_analyzer']['model']} (免费)")
        print(f"总成本: {SELECTOR_CONFIG['total_cost']}")
        print(f"{'='*70}\n")
    
    user_profile = user_profile or {
        "domains": ["教育", "心理学", "AI"],
        "style": "深度分析",
        "audience": "职场人士",
    }
    
    results = []
    
    for i, topic in enumerate(topics[:top_n * 2]):
        title = topic.get("title", "未知选题")
        
        if verbose:
            print(f"[{i+1}/{min(len(topics), top_n*2)}] 分析: {title[:40]}...")
        
        # 1. 基础评分
        base_result = score_topic(topic, user_profile.get("domains", []))
        base_score = base_result.get("total", 50)
        
        if verbose:
            print(f"    基础评分: {base_score}")
        
        # 2. 趋势分析
        trend_result = analyze_topic_trend(topic)
        trend_score = trend_result.get("trend_score", 50)
        
        if verbose:
            print(f"    趋势评分: {trend_score} ({trend_result.get('direction', '')})")
        
        # 3. LLM 分析 (可选)
        llm_score = 50
        llm_result = None
        
        if use_llm:
            if OPENROUTER_API_KEY:
                llm_result = analyze_topic(topic, user_profile)
                if "error" not in llm_result:
                    llm_score = llm_result.get("overall_score", 50)
                    if verbose:
                        print(f"    LLM评分: {llm_score} ({llm_result.get('recommendation', '')})")
                else:
                    if verbose:
                        print(f"    LLM分析: 失败 - {llm_result.get('error', '')}")
            else:
                if verbose:
                    print(f"    LLM分析: 跳过 (未配置 API Key)")
        
        # 4. 综合评分
        final_score = calculate_final_score(base_score, trend_score, llm_score)
        
        # 推荐等级
        if final_score >= 80:
            recommendation = "强烈推荐"
        elif final_score >= 70:
            recommendation = "推荐"
        elif final_score >= 60:
            recommendation = "可以考虑"
        else:
            recommendation = "不推荐"
        
        if verbose:
            print(f"    ✅ 综合评分: {final_score} ({recommendation})")
            print()
        
        # 组装结果
        result = {
            "title": title,
            "url": topic.get("url", ""),
            "source": topic.get("source", ""),
            "category": topic.get("category", ""),
            
            # 评分
            "final_score": final_score,
            "recommendation": recommendation,
            
            # 分项评分
            "scores": {
                "base": base_score,
                "trend": trend_score,
                "llm": llm_score if use_llm else None,
            },
            
            # 趋势信息
            "trend": {
                "direction": trend_result.get("direction", ""),
                "lifecycle": trend_result.get("lifecycle", ""),
                "best_timing": trend_result.get("best_timing", ""),
            },
            
            # LLM 分析结果
            "llm_analysis": llm_result,
            
            # 原始数据
            "raw": topic,
        }
        
        results.append(result)
    
    # 按综合评分排序
    results.sort(key=lambda x: x["final_score"], reverse=True)
    
    return results[:top_n]


def generate_final_report(results: List[Dict], output_format: str = "text") -> str:
    """生成最终报告"""
    
    if output_format == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    # 文本报告
    lines = [
        "=" * 70,
        "智能选题推荐报告",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 70,
        "",
    ]
    
    # 统计
    strong_rec = [r for r in results if r["final_score"] >= 80]
    rec = [r for r in results if 70 <= r["final_score"] < 80]
    consider = [r for r in results if 60 <= r["final_score"] < 70]
    
    lines.append(f"📊 推荐统计:")
    lines.append(f"  - 强烈推荐 (80+): {len(strong_rec)} 个")
    lines.append(f"  - 推荐 (70+): {len(rec)} 个")
    lines.append(f"  - 可以考虑 (60+): {len(consider)} 个")
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    
    for i, result in enumerate(results, 1):
        score_emoji = "🔥" if result["final_score"] >= 80 else "✅" if result["final_score"] >= 70 else "💡"
        
        lines.append(f"{score_emoji} 【{i}】{result['title']}")
        lines.append(f"    来源: {result['source']} | 分类: {result['category']}")
        lines.append(f"    综合评分: {result['final_score']} ({result['recommendation']})")
        lines.append(f"    分项: 基础{result['scores']['base']:.0f} + "
                    f"趋势{result['scores']['trend']:.0f}" +
                    (f" + LLM{result['scores']['llm']:.0f}" if result['scores']['llm'] else ""))
        
        trend = result.get("trend", {})
        if trend:
            lines.append(f"    趋势: {trend.get('direction', '')} | {trend.get('lifecycle', '')}")
            lines.append(f"    发布建议: {trend.get('best_timing', '')}")
        
        llm = result.get("llm_analysis", {})
        if llm and "writing_angles" in llm:
            angles = llm["writing_angles"][:2]
            lines.append("    写作角度:")
            for angle in angles:
                lines.append(f"      - {angle.get('angle', '')}: {angle.get('title', '')}")
        
        lines.append("")
    
    lines.extend([
        "=" * 70,
        "成本说明:",
        f"- 基础评分: $0 (本地规则)",
        f"- 趋势分析: $0 (本地计算)",
        f"- LLM分析: $0 (DeepSeek R1 免费模型)",
        f"- 总成本: $0",
        "",
        "评分权重:",
        f"- 基础评分: {SELECTOR_CONFIG['weights']['base_score']*100}%",
        f"- 趋势评分: {SELECTOR_CONFIG['weights']['trend_score']*100}%",
        f"- LLM评分: {SELECTOR_CONFIG['weights']['llm_score']*100}%",
        "=" * 70,
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='智能选题选择器')
    parser.add_argument('--input', '-i', help='输入JSON文件路径')
    parser.add_argument('--output', '-o', default='text', choices=['text', 'json'], help='输出格式')
    parser.add_argument('--top', '-n', type=int, default=5, help='输出数量')
    parser.add_argument('--domains', '-d', default='教育,心理学,AI', help='用户关注领域')
    parser.add_argument('--no-llm', action='store_true', help='不使用LLM分析')
    parser.add_argument('--quiet', '-q', action='store_true', help='安静模式')
    args = parser.parse_args()
    
    # 用户画像
    user_profile = {
        "domains": [d.strip() for d in args.domains.split(',')],
        "style": "深度分析",
        "audience": "职场人士",
    }
    
    # 加载选题
    if args.input:
        topics = load_topics_from_file(args.input)
    else:
        # 示例数据
        topics = [
            {"title": "AI 编程助手对比：Claude vs GPT-4", "source": "少数派", "score": "10万阅读", "category": "科技"},
            {"title": "心理学研究：压力与认知的关系", "source": "ScienceDaily", "score": "高热度", "category": "心理学"},
            {"title": "如何提高学习效率？5个实用方法", "source": "知乎", "score": "5000赞同", "category": "教育"},
        ]
    
    # 选择选题
    results = select_topics(
        topics,
        user_profile,
        top_n=args.top,
        use_llm=not args.no_llm,
        verbose=not args.quiet,
    )
    
    # 输出报告
    report = generate_final_report(results, args.output)
    print(report)
    
    # 保存报告
    if args.input:
        output_file = args.input.replace('.json', '_selected.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存: {output_file}")


if __name__ == '__main__':
    main()