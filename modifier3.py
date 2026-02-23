import re

pipe_file = '/root/.openclaw/workspace-writer/ai-article-publisher/pipeline.py'

with open(pipe_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix phase3 signature
content = re.sub(
    r"def phase3_create\(topic: Dict, style: str\) -> str:",
    "def phase3_create(topic: Dict, style: str, config: Dict = None) -> str:\n    if config: pass\n",
    content
)
# Add some trace
content = content.replace('print("\\n" + "=" * 60)\n    print("Phase 3: 内容创作")',
'''    print("\\n" + "=" * 60)
    print("Phase 3: 内容创作")
    if config and config.get("modules", {}).get("deep_research", False):
        print("🔍 触发 [Deep Research] 深度研究模块... (Stub)")
''')

# Fix phase4 signature
content = re.sub(
    r"def phase4_review\(article: str\) -> Dict:",
    "def phase4_review(article: str, config: Dict = None) -> Dict:\n    if config: pass\n",
    content
)
content = content.replace('print("\\n" + "=" * 60)\n    print("Phase 4: 审查订正")',
'''    print("\\n" + "=" * 60)
    print("Phase 4: 审查订正")
    if config and config.get("modules", {}).get("multi_agent_review", False):
        print("👥 触发 [Multi-Agent Review] 多终端博弈模块... (Stub)")
''')

with open(pipe_file, 'w', encoding='utf-8') as f:
    f.write(content)
