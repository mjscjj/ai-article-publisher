#!/usr/bin/env python3
"""
写作工厂 - 大纲生成器
基于 DeepSeek V3 的智能大纲生成

功能:
- 根据选题生成文章大纲
- 支持 5 种结构模板
- 适配 10+ 种写作风格
- 输出结构化 JSON
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.deepseek_client import DeepSeekClient


class Outliner:
    """
    大纲生成器
    
    根据选题和风格生成文章大纲
    """
    
    # 结构模板
    STRUCTURES = {
        '总分总': {
            'name': '总分总',
            'description': '经典结构 - 开篇点题，分论点展开，总结升华',
            'sections': [
                {'name': '开篇', 'guidance': '点明主题，引发兴趣'},
                {'name': '分论点一', 'guidance': '第一个核心观点'},
                {'name': '分论点二', 'guidance': '第二个核心观点'},
                {'name': '分论点三', 'guidance': '第三个核心观点'},
                {'name': '总结', 'guidance': '总结全文，升华主题'}
            ]
        },
        '问题 - 分析 - 解决': {
            'name': '问题 - 分析 - 解决',
            'description': '实用结构 - 提出问题，分析原因，给出方案',
            'sections': [
                {'name': '问题提出', 'guidance': '描述现状和痛点'},
                {'name': '原因分析', 'guidance': '深入分析问题根源'},
                {'name': '解决方案', 'guidance': '给出具体可行的方案'},
                {'name': '实施建议', 'guidance': '落地执行的建议'}
            ]
        },
        '时间线': {
            'name': '时间线',
            'description': '叙事结构 - 过去，现在，未来',
            'sections': [
                {'name': '过去', 'guidance': '历史背景和发展'},
                {'name': '现在', 'guidance': '当前状况和挑战'},
                {'name': '未来', 'guidance': '趋势预测和展望'}
            ]
        },
        '对比式': {
            'name': '对比式',
            'description': '辩证结构 - 正面，反面，综合',
            'sections': [
                {'name': '正面观点', 'guidance': '支持方的论据'},
                {'name': '反面观点', 'guidance': '反对方的论据'},
                {'name': '综合分析', 'guidance': '辩证看待，给出见解'}
            ]
        },
        '金字塔': {
            'name': '金字塔',
            'description': '结论先行 - 核心结论，支撑论据，详细说明',
            'sections': [
                {'name': '核心结论', 'guidance': '开门见山给出结论'},
                {'name': '支撑论据', 'guidance': '3 个核心论据'},
                {'name': '详细说明', 'guidance': '展开论述'},
                {'name': '行动建议', 'guidance': '给读者的建议'}
            ]
        }
    }
    
    # 写作风格
    STYLES = {
        '学术深度': {
            'name': '学术深度',
            'tone': '严谨',
            'characteristics': ['引用权威', '理论支撑', '数据详实'],
            'word_count_range': [1500, 3000]
        },
        '新闻报道': {
            'name': '新闻报道',
            'tone': '客观',
            'characteristics': ['事实准确', '时效性强', '简洁明了'],
            'word_count_range': [800, 1500]
        },
        '商业分析': {
            'name': '商业分析',
            'tone': '理性',
            'characteristics': ['逻辑清晰', '数据驱动', '洞察深刻'],
            'word_count_range': [1500, 2500]
        },
        '幽默调侃': {
            'name': '幽默调侃',
            'tone': '轻松',
            'characteristics': ['语言风趣', '梗多', '吐槽犀利'],
            'word_count_range': [1000, 2000]
        },
        '文艺抒情': {
            'name': '文艺抒情',
            'tone': '感性',
            'characteristics': ['修辞丰富', '意境优美', '情感真挚'],
            'word_count_range': [1200, 2500]
        },
        '热血激励': {
            'name': '热血激励',
            'tone': '激情',
            'characteristics': ['号召力强', '正能量', '行动导向'],
            'word_count_range': [1000, 2000]
        },
        '极客技术': {
            'name': '极客技术',
            'tone': '专业',
            'characteristics': ['术语准确', '实操性强', '案例丰富'],
            'word_count_range': [1500, 3000]
        },
        '教育科普': {
            'name': '教育科普',
            'tone': '亲和',
            'characteristics': ['易懂', '案例多', '互动性强'],
            'word_count_range': [1200, 2000]
        },
        '财经评论': {
            'name': '财经评论',
            'tone': '犀利',
            'characteristics': ['洞察深刻', '观点鲜明', '预测准确'],
            'word_count_range': [1500, 2500]
        },
        '毒舌评论': {
            'name': '毒舌评论',
            'tone': '尖锐',
            'characteristics': ['批判性强', '反转多', '金句频出'],
            'word_count_range': [1000, 2000]
        }
    }
    
    def __init__(self, model: str = 'v3'):
        """
        初始化大纲生成器
        
        Args:
            model: DeepSeek 模型类型
        """
        self.client = DeepSeekClient(model=model)
    
    def generate(self, title: str, description: str, key_points: List[str] = None,
                 style: str = '新闻报道', structure: str = '总分总',
                 word_count: int = 2000) -> Dict[str, Any]:
        """
        生成文章大纲
        
        Args:
            title: 文章标题
            description: 选题描述
            key_points: 核心要点
            style: 写作风格
            structure: 结构模板
            word_count: 目标字数
        
        Returns:
            大纲字典
        """
        # 验证风格和结构
        if style not in self.STYLES:
            style = '新闻报道'
        if structure not in self.STRUCTURES:
            structure = '总分总'
        
        # 构建 Prompt
        prompt = self._build_prompt(title, description, key_points, style, structure, word_count)
        
        # 调用 DeepSeek V3
        response = self.client._call_llm(prompt)
        
        # 解析结果
        outline = self._parse_response(response, title, style, structure, word_count)
        
        return outline
    
    def _build_prompt(self, title: str, description: str, key_points: List[str],
                      style: str, structure: str, word_count: int) -> str:
        """构建生成 Prompt"""
        
        style_info = self.STYLES[style]
        structure_info = self.STRUCTURES[structure]
        
        key_points_str = '\n'.join([f"- {kp}" for kp in (key_points or [])])
        
        prompt = f"""你是一位资深的内容策划专家，拥有 10 年媒体从业经验。

请为以下选题生成文章大纲：

【选题标题】
{title}

【选题描述】
{description}

【核心要点】
{key_points_str if key_points_str else '无特定要求，请自由发挥'}

【写作风格】
{style}
- 语调：{style_info['tone']}
- 特点：{', '.join(style_info['characteristics'])}
- 字数范围：{style_info['word_count_range'][0]}-{style_info['word_count_range'][1]}字

【结构模板】
{structure}
{structure_info['description']}

【生成要求】
1. 生成 3-5 个小节
2. 每个小节包含：
   - name: 小节标题 (简洁有力)
   - guidance: 写作方向 (具体指导)
   - quote_req: 需要引用的事实或数据 (可选)
3. 符合{style}风格特点
4. 结构清晰，逻辑连贯
5. 避免 AI 套话

请严格按照以下 JSON 格式输出 (只输出 JSON，不要其他内容):
{{
  "title": "文章标题",
  "style": "{style}",
  "structure": "{structure}",
  "target_word_count": {word_count},
  "sections": [
    {{
      "name": "小节标题",
      "guidance": "写作方向",
      "quote_req": "需要引用的事实"
    }}
  ],
  "estimated_word_distribution": {{
    "section_1": 300,
    "section_2": 500,
    ...
  }},
  "writing_tips": ["写作建议 1", "写作建议 2"]
}}"""
        
        return prompt
    
    def _parse_response(self, response: str, title: str, style: str, 
                        structure: str, word_count: int) -> Dict[str, Any]:
        """解析响应"""
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                outline = json.loads(json_match.group())
            else:
                outline = json.loads(response)
            
            # 补充元数据
            outline['generated_at'] = datetime.now().isoformat()
            outline['model_used'] = 'deepseek-chat-v3'
            
            return outline
            
        except Exception as e:
            # 降级处理
            return self._fallback_outline(title, style, structure, word_count, str(e))
    
    def _fallback_outline(self, title: str, style: str, structure: str,
                          word_count: int, error: str) -> Dict[str, Any]:
        """降级大纲"""
        structure_info = self.STRUCTURES.get(structure, self.STRUCTURES['总分总'])
        
        sections = []
        for i, sec in enumerate(structure_info['sections'][:4]):
            sections.append({
                'name': sec['name'],
                'guidance': sec['guidance'],
                'quote_req': f'请从选题材料中抽取相关事实',
                '_fallback': True
            })
        
        return {
            'title': title,
            'style': style,
            'structure': structure,
            'target_word_count': word_count,
            'sections': sections,
            'estimated_word_distribution': {
                f'section_{i+1}': word_count // len(sections)
                for i in range(len(sections))
            },
            'writing_tips': [
                '保持逻辑连贯',
                '引用可靠数据',
                '避免 AI 套话'
            ],
            'generated_at': datetime.now().isoformat(),
            'model_used': 'fallback',
            '_error': error
        }
    
    def get_styles(self) -> List[Dict]:
        """获取所有风格"""
        return [
            {'id': k, **v}
            for k, v in self.STYLES.items()
        ]
    
    def get_structures(self) -> List[Dict]:
        """获取所有结构模板"""
        return [
            {'id': k, **v}
            for k, v in self.STRUCTURES.items()
        ]


# 使用示例
if __name__ == '__main__':
    outliner = Outliner(model='v3')
    
    # 测试生成大纲
    outline = outliner.generate(
        title='AI 教育正在改变未来',
        description='人工智能技术在教育领域的应用越来越广泛，从智能辅导到个性化学习...',
        key_points=['AI 技术应用', '教育公平', '教师角色转变'],
        style='商业分析',
        structure='总分总',
        word_count=2000
    )
    
    print(json.dumps(outline, ensure_ascii=False, indent=2))
