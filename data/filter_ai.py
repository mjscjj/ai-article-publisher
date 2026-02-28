import json
import os
import glob

all_topics = []
for file in glob.glob('/root/.openclaw/workspace-writer/ai-article-publisher/data/hotnews/by_source/*.json'):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            items = []
            if isinstance(data, dict):
                items = list(data.get("items", {}).values()) if "items" in data else list(data.values())
            elif isinstance(data, list):
                items = data
            for item in items:
                title = item.get("title", "")
                desc = item.get("description", "")
                if "AI" in title or "人工智能" in title or "大模型" in title or "DeepSeek" in title or "OpenAI" in title or "GPT" in title or "Gemini" in title:
                    all_topics.append(item)
    except Exception as e:
        pass

print(f"找到 {len(all_topics)} 个AI相关话题")
with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/ai_topics.json', 'w', encoding='utf-8') as f:
    json.dump(all_topics, f, ensure_ascii=False, indent=2)
