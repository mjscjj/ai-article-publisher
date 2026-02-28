#!/usr/bin/env python3
"""
【切入角生成器】Angle Generator
基于话题和事实，生成多个独特的文章切入角度

核心理念:
- 同样的话题，不同的切入角 = 完全不同的文章
- 好的切入角 = 冲突 + 反差 + 具体人物/场景

支持的切入角类型:
1. 冲突型 - 两方对立 (专家 vs 大众、理想 vs 现实)
2. 反差型 - 预期违背 (看似 A 实际 B)
3. 悬念型 - 抛出问题 (为什么 X 却 Y)
4. 人物型 - 具体个体故事 (某人的真实经历)
5. 数据型 - 惊人数字 (X%的人不知道...)
6. 趋势型 - 未来预测 (3 年后将...)
7. 揭秘型 - 内幕曝光 (鲜为人知的...)
8. 对比型 - 前后/中外对比 (过去 vs 现在)
"""

import json
import os
import re
import requests
from typing import Dict, List, Any

AI_BASE_URL = "https://api.moonshot.cn/v1/chat/completions"
MODEL = "kimi-k2.5"
API_KEY = os.environ.get("MOONSHOT_API_KEY", "sk-tjG07oY0FqrzooJ8ymKVJeoLeGY8AuMORFjQATO2RdNmFmQw")

ANGLE_TYPES = {
    "conflict": {
        "name": "冲突型",
        "prompt": "找出这个话题中最大的矛盾冲突点：两方观点对立、利益冲突、认知差异。用'A vs B'的格式呈现。",
        "example": "专家说 AI 让人失业 vs 企业说招不到 AI 人才"
    },
    "contrast": {
        "name": "反差型",
        "prompt": "找出这个话题中最违背直觉的反差点：看似应该 A，实际却是 B。",
        "example": "看似高大上的 AI 技术，实际被用来干最土的活"
    },
    "suspense": {
        "name": "悬念型",
        "prompt": "针对这个话题，提出一个让人好奇的悬念问题：为什么 X 现象会发生？背后隐藏着什么？",
        "example": "为什么 AI 越发达，打工人越焦虑？"
    },
    "human": {
        "name": "人物型",
        "prompt": "找到一个具体的人物/群体，他们的真实故事能代表这个话题的核心痛点。",
        "example": "一个 35 岁程序员被 AI 取代的真实 72 小时"
    },
    "data": {
        "name": "数据型",
        "prompt": "提取这个话题中最惊人/反直觉的数据，用数字制造冲击力。",
        "example": "80% 的企业用 AI 只为裁员，不是增效"
    },
    "trend": {
        "name": "趋势型",
        "prompt": "预测这个话题 3-5 年后的走向，给出一个大胆但合理的判断。",
        "example": "2028 年，一半的大学专业将被 AI 淘汰"
    },
    "reveal": {
        "name": "揭秘型",
        "prompt": "曝光这个话题背后鲜为人知的内幕、潜规则或真相。",
        "example": "AI 培训机构的骗局：99% 的课程都是割韭菜"
    },
    "compare": {
        "name": "对比型",
        "prompt": "做一个强烈的对比：过去 vs 现在、中国 vs 国外、富人 vs 穷人等。",
        "example": "美国用 AI 搞科研，我们用 AI 写公文"
    }
}

class AngleGenerator:
    """切入角生成器"""
    
    def __init__(self):
        self.api_key = API_KEY
    
    def generate_angles(self, topic: str, facts: List[str]) -> List[Dict[str, Any]]:
        """
        为给定话题生成多个切入角
        
        返回：切入角列表，每个包含类型、标题、核心观点、开篇建议
        """
        angles = []
        
        # 为每种类型生成切入角
        for angle_type, config in ANGLE_TYPES.items():
            angle = self._generate_single_angle(topic, facts, angle_type, config)
            if angle:
                angles.append(angle)
        
        # 评分排序
        angles.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return angles
    
    def _generate_single_angle(self, topic: str, facts: List[str], 
                                angle_type: str, config: Dict) -> Dict[str, Any]:
        """生成单个切入角"""
        facts_str = "\n".join([f"- {f}" for f in facts[:5]])
        
        prompt = f"""话题：{topic}

相关事实：
{facts_str}

任务：{config['prompt']}

要求:
1. 标题要尖锐、有冲击力，15-25 字
2. 核心观点要清晰，一句话能说清楚
3. 开篇建议要具体，有画面感
4. 避免套话、空话

返回严格的 JSON 对象，不要任何其他文字:
{{"type": "{angle_type}", "type_name": "{config['name']}", "title": "标题", "core_viewpoint": "核心观点", "opening_hook": "开篇建议", "supporting_facts": ["事实 1", "事实 2"], "score": 85}}"""
        
        try:
            response = self._call_llm(prompt)
            angle_data = self._extract_json(response)
            
            if angle_data:
                angle_data['angle_type'] = angle_type
                return angle_data
        except Exception as e:
            print(f"[Angle] {config['name']} 生成失败：{e}")
        
        # 降级：返回基础版本
        return self._fallback_angle(topic, facts, angle_type, config)
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 简化 Prompt，避免过长
        short_prompt = prompt[:2000]
        
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "你是顶级新媒体编辑。只输出 JSON，不要任何其他文字。"},
                {"role": "user", "content": short_prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            resp = requests.post(AI_BASE_URL, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            # 打印详细错误
            print(f"    API 错误：{e}")
            if hasattr(e.response, 'text'):
                print(f"    响应：{e.response.text[:200]}")
            raise
    
    def _extract_json(self, text: str) -> Dict:
        """提取 JSON"""
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        return None
    
    def _fallback_angle(self, topic: str, facts: List[str], 
                        angle_type: str, config: Dict) -> Dict[str, Any]:
        """降级版本"""
        return {
            "type": angle_type,
            "type_name": config['name'],
            "title": f"{topic} 的{config['name']}视角",
            "core_viewpoint": f"从{config['name']}角度解读{topic}",
            "opening_hook": f"想象一下，{topic}正在改变一切...",
            "supporting_facts": facts[:2],
            "score": 60
        }
    
    def recommend_best(self, angles: List[Dict], target_audience: str = "general") -> Dict:
        """
        推荐最佳切入角
        
        target_audience: general(大众), professional(专业), youth(年轻)
        """
        if not angles:
            return None
        
        # 根据目标受众调整权重
        weights = {
            "general": {"data": 1.2, "human": 1.3, "conflict": 1.1},
            "professional": {"data": 1.3, "trend": 1.2, "reveal": 1.1},
            "youth": {"conflict": 1.3, "contrast": 1.2, "human": 1.1}
        }
        
        audience_weights = weights.get(target_audience, weights["general"])
        
        # 加权排序
        for angle in angles:
            bonus = audience_weights.get(angle['type'], 1.0)
            angle['adjusted_score'] = angle.get('score', 60) * bonus
        
        angles.sort(key=lambda x: x.get('adjusted_score', 0), reverse=True)
        return angles[0]


def test_angle_generator():
    """测试"""
    gen = AngleGenerator()
    
    topic = "人工智能对教育的冲击"
    facts = [
        "教育部发布 AI+ 教育指导意见",
        "60% 高校已开设 AI 相关课程",
        "教师担心被 AI 取代",
        "学生用 AI 写作业成常态",
        "AI 教育市场规模达 1000 亿"
    ]
    
    print(f"\n{'='*70}")
    print(f"📐 切入角生成测试：{topic}")
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
    test_angle_generator()
