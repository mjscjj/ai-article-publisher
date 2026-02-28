#!/usr/bin/env python3
"""
【端到端测试】Enhanced Pipeline Test
测试完整的增强写作流程：
话题 → 切入角 → 观点 → 结构 → 钩子 → 冲突 → 金句 → 文章
"""

import sys
import os
# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.angle_generator_lite import AngleGeneratorLite
from core.viewpoint_extractor import ViewpointExtractor
from core.narrative_optimizer import NarrativeOptimizer
from core.opening_hook_generator import HookGenerator
from core.conflict_builder import ConflictBuilder
from core.golden_sentence_generator import GoldenSentenceGenerator

def test_enhanced_pipeline():
    print("\n" + "="*70)
    print("🧪 增强写作流程端到端测试")
    print("="*70 + "\n")
    
    topic = "人工智能对教育的冲击"
    facts = [
        "教育部发布 AI+ 教育指导意见",
        "60% 高校已开设 AI 相关课程",
        "教师担心被 AI 取代",
        "学生用 AI 写作业成常态",
        "AI 教育市场规模达 1000 亿"
    ]
    
    # 1. 切入角生成
    print("Step 1: 生成切入角")
    angle_gen = AngleGeneratorLite()
    angles = angle_gen.generate_angles(topic, facts)
    best_angle = angle_gen.recommend_best(angles, "general")
    print(f"✅ 最佳切入角：[{best_angle['type_name']}] {best_angle['title']}")
    print(f"   核心观点：{best_angle['core_viewpoint']}\n")
    
    # 2. 观点提炼
    print("Step 2: 提炼核心观点")
    viewpoint_ext = ViewpointExtractor()
    viewpoints = viewpoint_ext.extract_viewpoints(topic, facts, best_angle['type'])
    best_viewpoint = viewpoint_ext.recommend_best(viewpoints)
    print(f"✅ 核心观点：[{best_viewpoint['type_name']}] {best_viewpoint['content']}")
    print(f"   强度：{best_viewpoint['intensity']}/10\n")
    
    # 3. 叙事结构
    print("Step 3: 推荐叙事结构")
    narrative_opt = NarrativeOptimizer()
    rec = narrative_opt.recommend_structure(best_angle['type'], topic)
    print(f"✅ 推荐结构：{rec['structure']['name']}")
    print(f"   原因：{rec['reason']}\n")
    
    # 4. 开篇钩子
    print("Step 4: 生成开篇钩子")
    hook_gen = HookGenerator()
    hooks = hook_gen.generate_hooks(topic, facts, best_angle['type'])
    best_hook = hook_gen.recommend_best(hooks)
    print(f"✅ 最佳钩子：[{best_hook['type_name']}] {best_hook['content']}\n")
    
    # 5. 冲突构建
    print("Step 5: 构建冲突")
    conflict_builder = ConflictBuilder()
    conflicts = conflict_builder.build_conflicts(topic, facts, best_angle['type'])
    best_conflict = conflict_builder.recommend_best(conflicts)
    print(f"✅ 最佳冲突：[{best_conflict['type_name']}] {best_conflict['content']}\n")
    
    # 6. 金句生成
    print("Step 6: 生成金句")
    sentence_gen = GoldenSentenceGenerator()
    sentences = sentence_gen.generate_sentences(topic, best_viewpoint['content'])
    best_sentence = sentence_gen.recommend_best(sentences)
    print(f"✅ 最佳金句：{best_sentence['content']}\n")
    
    # 7. 生成大纲
    print("Step 7: 生成详细大纲")
    outline = narrative_opt.generate_outline(
        "scqa", topic, best_viewpoint['content'], facts
    )
    print(f"✅ 文章结构：{outline['structure']}")
    print(f"   小节数：{len(outline['sections'])}\n")
    
    # 8. 汇总报告
    print("="*70)
    print("📋 完整创作方案")
    print("="*70)
    print(f"\n话题：{topic}")
    print(f"\n切入角：{best_angle['title']}")
    print(f"核心观点：{best_viewpoint['content']}")
    print(f"叙事结构：{outline['structure']}")
    print(f"开篇钩子：{best_hook['content']}")
    print(f"核心冲突：{best_conflict['content']}")
    print(f"点睛金句：{best_sentence['content']}")
    
    print(f"\n文章大纲:")
    for section in outline['sections']:
        print(f"  {section['order']}. {section['name']} ({section['word_count']}字)")
    
    print("\n" + "="*70)
    print("🎉 端到端测试完成")
    print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_enhanced_pipeline()
    sys.exit(0 if success else 1)
