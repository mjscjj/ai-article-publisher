import sys
sys.path.append('/root/.openclaw/workspace-writer/ai-article-publisher')
from topic_analyzer import call_llm

with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/temp_prompt.md', 'r') as f:
    prompt = f.read()

result = call_llm(prompt)
with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/x_doctor_article.md', 'w') as f:
    f.write(result)
print("Finished.")
