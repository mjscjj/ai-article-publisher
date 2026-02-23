import re

pipe_file = '/root/.openclaw/workspace-writer/ai-article-publisher/pipeline.py'

with open(pipe_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 注入 deep_research 到头部
imports = """
try:
    from feishu_integration import send_to_feishu_for_review
except ImportError:
    send_to_feishu_for_review = None

try:
    from deep_research import execute_deep_research
except ImportError:
    execute_deep_research = None
"""
if "from deep_research import" not in content:
    content = content.replace("from feishu_integration import send_to_feishu_for_review\\nexcept ImportError:\\n    send_to_feishu_for_review = None", imports)

# 2. 修改 phase3
old = """def phase3_create(topic: Dict, style: str = "技术干货", config: Dict = None) -> str:
    \"\"\"创作内容（实际调用 AI）\"\"\"
    print("\\n" + "=" * 60)
    print("Phase 3: 内容创作")
    if config and config.get("modules", {}).get("deep_research", False):
        print("🔍 触发 [Deep Research] 深度研究模块... (Stub)")

    print("=" * 60)"""

new = """def phase3_create(topic: Dict, style: str = "技术干货", config: Dict = None) -> str:
    \"\"\"创作内容（实际调用 AI）\"\"\"
    print("\\n" + "=" * 60)
    print("Phase 3: 内容创作")
    
    if config and config.get("modules", {}).get("deep_research", False):
        print("🔍 触发 [Deep Research] 深度融合检索机制...")
        try:
            if execute_deep_research:
                research_material = execute_deep_research(topic, config)
                # 拿到丰富大纲！将研究材料混入 topic 的 description 中
                topic['description'] = research_material
            else:
                print("⚠️ 未找到 execute_deep_research 函数")
        except Exception as e:
            print(f"⚠️ [Deep Research] 运行失败，回退至普通创作: {e}")

    print("=" * 60)"""

content = content.replace(old, new)

with open(pipe_file, 'w', encoding='utf-8') as f:
    f.write(content)

