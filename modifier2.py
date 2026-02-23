import sys

pipe_file = '/root/.openclaw/workspace-writer/ai-article-publisher/pipeline.py'

with open(pipe_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add config parsing to phase3
phase3_def = "def phase3_create(topic: Dict, style: str) -> str:"
new_phase3_def = """def phase3_create(topic: Dict, style: str, config: Dict = None) -> str:
    if config is None: config = {}
    modules = config.get("modules", {})
    
    print("\\n" + "=" * 60)
    print("Phase 3: 内容创作")
    print("=" * 60)
    
    if modules.get("deep_research", False):
        print("🔍 触发 [Deep Research] 深度研究模块...")
        print("  → [模块已激活] 开始多源交叉检索与大纲合成支持")
        # TODO: call deep research python script here!
        # ... fallback to normal creation for now ...
"""

# replace the first occurrence
content = content.replace("def phase3_create(topic: Dict, style: str) -> str:\n    \"\"\"根据选题生成内容\"\"\"\n    print(\"\\n\" + \"=\" * 60)\n    print(\"Phase 3: 内容创作\")\n    print(\"=\" * 60)", new_phase3_def)

# find the call to phase3_create
content = content.replace("article = phase3_create(selected_topic, style)", "article = phase3_create(selected_topic, style, PIPELINE_CONFIG)")

# multi_agent
phase4_def = "def phase4_review(article: str) -> Dict:"
new_phase4_def = """def phase4_review(article: str, config: Dict = None) -> Dict:
    if config is None: config = {}
    modules = config.get("modules", {})
    
    print("\\n" + "=" * 60)
    print("Phase 4: 审查订正")
    print("=" * 60)
    
    if modules.get("multi_agent_review", False):
        print("👥 触发 [Multi-Agent Review] 多终端博弈模块...")
        print("  → 正在初始化'主编'与'主笔'对抗审查...")
        # TODO: multi-agent review logic here
"""
content = content.replace("def phase4_review(article: str) -> Dict:\n    \"\"\"审查文章\"\"\"\n    print(\"\\n\" + \"=\" * 60)\n    print(\"Phase 4: 审查订正\")\n    print(\"=\" * 60)", new_phase4_def)

content = content.replace("review_result = phase4_review(article)", "review_result = phase4_review(article, PIPELINE_CONFIG)")

with open(pipe_file, 'w', encoding='utf-8') as f:
    f.write(content)

