#!/usr/bin/env python3
"""
写作工厂 - 优化改进器
基于 AI 的文章优化系统

功能:
1. AI 痕迹清除 - 移除套话
2. 金句增强 - 添加传播点
3. 数据补充 - 增加说服力
4. 案例丰富 - 提升可读性
5. 开头优化 - 增强吸引力
6. 结尾升华 - 提升价值
"""

import os
import sys
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deepseek_client import DeepSeekClient


class WritingOptimizer:
    """写作优化器"""
    
    def __init__(self, model: str = 'v3'):
        self.client = DeepSeekClient(model=model)
    
    def optimize(self, content: str, optimization_type: str = 'all') -> Dict:
        """
        优化文章
        
        Args:
            content: 原文内容
            optimization_type: 优化类型
                - all: 全面优化
                - ai_clean: AI 痕迹清除
                - golden_sentence: 金句增强
                - data: 数据补充
                - case: 案例丰富
                - opening: 开头优化
                - ending: 结尾升华
        
        Returns:
            优化结果
        """
        if optimization_type == 'all':
            return self._full_optimize(content)
        elif optimization_type == 'ai_clean':
            return self._clean_ai_traces(content)
        elif optimization_type == 'golden_sentence':
            return self._enhance_golden_sentences(content)
        elif optimization_type == 'data':
            return self._add_data_support(content)
        elif optimization_type == 'case':
            return self._add_cases(content)
        elif optimization_type == 'opening':
            return self._optimize_opening(content)
        elif optimization_type == 'ending':
            return self._optimize_ending(content)
        else:
            return self._full_optimize(content)
    
    def _full_optimize(self, content: str) -> Dict:
        """全面优化"""
        prompt = f"""你是一位资深的内容主编，请对以下文章进行全面优化：

【原文】
{content[:3000]}

【优化要求】
1. 清除 AI 套话（如"综上所述"、"在这个信息爆炸的时代"、"总而言之"等）
2. 增加 2-3 个金句，便于传播
3. 补充数据支撑观点
4. 增加 1-2 个案例
5. 优化开头，增强吸引力
6. 升华结尾，提升价值感

请输出优化后的完整文章。"""
        
        optimized = self.client._call_llm(prompt)
        
        return {
            'original': content,
            'optimized': optimized,
            'optimization_type': 'full',
            'improvements': [
                'AI 痕迹清除',
                '金句增强',
                '数据补充',
                '案例丰富',
                '开头优化',
                '结尾升华'
            ]
        }
    
    def _clean_ai_traces(self, content: str) -> Dict:
        """AI 痕迹清除"""
        ai_cliches = [
            '综上所述', '总而言之', '总的来说',
            '在这个信息爆炸的时代', '随着科技的发展',
            '我们可以看到', '不难看出', '显而易见',
            '首先...其次...最后', '一方面...另一方面'
        ]
        
        optimized = content
        for cliche in ai_cliches:
            optimized = optimized.replace(cliche, '')
        
        return {
            'original': content,
            'optimized': optimized,
            'optimization_type': 'ai_clean',
            'removed_cliches': [c for c in ai_cliches if c in content]
        }
    
    def _enhance_golden_sentences(self, content: str) -> Dict:
        """金句增强"""
        prompt = f"""请为以下文章增加 2-3 个金句：

【文章】
{content[:2000]}

【要求】
1. 金句要简洁有力
2. 易于传播和引用
3. 符合文章主题
4. 标注金句插入位置

输出格式：
{{
  "golden_sentences": [
    {{"sentence": "金句内容", "position": "插入位置"}}
  ],
  "optimized_content": "优化后的完整内容"
}}"""
        
        result = self.client._call_llm(prompt)
        
        return {
            'original': content,
            'optimized': result,
            'optimization_type': 'golden_sentence'
        }
    
    def _add_data_support(self, content: str) -> Dict:
        """数据补充"""
        prompt = f"""请为以下文章补充数据支撑：

【文章】
{content[:2000]}

【要求】
1. 补充 2-3 个相关数据
2. 数据要可靠可信
3. 标注数据来源
4. 自然融入文章

输出优化后的完整文章。"""
        
        optimized = self.client._call_llm(prompt)
        
        return {
            'original': content,
            'optimized': optimized,
            'optimization_type': 'data'
        }
    
    def _add_cases(self, content: str) -> Dict:
        """案例丰富"""
        prompt = f"""请为以下文章增加 1-2 个案例：

【文章】
{content[:2000]}

【要求】
1. 案例要真实可信
2. 与文章主题相关
3. 有细节描写
4. 自然融入文章

输出优化后的完整文章。"""
        
        optimized = self.client._call_llm(prompt)
        
        return {
            'original': content,
            'optimized': optimized,
            'optimization_type': 'case'
        }
    
    def _optimize_opening(self, content: str) -> Dict:
        """开头优化"""
        prompt = f"""请优化以下文章的开头：

【文章】
{content[:2000]}

【要求】
1. 前 3 句话要吸引眼球
2. 可以用问题/数据/故事开头
3. 快速切入主题
4. 激发读者兴趣

输出优化后的完整文章。"""
        
        optimized = self.client._call_llm(prompt)
        
        return {
            'original': content,
            'optimized': optimized,
            'optimization_type': 'opening'
        }
    
    def _optimize_ending(self, content: str) -> Dict:
        """结尾升华"""
        prompt = f"""请优化以下文章的结尾：

【文章】
{content[:2000]}

【要求】
1. 升华主题，提升价值
2. 给读者启发或行动建议
3. 留下深刻印象
4. 避免套话

输出优化后的完整文章。"""
        
        optimized = self.client._call_llm(prompt)
        
        return {
            'original': content,
            'optimized': optimized,
            'optimization_type': 'ending'
        }
    
    def batch_optimize(self, contents: List[str], optimization_type: str = 'all') -> List[Dict]:
        """批量优化"""
        results = []
        for i, content in enumerate(contents):
            print(f"优化进度：{i+1}/{len(contents)}")
            result = self.optimize(content, optimization_type)
            results.append(result)
        return results


# 便捷函数
def optimize_article(content: str, optimization_type: str = 'all') -> Dict:
    """优化文章便捷函数"""
    optimizer = WritingOptimizer()
    return optimizer.optimize(content, optimization_type)


def optimize_batch(contents: List[str], optimization_type: str = 'all') -> List[Dict]:
    """批量优化便捷函数"""
    optimizer = WritingOptimizer()
    return optimizer.batch_optimize(contents, optimization_type)


# 使用示例
if __name__ == '__main__':
    optimizer = WritingOptimizer(model='v3')
    
    # 测试 AI 痕迹清除
    test_content = """
    综上所述，在这个信息爆炸的时代，我们可以看到 AI 技术正在改变世界。
    总而言之，AI 的应用前景广阔。
    """
    
    result = optimizer._clean_ai_traces(test_content)
    print("原文:", test_content)
    print("优化后:", result['optimized'])
    print("移除套话:", result['removed_cliches'])
