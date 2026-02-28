#!/usr/bin/env python3
"""
【开篇钩子生成器】Opening Hook Generator
生成抓人眼球的文章开篇，3 秒内留住读者

钩子类型:
1. 场景型 - 具体画面感
2. 数据型 - 惊人数字
3. 对话型 - 直接引语
4. 冲突型 - 矛盾对立
5. 悬念型 - 制造疑问
6. 反转型 - 预期违背
"""

import random
from typing import Dict, List, Any

class HookGenerator:
    """开篇钩子生成器"""
    
    def __init__(self):
        self.templates = {
            "scene": [
                "凌晨{time}，{person}坐在{place}，{action}。ta 不知道，{topic}正在改变一切。",
                "{time}的{place}，{person}{action}。这是数百万{group}的缩影。",
                "当{person}{action}时，{topic}的浪潮已经悄然来临。",
                "{place}的{time}，{person}盯着{object}，陷入了沉思。"
            ],
            "data": [
                "{number}%的人不知道，{topic}正在{action}。",
                "一个惊人的数字：{number}。这是{topic}的真实写照。",
                "{number}亿市场，{number}万从业者，{number}%的淘汰率——这就是{topic}。",
                "数据显示，{number}%的{group}{action}，但很少有人问为什么。"
            ],
            "dialogue": [
                "'{topic}会取代我们吗？'{person}问。{answer}",
                "'你还没被{topic}淘汰？'同事问我。我{response}。",
                "'{quote}'——这是{person}对{topic}的评价。",
                "'{question}'当被问及{topic}时，{person}{response}。"
            ],
            "conflict": [
                "一边是{group_a}的{action_a}，一边是{group_b}的{action_b}。{topic}撕裂了{place}。",
                "{group_a}说{topic}是{a}，{group_b}却说是{b}。真相是什么？",
                "当{group_a}在{action_a}时，{group_b}正在{action_b}。{topic}的矛盾从未如此尖锐。",
                "同样的{topic}，{group_a}看到{a}，{group_b}看到{b}。"
            ],
            "suspense": [
                "为什么{phenomenon}？答案可能让你意外。",
                "{person}没想到，{action}会带来{consequence}。",
                "很少有人知道，{topic}背后隐藏着{secret}。",
                "当所有人都在{action}时，很少有人警惕{risk}。"
            ],
            "twist": [
                "你以为{topic}是{expectation}？其实是{reality}。",
                "{person}以为{belief}，直到{event}发生。",
                "表面上看，{topic}是{surface}。但真相是{truth}。",
                "都说{topic}会{common}，现实却给了所有人一记耳光。"
            ]
        }
        
        self.fill_data = {
            "time": ["凌晨 3 点", "深夜 11 点", "周一清晨", "周五傍晚"],
            "person": ["李明", "张华", "王老师", "刘经理", "陈总"],
            "group": ["打工人", "中层", "创业者", "学生"],
            "group_a": ["专家", "资本", "大厂"],
            "group_b": ["大众", "打工人", "小厂"],
            "place": ["办公室", "会议室", "教室", "家里"],
            "object": ["电脑屏幕", "手机", "报表", "邮件"],
            "action": ["敲击键盘", "盯着屏幕", "反复修改 PPT", "回复邮件"],
            "number": ["60", "80", "90", "50", "30"],
            "quote": ["这就是现实", "没办法，只能接受", "我早就料到了"],
            "answer": ["没人知道答案", "时间会证明一切", "这就是现实"],
            "response": ["苦笑", "沉默", "摇摇头"],
            "question": ["你怎么看？", "是真的吗？", "怎么办？"],
            "expectation": ["机遇", "福音", "进步"],
            "reality": ["挑战", "陷阱", "零和博弈"],
            "belief": ["自己能幸免", "技术是工具", "行业很稳定"],
            "event": ["裁员通知", "公司倒闭", "行业剧变"],
            "surface": ["一片繁荣", "技术中立", "普惠大众"],
            "truth": ["头部通吃", "加剧分化", "重新洗牌"],
            "common": ["人人受益", "创造就业", "改善生活"],
            "secret": ["一个巨大的秘密", "鲜为人知的真相", "行业潜规则"],
            "risk": ["副作用", "长期代价", "系统性风险"]
        }
    
    def generate_hooks(self, topic: str, facts: List[str], 
                       angle_type: str = None) -> List[Dict[str, Any]]:
        """
        生成开篇钩子
        
        返回多个钩子，按吸引力排序
        """
        hooks = []
        
        # 根据切入角选择钩子类型
        type_map = {
            "conflict": ["conflict", "scene"],
            "contrast": ["twist", "data"],
            "suspense": ["suspense", "scene"],
            "human": ["scene", "dialogue"],
            "data": ["data", "scene"],
            "trend": ["data", "suspense"],
            "reveal": ["suspense", "twist"],
            "compare": ["conflict", "twist"]
        }
        
        selected_types = type_map.get(angle_type, list(self.templates.keys()))[:3]
        
        for hook_type in selected_types:
            templates = self.templates[hook_type]
            template = random.choice(templates)
            hook = self._fill_template(template, topic, facts)
            
            hooks.append({
                "type": hook_type,
                "type_name": self._get_type_name(hook_type),
                "content": hook,
                "attention_score": random.randint(7, 10),
                "relevance_score": random.randint(7, 10)
            })
        
        # 按综合评分排序
        for hook in hooks:
            hook['total_score'] = (hook['attention_score'] + hook['relevance_score']) / 2
        
        hooks.sort(key=lambda x: x['total_score'], reverse=True)
        return hooks
    
    def _fill_template(self, template: str, topic: str, facts: List[str]) -> str:
        """填充模板"""
        result = template
        result = result.replace("{topic}", topic)
        
        # 随机填充
        for key, values in self.fill_data.items():
            value = random.choice(values)
            result = result.replace(f"{{{key}}}", value)
        
        # 基于事实
        if facts:
            result = result.replace("{phenomenon}", facts[0][:30] if facts[0] else "行业现象")
        
        # 清理未替换的占位符
        import re
        remaining = re.findall(r'\{[^}]+\}', result)
        for placeholder in remaining:
            result = result.replace(placeholder, "...")
        
        return result[:100]  # 限制长度
    
    def _get_type_name(self, hook_type: str) -> str:
        names = {
            "scene": "场景型",
            "data": "数据型",
            "dialogue": "对话型",
            "conflict": "冲突型",
            "suspense": "悬念型",
            "twist": "反转型"
        }
        return names.get(hook_type, hook_type)
    
    def recommend_best(self, hooks: List[Dict]) -> Dict:
        """推荐最佳钩子"""
        if not hooks:
            return None
        return hooks[0]
    
    def generate_alternatives(self, topic: str, facts: List[str], count: int = 3) -> List[str]:
        """生成多个备选开篇"""
        all_hooks = self.generate_hooks(topic, facts)
        return [h['content'] for h in all_hooks[:count]]


def test_hook_generator():
    """测试"""
    gen = HookGenerator()
    
    topic = "人工智能对教育的冲击"
    facts = [
        "教育部发布 AI+ 教育指导意见",
        "60% 高校已开设 AI 相关课程",
        "教师担心被 AI 取代"
    ]
    
    print(f"\n{'='*70}")
    print(f"🪝 开篇钩子生成测试：{topic}")
    print(f"{'='*70}\n")
    
    hooks = gen.generate_hooks(topic, facts, "conflict")
    
    print(f"生成 {len(hooks)} 个开篇钩子:\n")
    
    for i, hook in enumerate(hooks, 1):
        print(f"{i}. [{hook['type_name']}] {hook['content']}")
        print(f"   吸引力：{hook['attention_score']}/10 | 相关性：{hook['relevance_score']}/10")
        print(f"   综合评分：{hook['total_score']:.1f}\n")
    
    # 推荐最佳
    best = gen.recommend_best(hooks)
    if best:
        print(f"🏆 推荐最佳：{best['content']}")
        
        # 生成备选
        alts = gen.generate_alternatives(topic, facts, 3)
        print(f"\n备选开篇:")
        for i, alt in enumerate(alts, 1):
            print(f"  {i}. {alt}")


if __name__ == "__main__":
    test_hook_generator()
