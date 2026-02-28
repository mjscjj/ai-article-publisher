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
                combined_text = title + " " + desc
                
                # 条件: 包含 AI + 教育相关词汇
                has_ai = any(kw in combined_text for kw in ["AI", "人工智能", "大模型", "DeepSeek", "OpenAI", "GPT", "Gemini"])
                has_edu = any(kw in combined_text for kw in ["教育", "学习", "学校", "学生", "老师", "教学", "课程", "作业", "考试", "论文", "文科", "理科"])
                
                if has_ai and has_edu:
                    all_topics.append(item)
    except Exception as e:
        pass

print(f"找到 {len(all_topics)} 个 AI+教育 相关话题")
with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/ai_edu_topics.json', 'w', encoding='utf-8') as f:
    json.dump(all_topics, f, ensure_ascii=False, indent=2)
