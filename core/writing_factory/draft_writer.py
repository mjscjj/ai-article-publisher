#!/usr/bin/env python3
"""
写作工厂 - 初稿撰写器
基于 DeepSeek V3 的智能写作

功能:
- 根据大纲撰写初稿
- 支持 10+ 种写作风格
- 事实注入
- 长度控制
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.deepseek_client import DeepSeekClient


class DraftWriter:
    """
    初稿撰写器
    
    根据大纲和风格撰写文章初稿
    """
    
    def __init__(self, model: str = 'v3'):
        """
        初始化撰写器
        
        Args:
            model: DeepSeek 模型类型
        """
        self.client = DeepSeekClient(model=model)
    
    def write(self, outline: Dict[str, Any], style: str = '新闻报道',
              facts: List[Dict] = None) -> Dict[str, Any]:
        """
        撰写文章初稿
        
        Args:
            outline: 文章大纲
            style: 写作风格
            facts: 事实包 (可选)
        
        Returns:
            文章初稿
        """
        sections = outline.get('sections', [])
        target_word_count = outline.get('target_word_count', 2000)
        
        # 逐节撰写
        full_content = []
        section_results = []
        
        for i, section in enumerate(sections):
            print(f"  撰写第{i+1}/{len(sections)}节：{section.get('name', '未知')}")
            
            # 提取相关事实
            section_facts = self._extract_relevant_facts(facts, section)
            
            # 撰写本节
            section_content = self._write_section(
                title=outline.get('title', ''),
                section=section,
                style=style,
                facts=section_facts,
                word_count=target_word_count // len(sections)
            )
            
            full_content.append(section_content['content'])
            section_results.append({
                'section': section.get('name'),
                'content': section_content['content'],
                'word_count': section_content['word_count'],
                'quality_score': section_content.get('quality_score', 0)
            })
        
        # 组合全文
        full_text = '\n\n'.join(full_content)
        
        return {
            'title': outline.get('title', ''),
            'style': style,
            'content': full_text,
            'sections': section_results,
            'total_word_count': len(full_text),
            'target_word_count': target_word_count,
            'completion_rate': len(full_text) / target_word_count if target_word_count > 0 else 0,
            'written_at': datetime.now().isoformat(),
            'model_used': 'deepseek-chat-v3'
        }
    
    def _write_section(self, title: str, section: Dict, style: str,
                       facts: List[Dict], word_count: int) -> Dict[str, Any]:
        """撰写单节内容"""
        
        facts_str = '\n'.join([f"- {f.get('title', f.get('content', ''))}" for f in (facts or [])])
        
        prompt = f"""你是一位专业的内容创作者，擅长{style}风格写作。

【文章标题】
{title}

【当前小节】
{section.get('name', '未知')}

【写作方向】
{section.get('guidance', '自由发挥')}

【需要引用的事实】
{facts_str if facts_str else '无特定要求，可自由发挥'}

【字数要求】
约{word_count}字

【{style}风格特点】
- 语调：保持{style}风格
- 特点：语言流畅，逻辑清晰
- 要求：避免 AI 套话（如"综上所述"、"在这个信息爆炸的时代"）

请撰写这一小节的内容。要求:
1. 紧扣写作方向
2. 适当引用提供的事实
3. 语言生动，有感染力
4. 如果有金句更好

直接输出正文内容，不要其他说明:"""
        
        try:
            content = self.client._call_llm(prompt)
            
            # 简单质量评估
            quality_score = self._quick_quality_check(content, word_count)
            
            return {
                'content': content.strip(),
                'word_count': len(content),
                'quality_score': quality_score
            }
            
        except Exception as e:
            return {
                'content': f"[撰写失败：{e}]",
                'word_count': 0,
                'quality_score': 0,
                'error': str(e)
            }
    
    def _extract_relevant_facts(self, facts: List[Dict], section: Dict) -> List[Dict]:
        """提取相关事实"""
        if not facts:
            return []
        
        # 简单关键词匹配
        section_name = section.get('name', '').lower()
        section_guidance = section.get('guidance', '').lower()
        
        relevant = []
        for fact in facts:
            fact_title = fact.get('title', '').lower()
            fact_content = fact.get('content', '').lower()
            
            # 简单匹配
            if any(keyword in fact_title or keyword in fact_content 
                   for keyword in [section_name] + section_guidance.split()):
                relevant.append(fact)
        
        # 如果没有匹配，返回前 3 个
        return relevant[:3] if relevant else facts[:3]
    
    def _quick_quality_check(self, content: str, target_word_count: int) -> float:
        """快速质量检查"""
        score = 50.0
        
        # 字数检查 (±20%)
        actual = len(content)
        if 0.8 * target_word_count <= actual <= 1.2 * target_word_count:
            score += 20
        elif 0.6 * target_word_count <= actual <= 1.4 * target_word_count:
            score += 10
        
        # 段落检查
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 3:
            score += 15
        
        # 有引用
        if '据' in content or '表示' in content or '显示' in content:
            score += 15
        
        # 无 AI 套话
        ai_cliches = ['综上所述', '在这个信息爆炸的时代', '总而言之', '总的来说']
        if not any(cliche in content for cliche in ai_cliches):
            score += 10
        
        return min(score, 100)
    
    def write_from_topic(self, topic: Dict[str, Any], outline: Dict[str, Any],
                         facts: List[Dict] = None) -> Dict[str, Any]:
        """
        从选题直接撰写
        
        Args:
            topic: 选题数据
            outline: 大纲数据
            facts: 事实包
        
        Returns:
            文章初稿
        """
        style = topic.get('style', '新闻报道')
        
        return self.write(outline, style, facts)


# 使用示例
if __name__ == '__main__':
    writer = DraftWriter(model='v3')
    
    # 测试大纲
    test_outline = {
        'title': 'AI 教育正在改变未来',
        'style': '商业分析',
        'target_word_count': 1500,
        'sections': [
            {'name': '开篇：AI 教育的崛起', 'guidance': '描述现状和趋势'},
            {'name': '核心应用：智能辅导系统', 'guidance': '介绍主要应用场景'},
            {'name': '挑战与机遇', 'guidance': '分析面临的挑战'},
            {'name': '未来展望', 'guidance': '预测发展方向'}
        ]
    }
    
    # 测试事实
    test_facts = [
        {'title': '教育部数据', 'content': '2025 年 AI 教育市场规模达 1000 亿'},
        {'title': '专家观点', 'content': '李教授：AI 将重塑教育生态'}
    ]
    
    # 撰写
    draft = writer.write(test_outline, style='商业分析', facts=test_facts)
    
    print(f"\n标题：{draft['title']}")
    print(f"字数：{draft['total_word_count']} / {draft['target_word_count']}")
    print(f"完成率：{draft['completion_rate']*100:.1f}%")
    print(f"\n正文预览:\n{draft['content'][:500]}...")
