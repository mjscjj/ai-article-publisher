#!/usr/bin/env python3
"""
【切入角生成器】Angle Generator - 规则增强版
基于规则和模板生成切入角，不依赖 LLM（降级方案）
"""

import random
from typing import Dict, List, Any

class AngleGeneratorLite:
    """轻量级切入角生成器（规则驱动）"""
    
    def __init__(self):
        self.templates = {
            "conflict": [
                "{topic}：{group_a}说{view_a}，{group_b}却{view_b}",
                "{topic}的真相：{a}与{b}的正面交锋",
                "当{topic}来临，{group_a}在狂欢，{group_b}在哭泣"
            ],
            "contrast": [
                "你以为{topic}是{expectation}？其实是{reality}",
                "{topic}：表面{surface}，背后{truth}",
                "都说{topic}会{common_belief}，现实却给了所有人一记耳光"
            ],
            "suspense": [
                "为什么{phenomenon}？{topic}背后的真相让人意外",
                "{topic}正在{action}，但很少有人问为什么",
                "{number}%的人不知道，{topic}其实{surprising_fact}"
            ],
            "human": [
                "一个{role}的{time}：{topic}如何改变了 ta 的生活",
                "{topic}之下，{group}的真实生存图景",
                "我采访了{number}个{role}，发现{topic}的残酷真相"
            ],
            "data": [
                "{number}%的{target}{action}：{topic}的数据真相",
                "{topic}市场规模达{number}亿，但{contrast_data}",
                "数据揭示{topic}：{statistic}的人正在{action}"
            ],
            "trend": [
                "{topic}：{year}年后，{prediction}",
                "未来{year}年，{topic}将{trend_action}，{consequence}",
                "当我们在谈论{topic}时，{future_scenario}正在发生"
            ],
            "reveal": [
                "{topic}的{number}个潜规则，第{random}个最致命",
                "没人告诉你的{topic}真相：{revealed_fact}",
                "{topic}行业内幕：{insider_secret}"
            ],
            "compare": [
                "{a}用{topic}{action_a}，{b}却{action_b}",
                "{time_a}的{topic}{compare_word}{time_b}，变化令人唏嘘",
                "同样是{topic}，{group_a}和{group_b}的差距有多大？"
            ]
        }
        
        self.fill_data = {
            "group_a": ["专家", "资本", "大厂", "精英", "先行者"],
            "group_b": ["大众", "打工人", "小厂", "普通人", "后来者"],
            "role": ["程序员", "教师", "学生", "创业者", "中层管理者"],
            "time": ["72 小时", "30 天", "一年", "关键时刻"],
            "year": ["3", "5", "10"],
            "number": ["60", "80", "90", "50"],
            "random": ["3", "5", "7"]
        }
    
    def generate_angles(self, topic: str, facts: List[str]) -> List[Dict[str, Any]]:
        """生成切入角"""
        angles = []
        
        for angle_type, templates in self.templates.items():
            template = random.choice(templates)
            title = self._fill_template(template, topic, facts)
            
            angle = {
                "type": angle_type,
                "type_name": self._get_type_name(angle_type),
                "title": title,
                "core_viewpoint": self._generate_viewpoint(angle_type, topic, facts),
                "opening_hook": self._generate_hook(angle_type, topic, facts),
                "supporting_facts": facts[:3],
                "score": random.randint(70, 90)
            }
            angles.append(angle)
        
        angles.sort(key=lambda x: x['score'], reverse=True)
        return angles
    
    def _fill_template(self, template: str, topic: str, facts: List[str]) -> str:
        """填充模板"""
        result = template
        
        # 替换通用占位符
        replacements = {
            "{topic}": topic,
            "{group_a}": random.choice(self.fill_data["group_a"]),
            "{group_b}": random.choice(self.fill_data["group_b"]),
            "{role}": random.choice(self.fill_data["role"]),
            "{time}": random.choice(self.fill_data["time"]),
            "{year}": random.choice(self.fill_data["year"]),
            "{number}": random.choice(self.fill_data["number"]),
            "{random}": random.choice(self.fill_data["random"]),
        }
        
        for key, value in replacements.items():
            result = result.replace(key, value)
        
        # 基于事实填充
        fill_map = {
            "{action}": "正在改变一切",
            "{expectation}": "机遇",
            "{reality}": "挑战",
            "{surface}": "风光",
            "{truth}": "焦虑",
            "{surprising_fact}": "是一场零和博弈",
            "{contrast_data}": "真正受益的不到 10%",
            "{trend_action}": "淘汰一半传统岗位",
            "{consequence}": "你准备好了吗？",
            "{revealed_fact}": "90% 的培训都是割韭菜",
            "{insider_secret}": "头部玩家早已布局完毕",
            "{compare_word}": "对比",
            "{statistic}": "超过 80%",
            "{future_scenario}": "教育资源的重新洗牌"
        }
        for key, value in fill_map.items():
            result = result.replace(key, value)
        
        return result[:50]  # 限制长度
    
    def _get_type_name(self, angle_type: str) -> str:
        names = {
            "conflict": "冲突型",
            "contrast": "反差型",
            "suspense": "悬念型",
            "human": "人物型",
            "data": "数据型",
            "trend": "趋势型",
            "reveal": "揭秘型",
            "compare": "对比型"
        }
        return names.get(angle_type, angle_type)
    
    def _generate_viewpoint(self, angle_type: str, topic: str, facts: List[str]) -> str:
        """生成核心观点"""
        viewpoints = {
            "conflict": f"{topic}的核心矛盾在于利益分配不均",
            "contrast": f"{topic}的表象与真相存在巨大落差",
            "suspense": f"{topic}背后有未被察觉的深层逻辑",
            "human": f"{topic}最终影响的是每个具体的人",
            "data": f"数据揭示{topic}的真实规模被低估",
            "trend": f"{topic}将重塑未来 3-5 年的行业格局",
            "reveal": f"{topic}存在鲜为人知的行业潜规则",
            "compare": f"不同群体在{topic}中的处境天差地别"
        }
        return viewpoints.get(angle_type, f"深度解读{topic}")
    
    def _generate_hook(self, angle_type: str, topic: str, facts: List[str]) -> str:
        """生成开篇钩子"""
        hooks = {
            "conflict": f"想象一下，一边是{topic}的狂热追捧，一边是无声的抗议...",
            "contrast": f"表面上看，{topic}是一片繁荣，但真相可能让你意外...",
            "suspense": f"为什么越来越多的人开始质疑{topic}？...",
            "human": f"凌晨 3 点，李明还在电脑前挣扎，他是数百万被{topic}影响的人之一...",
            "data": f"一个惊人的数字：{random.choice(['60%', '80%', '90%'])}的人对{topic}存在误解...",
            "trend": f"站在 2026 年回望，{topic}的转折点已经悄然来临...",
            "reveal": f"很少有人知道，{topic}背后隐藏着一个巨大的秘密...",
            "compare": f"同样的{topic}，在不同人手中却是完全不同的命运..."
        }
        return hooks.get(angle_type, f"让我们从{topic}说起...")[:60]
    
    def recommend_best(self, angles: List[Dict], target_audience: str = "general") -> Dict:
        """推荐最佳切入角"""
        if not angles:
            return None
        
        weights = {
            "general": {"data": 1.2, "human": 1.3, "conflict": 1.1},
            "professional": {"data": 1.3, "trend": 1.2, "reveal": 1.1},
            "youth": {"conflict": 1.3, "contrast": 1.2, "human": 1.1}
        }
        
        audience_weights = weights.get(target_audience, weights["general"])
        
        for angle in angles:
            bonus = audience_weights.get(angle['type'], 1.0)
            angle['adjusted_score'] = angle.get('score', 60) * bonus
        
        angles.sort(key=lambda x: x.get('adjusted_score', 0), reverse=True)
        return angles[0]


def test_angle_generator_lite():
    """测试"""
    gen = AngleGeneratorLite()
    
    topic = "人工智能对教育的冲击"
    facts = [
        "教育部发布 AI+ 教育指导意见",
        "60% 高校已开设 AI 相关课程",
        "教师担心被 AI 取代",
        "学生用 AI 写作业成常态",
        "AI 教育市场规模达 1000 亿"
    ]
    
    print(f"\n{'='*70}")
    print(f"📐 切入角生成测试（规则版）：{topic}")
    print(f"{'='*70}\n")
    
    angles = gen.generate_angles(topic, facts)
    
    print(f"生成 {len(angles)} 个切入角:\n")
    
    for i, angle in enumerate(angles[:5], 1):
        print(f"{i}. [{angle['type_name']}] {angle['title']}")
        print(f"   核心观点：{angle['core_viewpoint']}")
        print(f"   开篇建议：{angle['opening_hook']}")
        print(f"   评分：{angle.get('score', 'N/A')}\n")
    
    # 推荐最佳
    best = gen.recommend_best(angles, "general")
    if best:
        print(f"🏆 推荐最佳 (大众受众): {best['title']}")
        print(f"   调整后评分：{best.get('adjusted_score', 0):.1f}")


if __name__ == "__main__":
    test_angle_generator_lite()
