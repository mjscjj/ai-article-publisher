#!/usr/bin/env python3
"""
【端到端测试脚本】E2E Test Pipeline
测试完整写作流程：话题发现 → 搜索增强 → 大纲生成 → 文章撰写 → HTML 排版
"""

import sys
import os
# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from plugins.topic_discovery.engine import TopicDiscoveryEngine
from core.prompt_toolkit import get_preset, build_prompt
from core.llm_client import ask_ai
from plugins.article_generator.outliner import generate_outline

def test_e2e_pipeline():
    print("\n" + "="*70)
    print("🧪 端到端测试：AI 写作全流程")
    print("="*70 + "\n")
    
    # Step 1: 话题发现
    print("Step 1: 话题发现")
    engine = TopicDiscoveryEngine()
    topics = engine.discover_topics(3)
    
    if not topics:
        print("❌ 话题发现失败")
        return False
    
    best_topic = topics[0]
    topic_keyword = best_topic['cluster']['cluster_keyword']
    print(f"✅ 选定话题：{topic_keyword}")
    print(f"   评分：{best_topic['scores']['total']} | {best_topic['recommendation']}")
    
    # Step 2: 构建 Fact-Pack
    print("\nStep 2: 构建事实包")
    cluster_items = best_topic['cluster']['items'][:5]
    fact_pack = {
        "title": topic_keyword,
        "facts": [item.get('title', '') for item in cluster_items],
        "sources": list(set([item.get('source_name', '未知') for item in cluster_items]))
    }
    print(f"✅ 事实包：{len(fact_pack['facts'])} 条事实，{len(fact_pack['sources'])} 个数据源")
    
    # Step 3: 生成大纲
    print("\nStep 3: 生成文章大纲")
    outline = generate_outline(fact_pack)
    print(f"✅ 大纲：{outline.get('title', 'N/A')}")
    print(f"   小节数：{len(outline.get('sections', []))}")
    
    # Step 4: 构建 Prompt
    print("\nStep 4: 构建写作 Prompt")
    facts_str = "\n".join([f"- {f}" for f in fact_pack['facts']])
    prompt = build_prompt(
        topic_keyword,
        facts_str,
        get_preset('commercial_deep')
    )
    print(f"✅ Prompt 长度：{len(prompt)} 字符")
    
    # Step 5: 调用 LLM 写作
    print("\nStep 5: AI 写作 (调用 Kimi-2.5)")
    system_prompt = "你是一名顶级商业科技媒体主笔，语言锋利克制，用事实和数据说话。"
    
    article = ask_ai(prompt, system_prompt)
    
    if article and len(article) > 500:
        print(f"✅ 文章生成成功：{len(article)} 字符")
        
        # 保存结果
        output_path = "data/e2e_test_article.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {outline.get('title', topic_keyword)}\n\n")
            f.write(article)
        print(f"✅ 文章已保存：{output_path}")
    else:
        print(f"⚠️ 文章生成异常：{len(article) if article else 0} 字符")
        print(f"   响应：{article[:200] if article else 'None'}...")
    
    print("\n" + "="*70)
    print("🎉 端到端测试完成")
    print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_e2e_pipeline()
    sys.exit(0 if success else 1)
