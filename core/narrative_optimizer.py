#!/usr/bin/env python3
"""
【叙事结构优化器】Narrative Structure Optimizer
优化文章的叙事流程，增强节奏感和吸引力

结构模式:
1. SCQA - 情境 - 冲突 - 疑问 - 解答
2. 倒金字塔 - 结论先行
3. 英雄之旅 - 起点→挣扎→顿悟→回归
4. 剥洋葱 - 层层深入
5. 双线叙事 - 明线 + 暗线
"""

from typing import Dict, List, Any

class NarrativeOptimizer:
    """叙事结构优化器"""
    
    def __init__(self):
        self.structures = {
            "scqa": {
                "name": "SCQA 结构",
                "description": "情境→冲突→疑问→解答",
                "sections": [
                    {"name": "情境 S", "desc": "建立稳定背景，用具体细节"},
                    {"name": "冲突 C", "desc": "打破现状的矛盾或反常现象"},
                    {"name": "疑问 Q", "desc": "引导出核心疑问，吊胃口"},
                    {"name": "解答 A", "desc": "深度解析，给出洞察与答案"}
                ],
                "tips": [
                    "情境要具体，最好有画面感",
                    "冲突要尖锐，让人意外",
                    "疑问要自然，是冲突的延伸",
                    "解答要深刻，不能是常识"
                ]
            },
            "pyramid": {
                "name": "倒金字塔",
                "description": "结论→关键论据→细节展开",
                "sections": [
                    {"name": "结论", "desc": "最重要的观点/新闻点，5W1H"},
                    {"name": "关键论据", "desc": "支撑结论的核心数据/事实"},
                    {"name": "细节展开", "desc": "背景、引用、延伸分析"}
                ],
                "tips": [
                    "第一段必须包含全部关键信息",
                    "每段重要性递减",
                    "适合新闻、快讯、政策解读"
                ]
            },
            "hero": {
                "name": "英雄之旅",
                "description": "平凡→召唤→挣扎→顿悟→回归",
                "sections": [
                    {"name": "平凡世界", "desc": "描述现状，建立共情"},
                    {"name": "变革召唤", "desc": "某个事件打破平静"},
                    {"name": "挣扎困境", "desc": "冲突升级，各方博弈"},
                    {"name": "关键顿悟", "desc": "转折点，洞察或突破"},
                    {"name": "新常态", "desc": "改变后的世界"}
                ],
                "tips": [
                    "适合人物特写、行业变革",
                    "挣扎部分要写得真实痛苦",
                    "顿悟要有力量"
                ]
            },
            "onion": {
                "name": "剥洋葱",
                "description": "表象→第一层→第二层→核心",
                "sections": [
                    {"name": "表象", "desc": "大众看到的表面现象"},
                    {"name": "第一层", "desc": "浅层原因分析"},
                    {"name": "第二层", "desc": "深层逻辑剖析"},
                    {"name": "核心", "desc": "本质/利益/人性"}
                ],
                "tips": [
                    "每层都要比上一层更深",
                    "用'但真的是这样吗？'过渡",
                    "核心要触及利益或人性"
                ]
            },
            "dual": {
                "name": "双线叙事",
                "description": "明线 (事件)+暗线 (逻辑)",
                "sections": [
                    {"name": "明线开端", "desc": "具体事件/人物故事"},
                    {"name": "暗线铺垫", "desc": "背后的行业/社会逻辑"},
                    {"name": "明线发展", "desc": "事件推进，冲突升级"},
                    {"name": "暗线揭示", "desc": "逻辑浮出水面"},
                    {"name": "双线汇合", "desc": "事件与逻辑交汇，点题"}
                ],
                "tips": [
                    "明线要具体有画面",
                    "暗线要深刻有洞察",
                    "汇合要点睛"
                ]
            }
        }
    
    def recommend_structure(self, angle_type: str, topic: str) -> Dict[str, Any]:
        """
        根据切入角类型推荐叙事结构
        
        angle_type: conflict, contrast, suspense, human, data, trend, reveal, compare
        """
        # 匹配规则
        mapping = {
            "conflict": ["scqa", "dual"],
            "contrast": ["onion", "scqa"],
            "suspense": ["onion", "hero"],
            "human": ["hero", "dual"],
            "data": ["pyramid", "scqa"],
            "trend": ["pyramid", "hero"],
            "reveal": ["onion", "dual"],
            "compare": ["scqa", "dual"]
        }
        
        recommended = mapping.get(angle_type, ["scqa"])
        structure_key = recommended[0]
        structure = self.structures[structure_key]
        
        return {
            "structure": structure,
            "reason": self._get_reason(angle_type, structure_key),
            "customization": self._get_customization(structure_key, topic)
        }
    
    def _get_reason(self, angle_type: str, structure_key: str) -> str:
        """解释推荐原因"""
        reasons = {
            ("conflict", "scqa"): "冲突型切入需要 SCQA 的冲突构建能力",
            ("conflict", "dual"): "双线叙事可以同时展现冲突双方",
            ("contrast", "onion"): "剥洋葱适合揭示表象与真相的反差",
            ("suspense", "onion"): "层层深入制造悬念感",
            ("human", "hero"): "英雄之旅最适合讲述人物故事",
            ("data", "pyramid"): "倒金字塔让数据冲击力最大化",
            ("trend", "pyramid"): "结论先行，适合趋势预测",
            ("reveal", "onion"): "剥洋葱式揭秘，层层曝光内幕",
            ("compare", "scqa"): "SCQA 可以清晰对比前后差异"
        }
        return reasons.get((angle_type, structure_key), "该结构最适合此类切入角")
    
    def _get_customization(self, structure_key: str, topic: str) -> List[str]:
        """给出针对话题的定制建议"""
        tips = []
        structure = self.structures[structure_key]
        
        for section in structure["sections"]:
            tip = f"{section['name']}: 建议围绕'{topic}'展开，{section['desc']}"
            tips.append(tip)
        
        return tips
    
    def generate_outline(self, structure_key: str, topic: str, 
                         viewpoint: str, facts: List[str]) -> Dict[str, Any]:
        """
        基于选定结构生成详细大纲
        """
        if structure_key not in self.structures:
            structure_key = "scqa"
        
        structure = self.structures[structure_key]
        
        outline = {
            "topic": topic,
            "viewpoint": viewpoint,
            "structure": structure["name"],
            "sections": []
        }
        
        for i, section in enumerate(structure["sections"]):
            outline["sections"].append({
                "order": i + 1,
                "name": section["name"],
                "guidance": section["desc"],
                "suggested_content": self._suggest_content(section["name"], topic, viewpoint, facts),
                "word_count": self._suggest_word_count(i, len(structure["sections"]))
            })
        
        return outline
    
    def _suggest_content(self, section_name: str, topic: str, 
                         viewpoint: str, facts: List[str]) -> str:
        """建议内容方向"""
        suggestions = {
            "情境 S": f"用{topic}相关的具体场景开场，建立画面感",
            "冲突 C": f"抛出与{viewpoint}相关的矛盾或反常现象",
            "疑问 Q": f"基于冲突，自然引出核心疑问",
            "解答 A": f"给出{viewpoint}的深度论证",
            "结论": f"直接抛出{viewpoint}",
            "关键论据": f"用{facts[0] if facts else '数据'}支撑结论",
            "细节展开": "补充背景、引用、延伸分析",
            "平凡世界": "描述{topic}发生前的状态",
            "变革召唤": f"{topic}如何打破平静",
            "挣扎困境": "各方的矛盾与博弈",
            "关键顿悟": "转折点是什么",
            "新常态": f"{topic}之后的世界",
            "表象": f"大众对{topic}的表面认知",
            "第一层": "浅层原因分析",
            "第二层": "深层逻辑剖析",
            "核心": "本质/利益/人性",
            "明线开端": "具体事件或人物故事",
            "暗线铺垫": "背后的行业逻辑",
            "明线发展": "事件推进",
            "暗线揭示": "逻辑浮出水面",
            "双线汇合": "事件与逻辑交汇点题"
        }
        return suggestions.get(section_name, "根据主题展开")
    
    def _suggest_word_count(self, section_index: int, total_sections: int) -> int:
        """建议字数"""
        # 平均分配，略有侧重
        base = 2000 // total_sections
        if section_index == 0:
            return base + 100  # 开头稍多
        elif section_index == total_sections - 1:
            return base + 50  # 结尾稍多
        return base


def test_narrative_optimizer():
    """测试"""
    opt = NarrativeOptimizer()
    
    topic = "人工智能对教育的冲击"
    viewpoint = "AI 教育的本质是教育资源重新洗牌"
    facts = [
        "教育部发布 AI+ 教育指导意见",
        "60% 高校已开设 AI 相关课程"
    ]
    
    print(f"\n{'='*70}")
    print(f"📐 叙事结构优化测试：{topic}")
    print(f"{'='*70}\n")
    
    # 推荐结构
    rec = opt.recommend_structure("conflict", topic)
    print(f"推荐结构：{rec['structure']['name']}")
    print(f"原因：{rec['reason']}")
    print(f"\n定制建议:")
    for tip in rec['customization'][:3]:
        print(f"  - {tip}")
    
    # 生成大纲
    print(f"\n{'='*70}")
    print("📋 详细大纲:")
    print(f"{'='*70}\n")
    
    outline = opt.generate_outline("scqa", topic, viewpoint, facts)
    
    for section in outline["sections"]:
        print(f"{section['order']}. {section['name']} ({section['word_count']}字)")
        print(f"   指导：{section['guidance']}")
        print(f"   建议：{section['suggested_content']}\n")


if __name__ == "__main__":
    test_narrative_optimizer()
