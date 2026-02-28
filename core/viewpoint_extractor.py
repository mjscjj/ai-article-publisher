#!/usr/bin/env python3
"""
【核心观点提炼器】Viewpoint Extractor
从话题和事实中提炼出尖锐、有传播力的核心观点

观点类型:
1. 判断型 - 直接下结论 (X 的本质是 Y)
2. 警示型 - 发出警告 (小心 X 带来的 Y)
3. 颠覆型 - 颠覆常识 (你以为 X，其实 Y)
4. 洞察型 - 深度洞察 (X 背后是 Y 的博弈)
5. 预测型 - 未来预测 (X 将导致 Y)
6. 方法型 - 给出方法 (面对 X，应该 Y)
"""

import random
from typing import Dict, List, Any

class ViewpointExtractor:
    """核心观点提炼器"""
    
    def __init__(self):
        self.templates = {
            "judgment": [
                "{topic}的本质，不是{surface}，而是{deep}",
                "{topic}看似是{a}问题，其实是{b}问题",
                "所有{topic}的争论，归根结底都是{core}",
                "{topic}，是一场关于{core}的博弈"
            ],
            "warning": [
                "当所有人都在{action}时，很少有人警惕{topic}的{risk}",
                "{topic}的最大风险，不是{risk_a}，而是{risk_b}",
                "盲目追逐{topic}的人，正在付出{cost}的代价",
                "小心！{topic}正在{danger}"
            ],
            "subvert": [
                "你以为{topic}是{expectation}？其实是{reality}",
                "{topic}最大的谎言，就是{lie}",
                "关于{topic}，{group}不会告诉你的真相是{truth}",
                "别再被{topic}的{illusion}欺骗了，真相是{truth}"
            ],
            "insight": [
                "{topic}背后，是{a}与{b}的无声较量",
                "看懂{topic}，就看懂了{insight}",
                "{topic}的底层逻辑，是{logic}",
                "{topic}撕开了{phenomenon}的遮羞布"
            ],
            "prediction": [
                "{time}后，{topic}将{prediction}",
                "当{topic}成为常态，{consequence}",
                "{topic}的终局，是{ending}",
                "未来属于{topic}的人，但{condition}"
            ],
            "method": [
                "面对{topic}，普通人最好的策略是{method}",
                "在{topic}时代，{action}才是核心竞争力",
                "想要{goal}？先理解{topic}的{key}",
                "{topic}浪潮下，{group}应该{action}"
            ]
        }
        
        self.fill_data = {
            "surface": ["技术问题", "效率提升", "工具升级", "产业升级"],
            "deep": ["利益重新分配", "权力重构", "认知战争", "生存焦虑"],
            "a": ["技术", "产品", "商业"],
            "b": ["人性", "政治", "社会"],
            "core": ["资源争夺", "话语权", "生存空间", "认知差"],
            "action": ["追捧", "投入", "学习", "布局"],
            "risk": ["副作用", "长期代价", "系统性风险"],
            "risk_a": ["技术不成熟", "成本太高"],
            "risk_b": ["认知被操控", "选择权丧失"],
            "cost": ["巨大", "惨重", "不可逆"],
            "danger": ["改变游戏规则", "重塑权力结构"],
            "expectation": ["机遇", "福音", "进步"],
            "reality": ["挑战", "陷阱", "零和博弈"],
            "lie": ["人人受益", "技术中立", "普惠大众"],
            "truth": ["头部通吃", "加剧分化", "重新洗牌"],
            "group": ["既得利益者", "平台", "资本"],
            "illusion": ["繁荣", "普惠", "民主化"],
            "time": ["3 年", "5 年", "10 年"],
            "prediction": ["淘汰一半从业者", "重塑行业格局", "创造新阶级"],
            "consequence": ["社会结构将发生剧变", "贫富差距会进一步扩大"],
            "ending": ["少数人的狂欢", "多数人的觉醒"],
            "condition": ["前提是你能活到那天"],
            "method": ["保持认知敏感", "建立护城河", "快速试错"],
            "goal": ["不被淘汰", "抓住机会", "实现跃迁"],
            "key": ["底层逻辑", "核心规律", "第一性原理"]
        }
    
    def extract_viewpoints(self, topic: str, facts: List[str], 
                           angle_type: str = None) -> List[Dict[str, Any]]:
        """
        提炼核心观点
        
        angle_type: 可选，与切入角类型匹配
        """
        viewpoints = []
        
        # 根据切入角类型选择观点模板
        type_map = {
            "conflict": ["judgment", "insight"],
            "contrast": ["subvert", "insight"],
            "suspense": ["insight", "warning"],
            "human": ["warning", "method"],
            "data": ["judgment", "prediction"],
            "trend": ["prediction", "insight"],
            "reveal": ["subvert", "warning"],
            "compare": ["judgment", "insight"]
        }
        
        selected_types = type_map.get(angle_type, list(self.templates.keys()))[:3]
        
        for vp_type in selected_types:
            templates = self.templates[vp_type]
            template = random.choice(templates)
            viewpoint = self._fill_template(template, topic, facts)
            
            viewpoints.append({
                "type": vp_type,
                "type_name": self._get_type_name(vp_type),
                "content": viewpoint,
                "intensity": random.randint(7, 10),
                "spreadability": random.randint(7, 10)
            })
        
        # 按强度排序
        viewpoints.sort(key=lambda x: x['intensity'], reverse=True)
        return viewpoints
    
    def _fill_template(self, template: str, topic: str, facts: List[str]) -> str:
        """填充模板"""
        result = template
        
        # 通用替换
        result = result.replace("{topic}", topic)
        
        # 随机填充
        for key, values in self.fill_data.items():
            if isinstance(values[0], list):
                value = random.choice(random.choice(values))
            else:
                value = random.choice(values)
            result = result.replace(f"{{{key}}}", value)
        
        # 基于事实的填充
        if facts:
            result = result.replace("{phenomenon}", facts[0][:20] if facts[0] else "行业现象")
        
        return result[:80]  # 限制长度
    
    def _get_type_name(self, vp_type: str) -> str:
        names = {
            "judgment": "判断型",
            "warning": "警示型",
            "subvert": "颠覆型",
            "insight": "洞察型",
            "prediction": "预测型",
            "method": "方法型"
        }
        return names.get(vp_type, vp_type)
    
    def generate_golden_sentence(self, viewpoint: str) -> str:
        """基于观点生成金句"""
        patterns = [
            "记住：{viewpoint}",
            "一句话：{viewpoint}",
            "真相就是：{viewpoint}",
            "{viewpoint}——这才是{topic}的真相"
        ]
        return random.choice(patterns)
    
    def recommend_best(self, viewpoints: List[Dict]) -> Dict:
        """推荐最佳观点"""
        if not viewpoints:
            return None
        
        # 综合评分
        for vp in viewpoints:
            vp['total_score'] = vp['intensity'] * 0.6 + vp['spreadability'] * 0.4
        
        viewpoints.sort(key=lambda x: x['total_score'], reverse=True)
        return viewpoints[0]


def test_viewpoint_extractor():
    """测试"""
    ext = ViewpointExtractor()
    
    topic = "人工智能对教育的冲击"
    facts = [
        "教育部发布 AI+ 教育指导意见",
        "60% 高校已开设 AI 相关课程",
        "教师担心被 AI 取代"
    ]
    
    print(f"\n{'='*70}")
    print(f"💡 核心观点提炼测试：{topic}")
    print(f"{'='*70}\n")
    
    viewpoints = ext.extract_viewpoints(topic, facts, "conflict")
    
    print(f"提炼 {len(viewpoints)} 个核心观点:\n")
    
    for i, vp in enumerate(viewpoints, 1):
        print(f"{i}. [{vp['type_name']}] {vp['content']}")
        print(f"   强度：{vp['intensity']}/10 | 传播力：{vp['spreadability']}/10\n")
    
    # 推荐最佳
    best = ext.recommend_best(viewpoints)
    if best:
        print(f"🏆 推荐最佳：{best['content']}")
        print(f"   综合评分：{best['total_score']:.1f}")
        
        # 生成金句
        golden = ext.generate_golden_sentence(best['content'])
        print(f"\n✨ 金句：{golden}")


if __name__ == "__main__":
    test_viewpoint_extractor()
