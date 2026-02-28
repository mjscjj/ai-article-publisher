import subprocess
import json
import urllib.request
import os

with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/temp_prompt.md', 'r') as f:
    prompt = f.read()

payload = json.dumps({
    "model": "deepseek/deepseek-r1-0528:free",
    "messages": [
        {"role": "user", "content": prompt}
    ]
}).encode('utf-8')

# OpenCLaw gateway provides internal OpenAI API compatible endpoint on localhost port 3000 ? Let's check config first
