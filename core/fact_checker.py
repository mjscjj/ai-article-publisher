#!/usr/bin/env python3
"""
【事实核查器】Fact Checker
验证文章中的事实准确性，识别虚假信息

功能:
1. 事实提取 - 从文章中提取可验证的陈述
2. 交叉验证 - 与多个数据源对比
3. 可信度评分 - 评估事实可靠性
4. 风险标记 - 标记潜在虚假信息
"""

import os
import sys
import re
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

class FactChecker:
    """事实核查器"""
    
    def __init__(self):
        # 可信数据源
        self.trusted_sources = {
            'gov': ['教育部', '国务院', '发改委', '科技部'],
            'media': ['新华社', '人民日报', '央视新闻', '澎湃新闻', '财新'],
            'academic': ['Nature', 'Science', 'arXiv', '知网']
        }
        
        # 可疑模式
        self.suspicious_patterns = [
            r'据说', r'听说', r'网传', r'爆料', r'内部消息',
            r'震惊', r'重磅', r'刚刚', r'突发',
            r'100%', r'绝对', r'肯定', r'一定'
        ]
    
    def check_article(self, content: str, 
                     reference_data: List[Dict] = None) -> Dict[str, Any]:
        """
        核查文章
        
        Args:
            content: 文章内容
            reference_data: 参考数据 (用于交叉验证)
        
        Returns:
            核查报告
        """
        # 1. 提取事实陈述
        facts = self._extract_facts(content)
        
        # 2. 核查每个事实
        fact_checks = []
        for fact in facts:
            check_result = self._check_single_fact(fact, reference_data)
            fact_checks.append(check_result)
        
        # 3. 检测可疑模式
        suspicious = self._detect_suspicious_patterns(content)
        
        # 4. 生成报告
        report = {
            'total_facts': len(facts),
            'verified_facts': sum(1 for f in fact_checks if f['status'] == 'verified'),
            'unverified_facts': sum(1 for f in fact_checks if f['status'] == 'unverified'),
            'suspicious_claims': len(suspicious),
            'fact_checks': fact_checks,
            'suspicious_patterns': suspicious,
            'overall_credibility': self._calculate_overall_credibility(fact_checks, suspicious),
            'recommendations': self._generate_recommendations(fact_checks, suspicious)
        }
        
        return report
    
    def _extract_facts(self, content: str) -> List[str]:
        """提取事实陈述"""
        facts = []
        
        # 提取包含数据的句子
        data_pattern = r'[^。]*\d+[^。]*。'
        data_sentences = re.findall(data_pattern, content)
        facts.extend([s.strip() for s in data_sentences[:10]])
        
        # 提取引用
        quote_pattern = r'[""][^""]{10,100}[""]'
        quotes = re.findall(quote_pattern, content)
        facts.extend([q.strip() for q in quotes[:5]])
        
        # 提取明确陈述
        statement_patterns = [
            r'[^。]*表明[^。]*。',
            r'[^。]*显示[^。]*。',
            r'[^。]*指出[^。]*。',
            r'[^。]*发现[^。]*。'
        ]
        
        for pattern in statement_patterns:
            statements = re.findall(pattern, content)
            facts.extend([s.strip() for s in statements[:5]])
        
        # 去重
        unique_facts = list(dict.fromkeys(facts))
        
        return unique_facts[:20]
    
    def _check_single_fact(self, fact: str, 
                          reference_data: List[Dict] = None) -> Dict[str, Any]:
        """核查单个事实"""
        result = {
            'fact': fact,
            'status': 'unverified',  # verified / unverified / disputed / false
            'confidence': 0.5,
            'sources': [],
            'notes': ''
        }
        
        # 1. 检查是否有数据支撑
        has_data = bool(re.search(r'\d+', fact))
        if has_data:
            result['confidence'] += 0.1
        
        # 2. 检查来源
        for category, sources in self.trusted_sources.items():
            for source in sources:
                if source in fact:
                    result['status'] = 'verified'
                    result['confidence'] += 0.3
                    result['sources'].append(source)
                    result['notes'] = f'来自可信{category}来源'
        
        # 3. 与参考数据交叉验证
        if reference_data:
            for ref in reference_data:
                ref_title = ref.get('title', '')
                # 简单相似度检查
                if self._text_similarity(fact, ref_title) > 0.6:
                    result['status'] = 'verified'
                    result['confidence'] += 0.2
                    result['sources'].append(ref.get('source', 'Unknown'))
        
        # 4. 检查可疑模式
        for pattern in self.suspicious_patterns:
            if re.search(pattern, fact, re.I):
                result['confidence'] -= 0.2
                if result['status'] == 'verified':
                    result['status'] = 'disputed'
        
        # 确保置信度在 0-1 之间
        result['confidence'] = max(0, min(1, result['confidence']))
        
        return result
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """简单文本相似度"""
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / max(union, 1)
    
    def _detect_suspicious_patterns(self, content: str) -> List[Dict]:
        """检测可疑模式"""
        suspicious = []
        
        for pattern in self.suspicious_patterns:
            matches = re.finditer(pattern, content, re.I)
            for match in matches:
                suspicious.append({
                    'pattern': pattern,
                    'text': match.group(),
                    'position': match.start(),
                    'severity': 'high' if pattern in ['100%', '绝对', '肯定'] else 'medium'
                })
        
        return suspicious
    
    def _calculate_overall_credibility(self, fact_checks: List[Dict], 
                                       suspicious: List[Dict]) -> str:
        """计算整体可信度"""
        if not fact_checks:
            return 'unknown'
        
        # 平均置信度
        avg_confidence = sum(f['confidence'] for f in fact_checks) / len(fact_checks)
        
        # 已验证比例
        verified_ratio = sum(1 for f in fact_checks if f['status'] == 'verified') / len(fact_checks)
        
        # 可疑模式惩罚
        suspicious_penalty = len(suspicious) * 0.05
        
        # 综合评分
        score = (avg_confidence * 0.5 + verified_ratio * 0.5) - suspicious_penalty
        
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        elif score >= 0.4:
            return 'low'
        else:
            return 'very_low'
    
    def _generate_recommendations(self, fact_checks: List[Dict], 
                                  suspicious: List[Dict]) -> List[str]:
        """生成改进建议"""
        recs = []
        
        # 未验证事实过多
        unverified = sum(1 for f in fact_checks if f['status'] == 'unverified')
        if unverified > len(fact_checks) * 0.5:
            recs.append(f"⚠️ {unverified} 个事实未经验证，建议添加可靠来源")
        
        # 可疑模式
        if len(suspicious) > 3:
            recs.append(f"⚠️ 发现 {len(suspicious)} 处可疑表述，建议修改绝对化语言")
        
        # 低置信度
        low_conf = [f for f in fact_checks if f['confidence'] < 0.5]
        if low_conf:
            recs.append(f"⚠️ {len(low_conf)} 个事实置信度低，建议核实")
        
        # 无问题
        if not recs:
            recs.append("✅ 事实核查通过，可信度良好")
        
        return recs


def test_fact_checker():
    """测试"""
    print("\n" + "="*70)
    print("✅ 事实核查器测试")
    print("="*70 + "\n")
    
    checker = FactChecker()
    
    # 测试文章
    test_article = """
    教育部最新发布数据显示，60% 的高校已开设 AI 相关课程。
    新华社报道，人工智能市场规模将在 2025 年达到 1000 亿元。
    据说有内部消息表明，某大厂即将裁员 50%。
    专家指出，AI 将取代 80% 的工作岗位。
    澎湃新闻采访发现，教师群体对 AI 态度分化严重。
    """
    
    # 参考数据
    reference_data = [
        {'title': '教育部：60% 高校开设 AI 课程', 'source': '教育部官网'},
        {'title': '人工智能市场规模突破千亿', 'source': '新华社'},
        {'title': 'AI 对就业市场的影响研究', 'source': 'Nature'}
    ]
    
    print("测试文章:")
    print(test_article)
    print("\n" + "="*70 + "\n")
    
    # 核查
    report = checker.check_article(test_article, reference_data)
    
    print("📊 核查报告")
    print(f"  总事实数：{report['total_facts']}")
    print(f"  已验证：{report['verified_facts']}")
    print(f"  未验证：{report['unverified_facts']}")
    print(f"  可疑表述：{report['suspicious_claims']}")
    print(f"  整体可信度：{report['overall_credibility']}")
    
    print(f"\n📋 事实核查详情:")
    for i, fc in enumerate(report['fact_checks'][:5], 1):
        status_icon = {'verified': '✅', 'unverified': '❓', 'disputed': '⚠️', 'false': '❌'}
        icon = status_icon.get(fc['status'], '❓')
        print(f"  {i}. {icon} {fc['fact'][:50]}...")
        print(f"     状态：{fc['status']} | 置信度：{fc['confidence']:.2f}")
    
    print(f"\n💡 改进建议:")
    for rec in report['recommendations']:
        print(f"  {rec}")
    
    print("\n" + "="*70)
    print("🎉 事实核查测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_fact_checker()
