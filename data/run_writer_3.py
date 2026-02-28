import sys
import os
import urllib.request
import json
sys.path.append('/root/.openclaw/workspace-writer/ai-article-publisher')

with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/temp_prompt.md', 'r') as f:
    prompt = f.read()

payload = json.dumps({
    "model": "openai/gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "You are X博士, a rigorous, deep, and insightful tech writer."},
        {"role": "user", "content": prompt}
    ]
}).encode('utf-8')

req = urllib.request.Request("http://43.134.234.4:3001/v1/chat/completions", data=payload, headers={
    'Content-Type': 'application/json',
    'Authorization': 'Bearer sk-WaUmgZsMxgeHOpp8SJxK1rmVQxiwfiDJ'
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

