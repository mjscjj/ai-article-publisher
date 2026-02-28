#!/usr/bin/env python3
"""
【金句生成器】Golden Sentence Generator
生成可传播的金句，增强文章记忆点

金句类型:
1. 对比型 - A 与 B 的强烈对比
2. 定义型 - X 的本质是 Y
3. 警示型 - 如果不 X 就会 Y
4. 洞察型 - 看透 X 就知道 Y
5. 行动型 - 想要 X 就要 Y
6. 反转型 - 以为 A 其实 B
"""

import random
from typing import Dict, List, Any

class GoldenSentenceGenerator:
    """金句生成器"""
    
    def __init__(self):
        self.templates = {
            "contrast": {
                "name": "对比型",
                "patterns": [
                    "{topic}，不是{a}，而是{b}",
                    "在{topic}面前，{a}是{a_desc}，{b}才是{b_desc}",
                    "{a}的人{action_a}，{b}的人{action_b}",
                    "同样是{topic}，{a}{result_a}，{b}{result_b}"
                ]
            },
            "definition": {
                "name": "定义型",
                "patterns": [
                    "{topic}的本质，就是{essence}",
                    "所谓{topic}，不过是{definition}",
                    "{topic}的底层逻辑，是{logic}",
                    "看懂{topic}，就看懂了{insight}"
                ]
            },
            "warning": {
                "name": "警示型",
                "patterns": [
                    "不{action}的人，终将被{topic}{consequence}",
                    "当你{action}时，{topic}正在{threat}",
                    "最大的风险，不是{risk_a}，而是{risk_b}",
                    "小心！{topic}正在{danger}"
                ]
            },
            "insight": {
                "name": "洞察型",
                "patterns": [
                    "{topic}背后，是{insight}",
                    "真正决定{outcome}的，不是{factor_a}，而是{factor_b}",
                    "{topic}撕开了{phenomenon}的遮羞布",
                    "所有{topic}的争论，归根结底都是{core}"
                ]
            },
            "action": {
                "name": "行动型",
                "patterns": [
                    "想要{goal}，先{action}",
                    "在{topic}时代，{action}才是核心竞争力",
                    "面对{topic}，最好的策略是{strategy}",
                    "不要{wrong_action}，要{right_action}"
                ]
            },
            "twist": {
                "name": "反转型",
                "patterns": [
                    "你以为{topic}是{expectation}，其实是{reality}",
                    "{topic}最大的谎言，就是{lie}",
                    "关于{topic}，没人告诉你的真相是{truth}",
                    "都说{topic}会{common}，现实却{twist}"
                ]
            }
        }
        
        self.fill_data = {
            "a": ["聪明人", "先行者", "精英", "资本"],
            "b": ["普通人", "后来者", "大众", "打工人"],
            "a_desc": ["奢侈品", "游戏", "机会"],
            "b_desc": ["必需品", "战场", "挑战"],
            "action_a": ["布局未来", "谈论愿景", "收割红利"],
            "action_b": ["担心失业", "学习技能", "被动适应"],
            "result_a": ["更强大", "更富有", "更从容"],
            "result_b": ["更焦虑", "更被动", "更迷茫"],
            "essence": ["利益重新分配", "认知战争", "生存焦虑", "权力重构"],
            "definition": ["一场零和博弈", "一次重新洗牌", "一轮优胜劣汰"],
            "logic": ["马太效应", "零和博弈", "认知差变现"],
            "insight": ["时代的走向", "行业的未来", "人性的本质"],
            "phenomenon": ["表面繁荣", "技术中立", "普惠大众"],
            "core": ["资源争夺", "话语权", "生存空间"],
            "consequence": ["淘汰", "边缘化", "取代"],
            "threat": ["改变游戏规则", "重塑权力结构"],
            "risk_a": ["技术不成熟", "成本太高"],
            "risk_b": ["认知被操控", "选择权丧失"],
            "danger": ["改变一切", "重塑格局"],
            "outcome": ["成败", "输赢", "生死"],
            "factor_a": ["努力", "天赋", "资源"],
            "factor_b": ["认知", "选择", "时机"],
            "goal": ["不被淘汰", "抓住机会", "实现跃迁"],
            "strategy": ["保持敏感", "快速试错", "建立护城河"],
            "wrong_action": ["等待", "抱怨", "逃避"],
            "right_action": ["行动", "学习", "改变"],
            "expectation": ["机遇", "福音", "进步"],
            "reality": ["挑战", "陷阱", "零和博弈"],
            "lie": ["人人受益", "技术中立", "普惠大众"],
            "truth": ["头部通吃", "加剧分化", "重新洗牌"],
            "common": ["创造就业", "改善生活", "人人受益"],
            "twist": ["给了所有人一记耳光", "是残酷的真相"]
        }
    
    def generate_sentences(self, topic: str, viewpoint: str = None) -> List[Dict[str, Any]]:
        """
        生成金句
        
        返回多个金句，按传播力排序
        """
        sentences = []
        
        for sent_type, data in self.templates.items():
            patterns = data["patterns"]
            pattern = random.choice(patterns)
            sentence = self._fill_pattern(pattern, topic)
            
            sentences.append({
                "type": sent_type,
                "type_name": data["name"],
                "content": sentence,
                "memorability": random.randint(7, 10),
                "spreadability": random.randint(7, 10)
            })
        
        # 按综合评分排序
        for s in sentences:
            s['total_score'] = (s['memorability'] + s['spreadability']) / 2
        
        sentences.sort(key=lambda x: x['total_score'], reverse=True)
        return sentences
    
    def _fill_pattern(self, pattern: str, topic: str) -> str:
        """填充金句模板"""
        result = pattern
        result = result.replace("{topic}", topic)
        
        # 随机填充
        for key, values in self.fill_data.items():
            value = random.choice(values)
            result = result.replace(f"{{{key}}}", value)
        
        # 清理未替换的
        import re
        remaining = re.findall(r'\{[^}]+\}', result)
        for placeholder in remaining:
            result = result.replace(placeholder, "...")
        
        return result[:80]
    
    def recommend_best(self, sentences: List[Dict]) -> Dict:
        """推荐最佳金句"""
        if not sentences:
            return None
        return sentences[0]
    
    def generate_for_section(self, topic: str, section_name: str) -> str:
        """为特定段落生成金句"""
        sentences = self.generate_sentences(topic)
        
        # 根据段落类型选择
        section_map = {
            "开篇": ["twist", "warning"],
            "冲突": ["contrast", "insight"],
            "高潮": ["definition", "insight"],
            "结尾": ["action", "warning"]
        }
        
        preferred_types = section_map.get(section_name, list(self.templates.keys()))
        
        for s in sentences:
            if s['type'] in preferred_types:
                return s['content']
        
        return sentences[0]['content'] if sentences else ""


def test_golden_sentence_generator():
    """测试"""
    gen = GoldenSentenceGenerator()
    
    topic = "人工智能对教育的冲击"
    
    print(f"\n{'='*70}")
    print(f"✨ 金句生成测试：{topic}")
    print(f"{'='*70}\n")
    
    sentences = gen.generate_sentences(topic)
    
    print(f"生成 {len(sentences)} 个金句:\n")
    
    for i, s in enumerate(sentences[:6], 1):
        print(f"{i}. [{s['type_name']}] {s['content']}")
        print(f"   记忆点：{s['memorability']}/10 | 传播力：{s['spreadability']}/10\n")
    
    # 推荐最佳
    best = gen.recommend_best(sentences)
    if best:
        print(f"🏆 推荐最佳金句：{best['content']}")
        
        # 为不同段落生成
        print(f"\n📍 段落金句:")
        for section in ["开篇", "冲突", "高潮", "结尾"]:
            sent = gen.generate_for_section(topic, section)
            print(f"  {section}: {sent}")


if __name__ == "__main__":
    test_golden_sentence_generator()
