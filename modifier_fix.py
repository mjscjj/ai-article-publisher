pipe_file = '/root/.openclaw/workspace-writer/ai-article-publisher/pipeline.py'

with open(pipe_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add the import correctly
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
    old_import = """try:
    from feishu_integration import send_to_feishu_for_review
except ImportError:
    send_to_feishu_for_review = None"""
    content = content.replace(old_import, imports)

with open(pipe_file, 'w', encoding='utf-8') as f:
    f.write(content)

