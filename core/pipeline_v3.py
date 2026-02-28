#!/usr/bin/env python3
"""
【V3 端到端主控管线 (E2E Pipeline)】
负责将今天所有的造物（国内三轨探针 + 魔法盒 + 晚点主编 + HTML排版机）
焊接在一起，只需输入一个命题，直接生成带排版的 HTML 微信爆款原稿。
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

from llm_client import ask_ai
from prompt_toolkit import build_prompt
from formatter_v2 import markdown_to_html_simple

# 1. 挂载 V3 的三轨情报局 (Baidu/小红书/知乎)
# 这里由于目录结构，我们需要动态加入路径
sys.path.append("/root/.openclaw/workspace-writer/ai-article-publisher/plugins/autonomous_researcher")
from researcher_cn import AutonomousResearcherCN

def run_v3_pipeline(topic: str):
    print("\n" + "="*70)
    print("🚀 [V3 Next-Gen] 端到端全自动发文流水线已启动")
    print("="*70 + "\n")
    
    # ---------------------------------------------------------
    # Phase 1: 情报收集 (Information Retrieval)
    # ---------------------------------------------------------
    print("\n>>> Phase 1: 启动三向国内探针 (Baidu x 小红书 x 知乎)")
    agent = AutonomousResearcherCN(llm_callable=ask_ai)
    fact_pack = agent.run(topic)
    
    # ---------------------------------------------------------
    # Phase 2: 大主笔创作 (Draft Generation)
    # ---------------------------------------------------------
    print("\n>>> Phase 2: 装载 Prompt 魔法盒进行内核撰写")
    techniques = [
        "scqa_framework",         # 叙事架构
        "latepost_style",         # 锋利商业风
        "anti_ai_formatting",     # 绝对禁止点列和套话
        "metaphor_injection",     # 高维隐喻
        "emotional_resonance"     # 痛点特写
    ]
    
    prompt_injected = build_prompt(topic, fact_pack, techniques)
    system_prompt = "你是一名顶级的非虚构新商业媒体主笔，你擅长用锋利的视角切分社会的系统性难题。你不屑于使用各种AI废话。"
    
    draft_markdown = ask_ai(prompt_injected, system_prompt)
    if not draft_markdown or "error" in draft_markdown:
        print("❌ 灾难性故障：大主笔生成失败！", draft_markdown)
        return
        
    draft_path = "/root/.openclaw/workspace-writer/ai-article-publisher/data/v3_draft.md"
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(draft_markdown)
        
    print(f"✅ V3 深度长文初稿已落盘: {draft_path}")

    # ---------------------------------------------------------
    # Phase 3: 毒舌主编抛光 (Reviewer)
    # ---------------------------------------------------------
    print("\n>>> Phase 3: 启动晚点毒舌主编脱水机制")
    reviewer_sys = """你是一把极其冰冷的手术刀，你的任务是修改底稿：
1. 绝对杀光诸如“在这个信息爆炸的时代”、“随着科技的发展”、“不可否认”、“综上所述”等机器陈词。
2. 保持字数和叙事主干，但让每一段的开头句变得极度抓人眼球。
3. 把所有的连接词砍掉，用更冷的陈述句推进，增加文字的压迫感。直接输出最终 Markdown，不要一句废话。"""
    
    polished_markdown = ask_ai(f"请对以下文章进行极致降味与锐化抛光：\n\n{draft_markdown}", reviewer_sys)
    
    polished_path = "/root/.openclaw/workspace-writer/ai-article-publisher/data/v3_polished.md"
    with open(polished_path, "w", encoding="utf-8") as f:
        f.write(polished_markdown)
        
    print(f"✅ 毒舌主编已完成脱水，最终定稿落盘: {polished_path}")

    # ---------------------------------------------------------
    # Phase 4: 黑客排版 (Formatter)
    # ---------------------------------------------------------
    print("\n>>> Phase 4: HTML 微信极客风排版注入")
    html_content = markdown_to_html_simple(polished_markdown)
    final_html = f"""
    <section style="box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 15px; background-color: #f8f9fa;">
        <section style="background-color: #fff; padding: 25px 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border-top: 5px solid #000;">
            {html_content}
            <br/>
            <p style="text-align:center; font-size:12px; color:#999; margin-top:30px; border-top: 1px solid #eee; padding-top: 10px;">
                主笔：OpenClaw V3 Autonomous Agent
            </p>
        </section>
    </section>
    """
    
    html_path = "/root/.openclaw/workspace-writer/ai-article-publisher/data/v3_final_article.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("\n" + "="*70)
    print(f"🎉 V3 工业级流水线运转完成！")
    print(f"🎉 最终微信公号推送准备就绪，目标文件: {html_path}")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_topic = "人工智能大模型对教育文科专业的冲击真实痛点"
    run_v3_pipeline(test_topic)
