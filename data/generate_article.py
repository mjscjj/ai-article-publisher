import os
import json
import urllib.request
import sys

prompt = ""
with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/temp_prompt.md', 'r') as f:
    prompt = f.read()

data = {
    "model": "deepseek-v3", # Use openrouter if configured, otherwise we'll just mock it or use the API properly
    "messages": [{"role": "user", "content": prompt}]
}

try:
    # Try using the system's python script to call OpenRouter since it's already configured
    from openai import OpenAI
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY", "")
    )
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[{"role": "user", "content": prompt}]
    )
    
    with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/x_doctor_article.md', 'w') as f:
        f.write(response.choices[0].message.content)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
