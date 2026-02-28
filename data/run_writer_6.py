import urllib.request
import json
import os

with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/temp_prompt.md', 'r') as f:
    prompt = f.read()

payload = json.dumps({
    "model": "deepseek-reasoner",
    "messages": [
        {"role": "user", "content": prompt}
    ]
}).encode('utf-8')

# Call Volcengine or other available provider assuming standard proxy
req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=payload, headers={
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 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'
})

try:
    with urllib.request.urlopen(req) as resp:
        res_data = json.loads(resp.read().decode('utf-8'))
        content = res_data['choices'][0]['message']['content']
        with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/x_doctor_article.md', 'w') as out:
            out.write(content)
        print("Success")
except Exception as e:
    print(e)
