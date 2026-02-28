#!/usr/bin/env python3
"""
【文章质量评分器】Article Quality Scorer
多维度评估文章质量，给出改进建议

评分维度:
1. 内容质量 (40%) - 深度、逻辑、事实
2. 结构质量 (25%) - 段落、过渡、节奏
3. 表达质量 (20%) - 语言、文风、金句
4. 传播潜力 (15%) - 标题、开篇、话题性
"""

import os
import sys
import re
from typing import Dict, List, Any
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

class ArticleScorer:
    """文章质量评分器"""
    
    def __init__(self):
        # AI 套话列表
        self.ai_cliches = [
            "在这个信息爆炸的时代", "随着科技的发展", "不可否认",
            "综上所述", "总而言之", "在这个充满挑战", "我们需要共同努力",
            "让我们携手", "展望未来", "具有重要意义", "大势所趋"
        ]
        
        # 优质特征
        self.quality_indicators = {
            'data': r'\d+[%亿千万百万]',  # 数据
            'quote': r'[""].*?[""]',  # 引用
            'question': r'？',  # 疑问句
            'contrast': r'但是 | 然而 | 却|其实',  # 转折
            'example': r'例如 | 比如|如'  # 举例
        }
    
    def score_article(self, content: str, title: str = "") -> Dict[str, Any]:
        """
        评分文章
        
        Args:
            content: 文章内容
            title: 文章标题
        
        Returns:
            评分报告
        """
        # 1. 内容质量 (40 分)
        content_score = self._score_content(content)
        
        # 2. 结构质量 (25 分)
        structure_score = self._score_structure(content)
        
        # 3. 表达质量 (20 分)
        expression_score = self._score_expression(content)
        
        # 4. 传播潜力 (15 分)
        viral_score = self._score_viral_potential(content, title)
        
        # 总分
        total_score = (
            content_score['score'] * 0.40 +
            structure_score['score'] * 0.25 +
            expression_score['score'] * 0.20 +
            viral_score['score'] * 0.15
        )
        
        # 等级
        if total_score >= 85:
            grade = 'S'
            comment = "🏆 爆款潜质"
        elif total_score >= 75:
            grade = 'A'
            comment = "✅ 优质文章"
        elif total_score >= 60:
            grade = 'B'
            comment = "👌 合格作品"
        elif total_score >= 40:
            grade = 'C'
            comment = "⚠️ 需要改进"
        else:
            grade = 'D'
            comment = "❌ 质量较差"
        
        return {
            'total_score': round(total_score, 1),
            'grade': grade,
            'comment': comment,
            'dimensions': {
                'content': content_score,
                'structure': structure_score,
                'expression': expression_score,
                'viral': viral_score
            },
            'recommendations': self._generate_recommendations(
                content_score, structure_score, expression_score, viral_score
            ),
            'stats': self._get_stats(content, title)
        }
    
    def _score_content(self, content: str) -> Dict[str, Any]:
        """内容质量评分"""
        score = 50  # 基础分
        details = []
        
        # 字数 (目标 1500-3000)
        char_count = len(content)
        if 1500 <= char_count <= 3000:
            score += 15
            details.append("✅ 字数适中")
        elif 1000 <= char_count < 1500 or 3000 < char_count <= 4000:
            score += 8
            details.append("⚠️ 字数偏" + ("少" if char_count < 1500 else "多"))
        else:
            details.append("❌ 字数不合理")
        
        # 数据密度
        data_count = len(re.findall(self.quality_indicators['data'], content))
        data_density = data_count / max(char_count / 1000, 1)
        if data_density >= 15:
            score += 15
            details.append(f"✅ 数据丰富 ({data_count}个)")
        elif data_density >= 8:
            score += 8
            details.append(f"👌 数据适中 ({data_count}个)")
        else:
            details.append(f"⚠️ 数据不足 ({data_count}个)")
        
        # AI 套话检测
        cliche_count = sum(1 for c in self.ai_cliches if c in content)
        if cliche_count == 0:
            score += 10
            details.append("✅ 无 AI 套话")
        elif cliche_count <= 2:
            score -= 5
            details.append(f"⚠️ {cliche_count}处 AI 套话")
        else:
            score -= 15
            details.append(f"❌ {cliche_count}处 AI 套话")
        
        return {
            'score': max(0, min(100, score)),
            'details': details,
            'char_count': char_count,
            'data_count': data_count,
            'cliche_count': cliche_count
        }
    
    def _score_structure(self, content: str) -> Dict[str, Any]:
        """结构质量评分"""
        score = 50
        details = []
        
        # 段落数
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        para_count = len(paragraphs)
        
        if 8 <= para_count <= 20:
            score += 15
            details.append(f"✅ 段落合理 ({para_count}段)")
        elif 5 <= para_count < 8 or 20 < para_count <= 30:
            score += 8
            details.append(f"👌 段落数尚可 ({para_count}段)")
        else:
            details.append(f"⚠️ 段落不合理 ({para_count}段)")
        
        # 小标题
        headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.M)
        if 2 <= len(headings) <= 6:
            score += 15
            details.append(f"✅ 有小标题 ({len(headings)}个)")
        elif len(headings) == 1:
            score += 5
            details.append("👌 有小标题")
        else:
            details.append("⚠️ 缺少小标题")
        
        # 平均段落长度
        if paragraphs:
            avg_para_len = sum(len(p) for p in paragraphs) / len(paragraphs)
            if 100 <= avg_para_len <= 300:
                score += 10
                details.append("✅ 段落长度适中")
            else:
                details.append("⚠️ 段落长度不均")
        
        return {
            'score': max(0, min(100, score)),
            'details': details,
            'paragraph_count': para_count,
            'heading_count': len(headings)
        }
    
    def _score_expression(self, content: str) -> Dict[str, Any]:
        """表达质量评分"""
        score = 50
        details = []
        
        # 引用数量
        quotes = re.findall(self.quality_indicators['quote'], content)
        if len(quotes) >= 5:
            score += 10
            details.append(f"✅ 引用丰富 ({len(quotes)}个)")
        elif len(quotes) >= 2:
            score += 5
            details.append(f"👌 有引用 ({len(quotes)}个)")
        else:
            details.append("⚠️ 缺少引用")
        
        # 金句 (短句且有力度)
        sentences = re.split(r'[。！？]', content)
        punchy = [s for s in sentences if 15 <= len(s) <= 40 and len(s.strip()) > 0]
        if len(punchy) >= 5:
            score += 10
            details.append(f"✅ 有金句潜质")
        else:
            details.append("👌 表达平稳")
        
        return {
            'score': max(0, min(100, score)),
            'details': details,
            'quote_count': len(quotes)
        }
    
    def _score_viral_potential(self, content: str, title: str) -> Dict[str, Any]:
        """传播潜力评分"""
        score = 50
        details = []
        
        # 标题质量
        if title:
            if 15 <= len(title) <= 30:
                score += 10
                details.append("✅ 标题长度适中")
            else:
                details.append("⚠️ 标题长度不佳")
            
            # 标题是否有吸引力
            if any(kw in title for kw in ['如何', '为什么', '真相', '揭秘', '重磅']):
                score += 10
                details.append("✅ 标题有吸引力")
        else:
            details.append("⚠️ 无标题")
        
        # 开篇钩子
        first_para = content.split('\n\n')[0] if '\n\n' in content else content[:200]
        if len(first_para) <= 100 and ('？' in first_para or len(first_para) < 80):
            score += 10
            details.append("✅ 开篇简洁")
        else:
            details.append("👌 开篇常规")
        
        # 话题性
        hot_topics = ['AI', '人工智能', '教育', '就业', '赚钱', '未来']
        if any(kw in content for kw in hot_topics):
            score += 10
            details.append("✅ 话题热门")
        
        return {
            'score': max(0, min(100, score)),
            'details': details
        }
    
    def _generate_recommendations(self, content: Dict, structure: Dict, 
                                  expression: Dict, viral: Dict) -> List[str]:
        """生成改进建议"""
        recs = []
        
        if content['score'] < 70:
            if content['cliche_count'] > 0:
                recs.append(f"🔧 删除{content['cliche_count']}处 AI 套话")
            if content['data_count'] < 10:
                recs.append("🔧 增加数据支撑")
        
        if structure['score'] < 70:
            if structure['heading_count'] < 2:
                recs.append("🔧 添加小标题")
            if structure['paragraph_count'] < 8:
                recs.append("🔧 拆分段落")
        
        if expression['score'] < 70:
            if expression['quote_count'] < 3:
                recs.append("🔧 增加直接引语")
        
        if viral['score'] < 70:
            recs.append("🔧 优化标题和开篇")
        
        if not recs:
            recs.append("✅ 文章质量良好，无需重大修改")
        
        return recs
    
    def _get_stats(self, content: str, title: str) -> Dict[str, Any]:
        """基础统计"""
        return {
            'char_count': len(content),
            'word_count': len(content) // 2,
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'sentence_count': len(re.split(r'[。！？]', content)),
            'title_length': len(title)
        }


def test_article_scorer():
    """测试"""
    print("\n" + "="*70)
    print("📊 文章质量评分器测试")
    print("="*70 + "\n")
    
    scorer = ArticleScorer()
    
    # 测试文章
    test_article = """
# AI 正在重塑教育

## 现状与触发

本周，教育部发布《人工智能 + 教育》指导意见。

> 人工智能将成为重塑教育格局的关键变量

## 核心矛盾

程序员失业论调再起，但专家李政涛表示：

`AI 不会取代教师，但会重新定义教学`

### 数据支撑

- 2025 年 AI 教育市场规模达 1000 亿
- 60% 高校已开设 AI 相关课程

## 未来走向

当我们在谈论 AI 教育时，我们在谈论什么？

不是技术，而是人的发展。
"""
    
    test_title = "AI 正在重塑教育：60% 高校已开设相关课程"
    
    # 评分
    report = scorer.score_article(test_article, test_title)
    
    print(f"📊 评分报告")
    print(f"\n总分：{report['total_score']}/100")
    print(f"等级：{report['grade']} - {report['comment']}")
    
    print(f"\n📈 维度评分:")
    for dim_name, dim_data in report['dimensions'].items():
        dim_labels = {'content': '内容', 'structure': '结构', 'expression': '表达', 'viral': '传播'}
        print(f"  {dim_labels.get(dim_name, dim_name)}: {dim_data['score']}/100")
        for detail in dim_data['details'][:3]:
            print(f"    - {detail}")
    
    print(f"\n💡 改进建议:")
    for rec in report['recommendations']:
        print(f"  {rec}")
    
    print(f"\n📋 基础统计:")
    stats = report['stats']
    print(f"  字数：{stats['char_count']}")
    print(f"  段落：{stats['paragraph_count']}")
    print(f"  句子：{stats['sentence_count']}")
    print(f"  标题：{stats['title_length']}字")
    
    print("\n" + "="*70)
    print("🎉 评分测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_article_scorer()
