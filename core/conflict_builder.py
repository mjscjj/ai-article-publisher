#!/usr/bin/env python3
"""
【冲突构建器】Conflict Builder
为文章构建冲突张力，让叙事更有吸引力

冲突类型:
1. 利益冲突 - 谁受益谁受损
2. 认知冲突 - 不同群体的理解差异
3. 时间冲突 - 短期 vs 长期
4. 价值观冲突 - 效率 vs 公平
5. 身份冲突 - 精英 vs 大众
"""

import random
from typing import Dict, List, Any

class ConflictBuilder:
    """冲突构建器"""
    
    def __init__(self):
        self.conflict_templates = {
            "interest": {
                "name": "利益冲突",
                "description": "谁受益，谁受损",
                "patterns": [
                    "{group_a}在{topic}中{gain}，而{group_b}却在{loss}",
                    "{topic}的本质，是{group_a}对{resource}的重新分配",
                    "当{group_a}庆祝{topic}带来的{benefit}时，{group_b}正在承受{cost}",
                    "同样的{topic}，对{group_a}是{a}，对{group_b}却是{b}"
                ],
                "fill": {
                    "gain": ["大举收割", "抢占先机", "巩固地位"],
                    "loss": ["被动出局", "失去选择权", "被迫转型"],
                    "resource": ["资源", "话语权", "生存空间"],
                    "benefit": ["效率提升", "成本下降", "利润增长"],
                    "cost": ["失业焦虑", "技能贬值", "边缘化"]
                }
            },
            "cognitive": {
                "name": "认知冲突",
                "description": "不同群体的理解差异",
                "patterns": [
                    "{group_a}认为{topic}是{view_a}，{group_b}却认为是{view_b}",
                    "关于{topic}，{group_a}和{group_b}的认知差距比想象中大",
                    "当{group_a}在讨论{topic_a}时，{group_b}关心的是{topic_b}",
                    "同样是{topic}，{group_a}看到{a}，{group_b}看到{b}"
                ],
                "fill": {
                    "view_a": ["技术革新", "历史机遇", "必然趋势"],
                    "view_b": ["生存威胁", "资本游戏", "零和博弈"],
                    "topic_a": ["如何抓住机会", "技术细节", "商业模式"],
                    "topic_b": ["如何活下去", "失业风险", "被替代"]
                }
            },
            "temporal": {
                "name": "时间冲突",
                "description": "短期 vs 长期",
                "patterns": [
                    "短期看，{topic}带来{short_term}；长期看，可能导致{long_term}",
                    "{group_a}追求{topic}的{immediate}，{group_b}担心{future}",
                    "当所有人都在{action_now}时，很少有人思考{action_later}",
                    "{topic}的{short_gain}，可能以{long_cost}为代价"
                ],
                "fill": {
                    "short_term": ["效率提升", "成本下降", "增长加速"],
                    "long_term": ["技能退化", "依赖加深", "系统性风险"],
                    "immediate": ["短期利益", "快速回报", "数据增长"],
                    "future": ["长期代价", "不可逆影响", "结构性问题"]
                }
            },
            "value": {
                "name": "价值观冲突",
                "description": "效率 vs 公平等",
                "patterns": [
                    "{topic}的核心矛盾，是{value_a}与{value_b}的冲突",
                    "当我们在追求{topic}的{value_a}时，是否忽略了{value_b}？",
                    "{group_a}强调{topic}的{value_a}，{group_b}呼吁关注{value_b}",
                    "在{value_a}和{value_b}之间，{topic}选择了前者"
                ],
                "fill": {
                    "value_a": ["效率", "增长", "创新", "竞争"],
                    "value_b": ["公平", "稳定", "传承", "包容"]
                }
            },
            "identity": {
                "name": "身份冲突",
                "description": "精英 vs 大众",
                "patterns": [
                    "{elite}说{topic}会{promise}，{masses}问{question}",
                    "当{elite}在{elite_action}时，{masses}在{masses_action}",
                    "{topic}让{elite}更{elite_result}，让{masses}更{masses_result}",
                    "同样的{topic}，{elite}的{elite_perspective}，{masses}的{masses_perspective}"
                ],
                "fill": {
                    "elite": ["专家", "大佬", "投资人", "先行者"],
                    "masses": ["打工人", "普通人", "后来者", "小厂"],
                    "promise": ["普惠大众", "创造就业", "改善生活"],
                    "question": ["我的工作呢？", "我真的受益了吗？"],
                    "elite_action": ["布局未来", "谈论愿景", "收割红利"],
                    "masses_action": ["担心失业", "学习新技能", "被动适应"]
                }
            }
        }
    
    def build_conflicts(self, topic: str, facts: List[str], 
                        angle_type: str = None) -> List[Dict[str, Any]]:
        """
        构建冲突
        
        返回多个冲突场景，按张力排序
        """
        conflicts = []
        
        # 根据切入角选择冲突类型
        type_map = {
            "conflict": ["interest", "identity"],
            "contrast": ["cognitive", "value"],
            "suspense": ["temporal", "cognitive"],
            "human": ["identity", "interest"],
            "data": ["interest", "temporal"],
            "trend": ["temporal", "value"],
            "reveal": ["interest", "identity"],
            "compare": ["cognitive", "identity"]
        }
        
        selected_types = type_map.get(angle_type, list(self.conflict_templates.keys()))[:3]
        
        for conflict_type in selected_types:
            template_data = self.conflict_templates[conflict_type]
            pattern = random.choice(template_data["patterns"])
            conflict = self._fill_pattern(pattern, topic, template_data["fill"])
            
            conflicts.append({
                "type": conflict_type,
                "type_name": template_data["name"],
                "description": template_data["description"],
                "content": conflict,
                "tension_score": random.randint(7, 10),
                "relevance_score": random.randint(7, 10)
            })
        
        # 按综合评分排序
        for c in conflicts:
            c['total_score'] = (c['tension_score'] + c['relevance_score']) / 2
        
        conflicts.sort(key=lambda x: x['total_score'], reverse=True)
        return conflicts
    
    def _fill_pattern(self, pattern: str, topic: str, fill_data: Dict) -> str:
        """填充冲突模式"""
        result = pattern
        result = result.replace("{topic}", topic)
        
        # 通用填充
        groups = {
            "group_a": ["专家", "资本", "大厂", "精英", "先行者"],
            "group_b": ["大众", "打工人", "小厂", "普通人", "后来者"],
            "a": ["机遇", "福音", "进步"],
            "b": ["挑战", "陷阱", "威胁"]
        }
        
        for key, values in groups.items():
            result = result.replace(f"{{{key}}}", random.choice(values))
        
        # 特定类型填充
        if fill_data:
            for key, values in fill_data.items():
                result = result.replace(f"{{{key}}}", random.choice(values))
        
        # 清理未替换的
        import re
        remaining = re.findall(r'\{[^}]+\}', result)
        for placeholder in remaining:
            result = result.replace(placeholder, "...")
        
        return result[:120]
    
    def recommend_best(self, conflicts: List[Dict]) -> Dict:
        """推荐最佳冲突"""
        if not conflicts:
            return None
        return conflicts[0]
    
    def generate_conflict_paragraph(self, topic: str, conflict: Dict, 
                                    facts: List[str]) -> str:
        """
        基于冲突生成完整段落（200-300 字）
        """
        intro = conflict['content']
        
        # 扩展段落
        extensions = [
            f"这不是偶然。{topic}正在重塑游戏规则。",
            f"数据不会说谎。事实摆在眼前。",
            f"问题是，你站在哪一边？",
            f"这就是{topic}的残酷真相。"
        ]
        
        paragraph = f"{intro}{random.choice(extensions)}"
        
        if facts:
            paragraph += f"正如{facts[0][:50] if facts[0] else '事实所示'}。"
        
        return paragraph


def test_conflict_builder():
    """测试"""
    builder = ConflictBuilder()
    
    topic = "人工智能对教育的冲击"
    facts = [
        "教育部发布 AI+ 教育指导意见",
        "60% 高校已开设 AI 相关课程",
        "教师担心被 AI 取代"
    ]
    
    print(f"\n{'='*70}")
    print(f"⚔️ 冲突构建测试：{topic}")
    print(f"{'='*70}\n")
    
    conflicts = builder.build_conflicts(topic, facts, "conflict")
    
    print(f"构建 {len(conflicts)} 个冲突场景:\n")
    
    for i, c in enumerate(conflicts, 1):
        print(f"{i}. [{c['type_name']}] {c['content']}")
        print(f"   张力：{c['tension_score']}/10 | 相关性：{c['relevance_score']}/10\n")
    
    # 推荐最佳
    best = builder.recommend_best(conflicts)
    if best:
        print(f"🏆 推荐最佳冲突：{best['content']}")
        
        # 生成段落
        paragraph = builder.generate_conflict_paragraph(topic, best, facts)
        print(f"\n📝 扩展段落:\n{paragraph}")


if __name__ == "__main__":
    test_conflict_builder()
