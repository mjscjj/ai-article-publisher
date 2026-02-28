import subprocess
import json

with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/temp_prompt.md', 'r') as f:
    prompt = f.read()

payload_dict = {
    "model": "deepseek/deepseek-r1-0528:free",
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/payload.json', 'w') as f:
    json.dump(payload_dict, f)

