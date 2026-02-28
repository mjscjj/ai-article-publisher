import urllib.request
import json
import os

with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/temp_prompt.md', 'r') as f:
    prompt = f.read()

payload = json.dumps({
    "model": "qwen3.5-plus-02-15",
    "messages": [
        {"role": "user", "content": prompt}
    ]
}).encode('utf-8')

# Assume gateway environment passes through openclaw session API?
# fallback: ask openclaw for LLM using the same keys present in SHARED_INFO
