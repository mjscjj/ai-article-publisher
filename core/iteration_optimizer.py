#!/usr/bin/env python3
"""
【迭代优化器】Iteration Optimizer
基于上一轮文章质量，自动优化搜索策略和写作参数

功能:
1. 分析文章质量 (字数、结构、引用密度)
2. 调整搜索关键词策略
3. 优化 Prompt 组合
4. 生成改进建议
"""

import json
import os
import re
from typing import Dict, List, Any

class ArticleAnalyzer:
    """文章质量分析器"""
    
    def __init__(self):
        self.ai_cliches = [
            "在这个信息爆炸的时代",
            "随着科技的发展",
            "不可否认",
            "综上所述",
            "总而言之",
            "在这个充满挑战",
            "我们需要共同努力",
            "让我们携手",
            "展望未来",
            "具有重要意义",
        ]
    
    def analyze(self, article_path: str) -> Dict[str, Any]:
        """分析文章质量"""
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 去除思考链路
        if "【🧠 Kimi 2.5 内部推演回路" in content:
            match = re.search(r'【🖋️ Kimi 2.5 最终执行出稿】\n(.*)', content, re.S)
            content = match.group(1) if match else content
        
        # 基本统计
        char_count = len(content)
        para_count = len([p for p in content.split('\n\n') if p.strip()])
        
        # AI 套话检测
        ai_cliche_count = sum(1 for cliche in self.ai_cliches if cliche in content)
        
        # 数据密度 (数字出现频率)
        numbers = re.findall(r'\d+', content)
        data_density = len(numbers) / max(1, char_count / 1000)
        
        # 引用检测
        quotes = re.findall(r'[""].*?[""]', content)
        quote_density = len(quotes) / max(1, para_count)
        
        # 小标题检测
        headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.M)
        
        # 项目符号检测 (违规)
        bullet_violations = len(re.findall(r'^[\-\*]\s+', content, re.M))
        numbered_violations = len(re.findall(r'^\d+\.\s+', content, re.M))
        
        return {
            "char_count": char_count,
            "para_count": para_count,
            "heading_count": len(headings),
            "ai_cliche_count": ai_cliche_count,
            "data_density": round(data_density, 1),
            "quote_density": round(quote_density, 1),
            "bullet_violations": bullet_violations,
            "numbered_violations": numbered_violations,
            "quality_score": self._calculate_score(
                char_count, ai_cliche_count, data_density, 
                quote_density, bullet_violations + numbered_violations
            ),
            "recommendations": self._generate_recommendations(
                char_count, ai_cliche_count, data_density,
                quote_density, bullet_violations + numbered_violations
            ),
        }
    
    def _calculate_score(self, chars, cliches, data_density, quote_density, violations) -> int:
        """计算质量分数 (0-100)"""
        score = 50
        
        # 字数分 (目标 1500-3000)
        if 1500 <= chars <= 3000:
            score += 20
        elif 1000 <= chars < 1500 or 3000 < chars <= 4000:
            score += 10
        
        # AI 套话扣分
        score -= cliches * 5
        
        # 数据密度加分
        if data_density >= 20:
            score += 10
        elif data_density >= 10:
            score += 5
        
        # 引用密度加分
        if quote_density >= 1.5:
            score += 10
        elif quote_density >= 0.8:
            score += 5
        
        # 违规扣分
        score -= violations * 10
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, chars, cliches, data_density, quote_density, violations) -> List[str]:
        """生成改进建议"""
        recs = []
        
        if chars < 1500:
            recs.append("📏 字数偏少，建议增加深度分析和案例")
        elif chars > 4000:
            recs.append("📏 字数过多，建议精简冗余表述")
        
        if cliches > 0:
            recs.append(f"⚠️ 发现 {cliches} 处 AI 套话，需删除替换")
        
        if data_density < 10:
            recs.append("📊 数据密度不足，增加具体数字和报告引用")
        
        if quote_density < 0.8:
            recs.append("💬 引用密度不足，增加当事人原话和专家观点")
        
        if violations > 0:
            recs.append(f"❌ 发现 {violations} 处项目符号违规，改用完整段落")
        
        return recs if recs else ["✅ 文章质量良好，无需重大调整"]


class IterationOptimizer:
    """迭代优化器"""
    
    def __init__(self):
        self.analyzer = ArticleAnalyzer()
    
    def optimize(self, article_path: str, config_path: str = None) -> Dict[str, Any]:
        """
        基于文章分析结果，优化下一轮配置
        """
        # 分析文章
        analysis = self.analyzer.analyze(article_path)
        
        # 生成优化建议
        optimizations = {
            "prompt_adjustments": [],
            "search_adjustments": [],
            "config_changes": {},
        }
        
        # 根据问题调整策略
        if analysis["ai_cliche_count"] > 0:
            optimizations["prompt_adjustments"].append(
                "强化 anti_ai_formatting 约束，添加更多禁止套话示例"
            )
        
        if analysis["data_density"] < 10:
            optimizations["prompt_adjustments"].append(
                "在 Prompt 中强制要求每个论点配 1-2 个具体数据"
            )
            optimizations["search_adjustments"].append(
                "搜索时优先抓取含数据的新闻源 (财报、报告、统计数据)"
            )
        
        if analysis["quote_density"] < 0.8:
            optimizations["prompt_adjustments"].append(
                "启用 quote_heavy 风格，强制要求 3+ 处直接引语"
            )
            optimizations["search_adjustments"].append(
                "增加知乎/微博等含用户评论的数据源权重"
            )
        
        if analysis["char_count"] < 1500:
            optimizations["prompt_adjustments"].append(
                "调整字数要求为 2000-2500 字"
            )
        
        return {
            "analysis": analysis,
            "optimizations": optimizations,
        }


if __name__ == "__main__":
    import sys
    
    article_path = sys.argv[1] if len(sys.argv) > 1 else "data/e2e_test_article.md"
    
    if not os.path.exists(article_path):
        print(f"❌ 文件不存在：{article_path}")
        sys.exit(1)
    
    optimizer = IterationOptimizer()
    result = optimizer.optimize(article_path)
    
    print("\n" + "="*70)
    print("📊 文章质量分析报告")
    print("="*70)
    
    analysis = result["analysis"]
    print(f"\n基本统计:")
    print(f"  字数：{analysis['char_count']}")
    print(f"  段落：{analysis['para_count']}")
    print(f"  小标题：{analysis['heading_count']}")
    
    print(f"\n质量指标:")
    print(f"  AI 套话：{analysis['ai_cliche_count']} 处")
    print(f"  数据密度：{analysis['data_density']} 个/千字")
    print(f"  引用密度：{analysis['quote_density']} 个/段")
    print(f"  格式违规：{analysis['bullet_violations'] + analysis['numbered_violations']} 处")
    
    print(f"\n综合评分：{analysis['quality_score']}/100")
    
    print(f"\n改进建议:")
    for rec in analysis["recommendations"]:
        print(f"  {rec}")
    
    print("\n" + "="*70)
    print("🔧 优化建议")
    print("="*70)
    
    opts = result["optimizations"]
    if opts["prompt_adjustments"]:
        print("\nPrompt 调整:")
        for adj in opts["prompt_adjustments"]:
            print(f"  - {adj}")
    
    if opts["search_adjustments"]:
        print("\n搜索策略调整:")
        for adj in opts["search_adjustments"]:
            print(f"  - {adj}")
    
    print("\n")
