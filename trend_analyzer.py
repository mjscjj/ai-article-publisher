#!/usr/bin/env python3
"""
简化版趋势分析器
使用简单规则进行热点趋势预测，不依赖复杂模型

⚠️ 设计原则: 简单 > 复杂
   不使用 LSTM/STL/Prophet 等复杂模型
   使用简单统计规则

作者: AI Article Publisher
创建时间: 2026-02-22
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re

# ============================================
# 趋势预测配置
# ============================================
# 使用简单规则，不使用复杂模型
# 成本: $0 (纯本地计算)

TREND_CONFIG = {
    "model": "simple_rules",  # 简单规则模型
    "cost": "$0",
    "hot_threshold": 70,       # 热度阈值
    "growth_threshold": 0.3,   # 增长率阈值 (30%)
    "decay_half_life": 3,      # 热点半衰期 (天)
}


def extract_hotness_value(score_str: str) -> int:
    """
    从热度字符串提取数值
    
    Examples:
        "10万阅读" → 100000
        "5000赞同" → 5000
        "100万+" → 1000000
    """
    if not score_str:
        return 0
    
    # 提取数字
    numbers = re.findall(r'[\d.]+', str(score_str))
    if not numbers:
        return 0
    
    num = float(numbers[0])
    
    # 处理单位
    if '万' in str(score_str):
        num *= 10000
    elif '千' in str(score_str):
        num *= 1000
    elif '百万' in str(score_str):
        num *= 1000000
    
    return int(num)


def calculate_trend_score(
    current_hotness: int,
    history_hotness: List[int] = None,
    days_since_publish: int = 0,
) -> Dict:
    """
    计算趋势分数
    
    使用简单规则:
    1. 增长率 = (当前 - 历史) / 历史
    2. 衰减 = 根据天数估算
    3. 生命周期 = 增长率 - 衰减
    
    Args:
        current_hotness: 当前热度值
        history_hotness: 历史热度列表 [昨天, 前天, ...]
        days_since_publish: 发布天数
    
    Returns:
        趋势分析结果
    """
    # 默认历史数据
    if history_hotness is None:
        history_hotness = [current_hotness * 0.8]  # 假设昨天是今天的 80%
    
    # 计算增长率
    if len(history_hotness) > 0 and history_hotness[0] > 0:
        growth_rate = (current_hotness - history_hotness[0]) / history_hotness[0]
    else:
        growth_rate = 0
    
    # 计算衰减 (指数衰减)
    if days_since_publish > 0:
        decay_factor = 0.5 ** (days_since_publish / TREND_CONFIG["decay_half_life"])
    else:
        decay_factor = 1.0
    
    # 趋势分数 = 增长率 * 衰减因子
    trend_score = (1 + growth_rate) * decay_factor * 50  # 归一化到 0-100
    
    # 判断趋势方向
    if growth_rate > TREND_CONFIG["growth_threshold"]:
        direction = "上升"
        emoji = "📈"
    elif growth_rate < -TREND_CONFIG["growth_threshold"]:
        direction = "下降"
        emoji = "📉"
    else:
        direction = "平稳"
        emoji = "➡️"
    
    # 预测生命周期
    if growth_rate > 0.5:
        lifecycle = "爆发期 (预计持续 2-3 天)"
        best_timing = "尽快发布"
    elif growth_rate > 0.2:
        lifecycle = "上升期 (预计持续 3-5 天)"
        best_timing = "今天或明天发布"
    elif growth_rate > 0:
        lifecycle = "平稳期 (预计持续 5-7 天)"
        best_timing = "本周内发布"
    else:
        lifecycle = "衰退期 (热点已过)"
        best_timing = "不建议发布"
    
    return {
        "trend_score": round(trend_score, 1),
        "growth_rate": round(growth_rate * 100, 1),  # 转为百分比
        "decay_factor": round(decay_factor, 2),
        "direction": direction,
        "emoji": emoji,
        "lifecycle": lifecycle,
        "best_timing": best_timing,
        "model": TREND_CONFIG["model"],
        "cost": TREND_CONFIG["cost"],
    }


def analyze_topic_trend(topic: Dict, history_data: Dict = None) -> Dict:
    """
    分析单个选题的趋势
    
    Args:
        topic: 选题信息
        history_data: 历史数据 (可选)
    
    Returns:
        趋势分析结果
    """
    # 提取热度值
    hotness = extract_hotness_value(topic.get("score", ""))
    
    # 获取历史数据
    history_hotness = None
    if history_data and topic.get("id") in history_data:
        history_hotness = history_data[topic["id"]].get("hotness_history", [])
    
    # 计算发布天数 (从爬取时间推断)
    days = 0
    if topic.get("crawl_time"):
        try:
            crawl_time = datetime.strptime(topic["crawl_time"], "%Y-%m-%d %H:%M:%S")
            days = (datetime.now() - crawl_time).days
        except:
            pass
    
    # 计算趋势
    trend = calculate_trend_score(hotness, history_hotness, days)
    
    # 添加原始信息
    trend["topic"] = topic.get("title", "")
    trend["current_hotness"] = hotness
    
    return trend


def batch_analyze_trends(
    topics: List[Dict],
    history_data: Dict = None,
) -> List[Dict]:
    """
    批量分析趋势
    
    Args:
        topics: 选题列表
        history_data: 历史数据
    
    Returns:
        排序后的趋势分析结果
    """
    print(f"\n{'='*60}")
    print(f"趋势分析")
    print(f"{'='*60}")
    print(f"模型: {TREND_CONFIG['model']} (简单规则)")
    print(f"费用: 免费 ($0)")
    print(f"分析选题: {len(topics)} 个")
    print(f"{'='*60}\n")
    
    results = []
    
    for i, topic in enumerate(topics):
        trend = analyze_topic_trend(topic, history_data)
        results.append(trend)
        
        print(f"[{i+1}] {trend['topic'][:40]}...")
        print(f"    {trend['emoji']} 趋势: {trend['direction']} ({trend['growth_rate']}%)")
        print(f"    📊 评分: {trend['trend_score']} | 生命周期: {trend['lifecycle']}")
        print(f"    ⏰ 建议: {trend['best_timing']}")
        print()
    
    # 按趋势分数排序
    results.sort(key=lambda x: x["trend_score"], reverse=True)
    
    return results


def generate_trend_report(results: List[Dict], output_format: str = "text") -> str:
    """生成趋势报告"""
    
    if output_format == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    # 文本报告
    lines = [
        "=" * 70,
        "热点趋势分析报告",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"模型: {TREND_CONFIG['model']} (简单规则)",
        f"费用: 免费 ($0)",
        "=" * 70,
        "",
    ]
    
    # 分类统计
    rising = [r for r in results if r["direction"] == "上升"]
    stable = [r for r in results if r["direction"] == "平稳"]
    falling = [r for r in results if r["direction"] == "下降"]
    
    lines.append(f"📈 上升趋势: {len(rising)} 个")
    lines.append(f"➡️ 平稳趋势: {len(stable)} 个")
    lines.append(f"📉 下降趋势: {len(falling)} 个")
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    
    # 推荐发布
    lines.append("🔥 推荐尽快发布:")
    for i, r in enumerate([r for r in results if "尽快" in r["best_timing"]][:5], 1):
        lines.append(f"  {i}. {r['topic'][:50]}")
        lines.append(f"     趋势: {r['emoji']} {r['direction']} | 热度: {r['current_hotness']:,}")
        lines.append("")
    
    lines.extend([
        "=" * 70,
        "趋势说明:",
        "- 📈 上升: 增长率 > 30%, 热度正在上升",
        "- ➡️ 平稳: 增长率在 ±30% 内, 热度稳定",
        "- 📉 下降: 增长率 < -30%, 热度正在下降",
        "",
        "发布建议:",
        "- 上升期选题: 尽快发布, 抓住热度",
        "- 平稳期选题: 可择机发布, 时间充裕",
        "- 衰退期选题: 不建议发布, 热度已过",
        "",
        f"成本: $0 (本地计算)",
        "=" * 70,
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='简化版趋势分析器')
    parser.add_argument('--input', '-i', help='输入JSON文件路径')
    parser.add_argument('--output', '-o', default='text', choices=['text', 'json'], help='输出格式')
    parser.add_argument('--top', '-n', type=int, default=10, help='输出数量')
    args = parser.parse_args()
    
    # 读取输入
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 支持两种格式: 列表或对象
            if isinstance(data, dict) and "items" in data:
                topics = list(data["items"].values())
            elif isinstance(data, dict):
                topics = list(data.values())
            else:
                topics = data
    else:
        # 示例数据
        topics = [
            {"title": "AI 编程助手对比", "score": "10万阅读", "crawl_time": "2026-02-22 06:00:00"},
            {"title": "心理学研究新发现", "score": "50万阅读", "crawl_time": "2026-02-22 06:00:00"},
            {"title": "学习方法总结", "score": "5000赞同", "crawl_time": "2026-02-21 12:00:00"},
        ]
    
    # 分析趋势
    results = batch_analyze_trends(topics[:args.top * 2])
    
    # 输出报告
    report = generate_trend_report(results[:args.top], args.output)
    print(report)


if __name__ == '__main__':
    main()