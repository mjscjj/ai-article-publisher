#!/usr/bin/env python3
"""
【自动化写作引擎】Auto Writing Engine
完整流程：选题 → 搜索数据 → 生成大纲 → 写作 → 排版

使用示例:
    from core.auto_writer import AutoWriter
    
    writer = AutoWriter()
    article = writer.write_full_article("人工智能对教育的冲击")
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# 导入各模块
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from angle_generator_lite import AngleGeneratorLite
from viewpoint_extractor import ViewpointExtractor
from narrative_optimizer import NarrativeOptimizer
from opening_hook_generator import HookGenerator
from conflict_builder import ConflictBuilder
from golden_sentence_generator import GoldenSentenceGenerator
from rag_simple import SimpleRAG
try:
    from llm_client import ask_ai
except:
    ask_ai = None
try:
    from formatter_v2 import markdown_to_html_simple
except:
    markdown_to_html_simple = lambda x: x

class AutoWriter:
    """自动化写作引擎"""
    
    def __init__(self, use_llm: bool = True):
        """
        Args:
            use_llm: 是否使用 LLM 写作 (True=用 Kimi，False=规则生成)
        """
        self.use_llm = use_llm
        
        # 初始化各模块
        self.angle_gen = AngleGeneratorLite()
        self.viewpoint_ext = ViewpointExtractor()
        self.narrative_opt = NarrativeOptimizer()
        self.hook_gen = HookGenerator()
        self.conflict_builder = ConflictBuilder()
        self.sentence_gen = GoldenSentenceGenerator()
        self.rag = SimpleRAG()
        
        # 输出目录
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'output'
        )
        os.makedirs(self.output_dir, exist_ok=True)
    
    def write_full_article(self, topic: str, 
                          facts: List[str] = None,
                          style: str = "commercial_deep") -> Dict[str, Any]:
        """
        完整写作流程
        
        Args:
            topic: 话题
            facts: 事实列表 (可选，不提供则从 RAG 搜索)
            style: 写作风格 (commercial_deep/news_fast/story_feature...)
        
        Returns:
            {
                "topic": 话题,
                "angle": 切入角,
                "viewpoint": 核心观点,
                "outline": 大纲,
                "draft": 草稿 (Markdown),
                "html": 排版后 HTML,
                "stats": 统计信息
            }
        """
        print(f"\n{'='*70}")
        print(f"🚀 自动化写作启动：{topic}")
        print(f"{'='*70}\n")
        
        # Step 1: 从 RAG 搜索数据 (如果未提供 facts)
        if not facts:
            print("Step 1: 从 RAG 搜索相关数据")
            rag_results = self.rag.search(topic, top_k=5)
            facts = [r['snippet'] for r in rag_results]
            
            if not facts:
                # RAG 无数据，使用默认事实
                facts = [f"{topic}正在改变行业格局", f"专家热议{topic}的影响"]
            
            print(f"   ✅ 获取 {len(facts)} 条事实\n")
        else:
            print(f"Step 1: 使用提供的事实 ({len(facts)} 条)\n")
        
        # Step 2: 生成切入角
        print("Step 2: 生成切入角")
        angles = self.angle_gen.generate_angles(topic, facts)
        best_angle = self.angle_gen.recommend_best(angles, "general")
        print(f"   ✅ [{best_angle['type_name']}] {best_angle['title']}\n")
        
        # Step 3: 提炼核心观点
        print("Step 3: 提炼核心观点")
        viewpoints = self.viewpoint_ext.extract_viewpoints(
            topic, facts, best_angle['type']
        )
        best_viewpoint = self.viewpoint_ext.recommend_best(viewpoints)
        print(f"   ✅ {best_viewpoint['content']}\n")
        
        # Step 4: 推荐叙事结构
        print("Step 4: 推荐叙事结构")
        rec = self.narrative_opt.recommend_structure(best_angle['type'], topic)
        structure_key = self._get_structure_key(rec['structure']['name'])
        outline = self.narrative_opt.generate_outline(
            structure_key, topic, best_viewpoint['content'], facts
        )
        print(f"   ✅ {rec['structure']['name']} ({len(outline['sections'])}小节)\n")
        
        # Step 5: 生成开篇钩子
        print("Step 5: 生成开篇钩子")
        hooks = self.hook_gen.generate_hooks(topic, facts, best_angle['type'])
        best_hook = self.hook_gen.recommend_best(hooks)
        print(f"   ✅ {best_hook['content']}\n")
        
        # Step 6: 构建核心冲突
        print("Step 6: 构建核心冲突")
        conflicts = self.conflict_builder.build_conflicts(
            topic, facts, best_angle['type']
        )
        best_conflict = self.conflict_builder.recommend_best(conflicts)
        print(f"   ✅ {best_conflict['content']}\n")
        
        # Step 7: 生成金句
        print("Step 7: 生成金句")
        sentences = self.sentence_gen.generate_sentences(
            topic, best_viewpoint['content']
        )
        best_sentence = self.sentence_gen.recommend_best(sentences)
        print(f"   ✅ {best_sentence['content']}\n")
        
        # Step 8: 写作
        print("Step 8: 生成文章")
        if self.use_llm:
            draft = self._write_with_llm(
                topic, best_angle, best_viewpoint, outline, 
                best_hook, best_conflict, best_sentence, facts
            )
        else:
            draft = self._write_with_rules(
                topic, best_angle, best_viewpoint, outline,
                best_hook, best_conflict, best_sentence, facts
            )
        
        print(f"   ✅ 文章生成成功 ({len(draft)} 字符)\n")
        
        # Step 9: HTML 排版
        print("Step 9: HTML 排版")
        html = markdown_to_html_simple(draft)
        print(f"   ✅ 排版完成\n")
        
        # Step 10: 保存到 RAG 和文件
        print("Step 10: 保存成果")
        self.rag.add_article(
            title=f"[草稿] {topic}",
            content=draft,
            topic=topic,
            tags=[best_angle['type'], structure_key]
        )
        
        # 保存文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        md_path = os.path.join(self.output_dir, f"article_{timestamp}.md")
        html_path = os.path.join(self.output_dir, f"article_{timestamp}.html")
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {topic}\n\n{draft}")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"   ✅ Markdown: {md_path}")
        print(f"   ✅ HTML: {html_path}\n")
        
        # 返回完整结果
        return {
            "topic": topic,
            "angle": best_angle,
            "viewpoint": best_viewpoint,
            "outline": outline,
            "draft": draft,
            "html": html,
            "stats": {
                "char_count": len(draft),
                "word_count": len(draft) // 2,
                "facts_used": len(facts),
                "structure": rec['structure']['name']
            },
            "files": {
                "markdown": md_path,
                "html": html_path
            }
        }
    
    def _write_with_llm(self, topic: str, angle: Dict, viewpoint: Dict,
                        outline: Dict, hook: Dict, conflict: Dict, 
                        sentence: Dict, facts: List[str]) -> str:
        """使用 LLM 写作"""
        
        # 构建 Prompt
        prompt_parts = []
        
        # 1. 角色设定
        prompt_parts.append("""你是一名顶级新媒体主笔，擅长写出爆款深度文章。
语言锋利克制，用事实和数据说话，拒绝 AI 套话。""")
        
        # 2. 核心信息
        prompt_parts.append(f"\n## 话题：{topic}")
        prompt_parts.append(f"\n## 切入角：{angle['title']}")
        prompt_parts.append(f"\n## 核心观点：{viewpoint['content']}")
        
        # 3. 开篇钩子
        prompt_parts.append(f"\n## 开篇要求：{hook['content']}")
        
        # 4. 核心冲突
        prompt_parts.append(f"\n## 核心冲突：{conflict['content']}")
        
        # 5. 点睛金句
        prompt_parts.append(f"\n## 必须包含的金句：{sentence['content']}")
        
        # 6. 事实支撑
        prompt_parts.append("\n## 必须使用的事实:")
        for i, fact in enumerate(facts, 1):
            prompt_parts.append(f"{i}. {fact}")
        
        # 7. 文章结构
        prompt_parts.append("\n## 文章结构:")
        for section in outline['sections']:
            prompt_parts.append(
                f"- {section['name']} ({section['word_count']}字): {section['guidance']}"
            )
        
        # 8. 写作要求
        prompt_parts.append("""
## 写作要求:
1. 字数：2000-2500 字
2. 禁止使用项目符号 (-、1.2.3.)，用完整段落
3. 禁止 AI 套话 ("在这个信息爆炸的时代"、"综上所述"等)
4. 每段都要有事实或数据支撑
5. 至少包含 3 个直接引语
6. 结尾必须有力，呼应开篇

直接输出文章正文，不要任何前置说明。""")
        
        full_prompt = "\n".join(prompt_parts)
        
        # 调用 LLM
        system_prompt = "你是《晚点 LatePost》资深主笔，语言锋利，用事实说话。"
        article = ask_ai(full_prompt, system_prompt)
        
        # 清理响应
        if "【🧠" in article:
            # 去除思考链路
            import re
            match = re.search(r'【🖋️.*?】\n(.*)', article, re.S)
            if match:
                article = match.group(1)
        
        return article.strip()
    
    def _write_with_rules(self, topic: str, angle: Dict, viewpoint: Dict,
                          outline: Dict, hook: Dict, conflict: Dict,
                          sentence: Dict, facts: List[str]) -> str:
        """使用规则写作 (无 LLM)"""
        
        paragraphs = []
        
        # 开篇
        paragraphs.append(hook['content'])
        paragraphs.append("")
        
        # 按大纲段落生成
        for section in outline['sections']:
            # 小标题
            paragraphs.append(f"## {section['name']}")
            paragraphs.append("")
            
            # 段落内容
            para = f"{section['guidance']}。"
            
            # 加入事实
            if facts:
                para += f"正如{facts[0]}。"
            
            paragraphs.append(para)
            paragraphs.append("")
        
        # 结尾金句
        paragraphs.append("---")
        paragraphs.append("")
        paragraphs.append(f"> {sentence['content']}")
        
        return "\n".join(paragraphs)
    
    def _get_structure_key(self, structure_name: str) -> str:
        """结构名称转 key"""
        mapping = {
            "SCQA 结构": "scqa",
            "倒金字塔": "pyramid",
            "英雄之旅": "hero",
            "剥洋葱": "onion",
            "双线叙事": "dual"
        }
        return mapping.get(structure_name, "scqa")


def test_auto_writer():
    """测试自动写作"""
    print("\n" + "="*70)
    print("🤖 自动化写作引擎测试")
    print("="*70 + "\n")
    
    # 创建写作引擎 (不使用 LLM，避免 API 调用)
    writer = AutoWriter(use_llm=False)
    
    # 写作
    result = writer.write_full_article(
        topic="人工智能对教育的冲击",
        style="commercial_deep"
    )
    
    # 输出统计
    print("="*70)
    print("📊 写作统计")
    print("="*70)
    print(f"话题：{result['topic']}")
    print(f"切入角：{result['angle']['title']}")
    print(f"核心观点：{result['viewpoint']['content']}")
    print(f"结构：{result['stats']['structure']}")
    print(f"字数：{result['stats']['word_count']}")
    print(f"使用事实：{result['stats']['facts_used']} 条")
    print(f"\n文件保存:")
    print(f"  Markdown: {result['files']['markdown']}")
    print(f"  HTML: {result['files']['html']}")
    print("\n" + "="*70)
    print("🎉 自动化写作测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_auto_writer()
