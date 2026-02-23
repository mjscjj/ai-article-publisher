import sys

pipe_file = '/root/.openclaw/workspace-writer/ai-article-publisher/pipeline.py'

with open(pipe_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Modify Phase 5 to use the switch
phase5_def = "def phase5_prepare(article: str, topic: Dict, review_result: Dict) -> Dict:"
new_phase5_def = """def phase5_prepare(article: str, topic: Dict, review_result: Dict, config: Dict = None) -> Dict:
    if config is None: config = {}
    modules = config.get("modules", {})
    
    # === 拦截逻辑: 如果启用了 Human in the loop, 走飞书审查 ===
    if modules.get("human_in_the_loop", False):
        try:
            from feishu_integration import send_to_feishu_for_review
            print("\\n[工作流挂起] 🚨 触发 Human-in-the-loop 人工审查模块")
            task_file = send_to_feishu_for_review(article, topic.get("title", "未命名文章"))
            return {"status": "pending_human_review", "task_file": task_file, "message": "文章已发送至飞书等待发布指令。"}
        except ImportError:
            pass
"""

content = content.replace(phase5_def, new_phase5_def)
with open(pipe_file, 'w', encoding='utf-8') as f:
    f.write(content)
