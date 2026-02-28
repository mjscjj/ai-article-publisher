#!/usr/bin/env python3
"""
DeepSeek 客户端 - 工作评价专用
基于 AnythingLLM 统一路由

支持模型:
- deepseek/deepseek-chat (高性价比)
- deepseek/deepseek-r1-0528:free (免费)
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime


class DeepSeekClient:
    """
    DeepSeek API 客户端
    
    通过 AnythingLLM 统一路由调用 DeepSeek 模型
    """
    
    # 配置
    AI_BASE_URL = os.getenv('AI_BASE_URL', 'http://43.134.234.4:3001')
    API_KEY = os.getenv('AI_BASE_API_KEY', 'sk-WaUmgZsMxgeHOpp8SJxK1rmVQxiwfiDJ')
    WORKSPACE = os.getenv('AI_WORKSPACE', 'common')
    
    # 模型配置
    MODELS = {
        'chat': 'deepseek/deepseek-chat',  # 高性价比
        'free': 'deepseek/deepseek-r1-0528:free',  # 免费
        'v3': 'deepseek/deepseek-chat-v3'  # V3 版本
    }
    
    def __init__(self, model: str = 'chat'):
        """
        初始化客户端
        
        Args:
            model: 模型类型 ('chat' | 'free' | 'v3')
        """
        self.model = self.MODELS.get(model, self.MODELS['chat'])
        self.session = requests.Session()
    
    def evaluate_article(self, title: str, content: str, 
                        evaluation_type: str = 'article') -> Dict[str, Any]:
        """
        评价文章/选题
        
        Args:
            title: 标题
            content: 内容
            evaluation_type: 评价类型 ('article' | 'topic')
        
        Returns:
            评价结果字典
        """
        prompt = self._build_evaluation_prompt(title, content, evaluation_type)
        
        try:
            response = self._call_llm(prompt)
            result = self._parse_evaluation_result(response)
            result['model_used'] = self.model
            result['evaluated_at'] = datetime.now().isoformat()
            return result
        except Exception as e:
            return {
                'error': str(e),
                'total_score': 0,
                'grade': 'E',
                'recommendation': '评估失败，请重试'
            }
    
    def _build_evaluation_prompt(self, title: str, content: str, 
                                  eval_type: str) -> str:
        """构建评价 Prompt"""
        
        if eval_type == 'topic':
            template = """你是一位资深的内容策划专家，拥有 10 年媒体从业经验。

请对以下选题进行专业评估：

【选题标题】
{title}

【选题描述】
{content}

【评估要求】
1. 从 5 个维度打分 (0-100):
   - 热度分 (30%): 基于平台热度
   - 潜力分 (25%): 趋势预测
   - 匹配分 (20%): 与账号定位匹配度
   - 新颖分 (15%): 独特性/差异化
   - 可行分 (10%): 素材充足度

2. 给出总体评分和等级 (S/A/B/C/D)

3. 指出 3 个优点

4. 指出 3 个改进建议

5. 给出最终推荐 (优先写作/正常写作/需要优化/放弃)

请严格按照以下 JSON 格式输出 (只输出 JSON，不要其他内容):
{{
  "scores": {{
    "heat": 85,
    "potential": 80,
    "match": 75,
    "novelty": 90,
    "feasibility": 70
  }},
  "total_score": 82,
  "grade": "A",
  "strengths": ["优点 1", "优点 2", "优点 3"],
  "improvements": ["建议 1", "建议 2", "建议 3"],
  "recommendation": "正常写作",
  "comment": "总体评价"
}}"""
        else:
            template = """你是一位资深的内容质量评估专家，拥有 10 年媒体从业经验。

请对以下文章进行专业评估：

【文章标题】
{title}

【文章内容】
{content}

【评估要求】
1. 从 5 个维度打分 (0-100):
   - 内容质量 (30%): 准确性、深度、数据支撑
   - 结构逻辑 (25%): 框架清晰、层次分明、过渡自然
   - 表达文采 (20%): 语言流畅、修辞运用、金句
   - 传播价值 (15%): 话题性、共鸣点、传播潜力
   - 创新独特 (10%): 视角新颖、差异化、独特见解

2. 给出总体评分和等级 (S/A/B/C/D)

3. 指出 3 个优点

4. 指出 3 个改进建议

5. 给出最终推荐 (优先发布/正常发布/修改后发布/返回重写/废弃)

请严格按照以下 JSON 格式输出 (只输出 JSON，不要其他内容):
{{
  "scores": {{
    "content": 85,
    "structure": 80,
    "expression": 75,
    "viral": 90,
    "innovation": 70
  }},
  "total_score": 82,
  "grade": "A",
  "strengths": ["优点 1", "优点 2", "优点 3"],
  "improvements": ["建议 1", "建议 2", "建议 3"],
  "recommendation": "正常发布",
  "comment": "总体评价"
}}"""
        
        return template.format(title=title, content=content[:3000])  # 限制长度
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        url = f"{self.AI_BASE_URL}/api/v1/workspace/{self.WORKSPACE}/chat"
        
        headers = {
            'Authorization': f'Bearer {self.API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'message': prompt,
            'mode': 'chat',
            'model': self.model
        }
        
        response = self.session.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        return data.get('response', '')
    
    def _parse_evaluation_result(self, response: str) -> Dict[str, Any]:
        """解析评价结果"""
        try:
            # 提取 JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
            else:
                result = json.loads(response)
            
            # 计算总分
            if 'scores' in result:
                scores = result['scores']
                weights = self._get_weights()
                total = sum(scores[k] * weights.get(k, 0.2) for k in scores)
                result['total_score'] = round(total, 1)
            
            # 确定等级
            total = result.get('total_score', 0)
            if total >= 90:
                result['grade'] = 'S'
            elif total >= 80:
                result['grade'] = 'A'
            elif total >= 70:
                result['grade'] = 'B'
            elif total >= 60:
                result['grade'] = 'C'
            else:
                result['grade'] = 'D'
            
            return result
            
        except Exception as e:
            return {
                'error': f'解析失败：{e}',
                'total_score': 0,
                'grade': 'E',
                'recommendation': '解析失败，请重试'
            }
    
    def _get_weights(self) -> Dict[str, float]:
        """获取评分权重"""
        return {
            # 文章评价权重
            'content': 0.30,
            'structure': 0.25,
            'expression': 0.20,
            'viral': 0.15,
            'innovation': 0.10,
            # 选题评价权重
            'heat': 0.30,
            'potential': 0.25,
            'match': 0.20,
            'novelty': 0.15,
            'feasibility': 0.10
        }
    
    def batch_evaluate(self, items: list, eval_type: str = 'article') -> list:
        """
        批量评价
        
        Args:
            items: 评价项列表 [{'title': '', 'content': ''}, ...]
            eval_type: 评价类型
        
        Returns:
            评价结果列表
        """
        results = []
        for i, item in enumerate(items):
            print(f"评价进度：{i+1}/{len(items)}")
            result = self.evaluate_article(
                item.get('title', ''),
                item.get('content', ''),
                eval_type
            )
            results.append(result)
        return results


# 使用示例
if __name__ == '__main__':
    client = DeepSeekClient(model='free')  # 使用免费模型
    
    # 测试文章评价
    test_article = {
        'title': 'AI 教育正在改变未来',
        'content': '''
        人工智能技术的快速发展正在深刻改变教育行业。
        从智能辅导系统到个性化学习路径，AI 的应用场景越来越广泛。
        然而，我们也应该看到，AI 教育还面临诸多挑战...
        '''
    }
    
    result = client.evaluate_article(
        test_article['title'],
        test_article['content'],
        eval_type='article'
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
