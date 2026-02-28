import json

with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/hotnews/daily/2026-02-24_unified.json', 'r') as f:
    data = json.load(f)

items = data.get('items', [])
edu_kws = ['教育', '学校', '老师', '学生', '大学', '文科', '理科', '辅导', '学习', '考试', '科研', '高等教育', '培训班']
ai_kws = ['AI', '人工智能', '大模型', 'GPT', 'Sora', 'Claude', '生成式', '大语言模型', 'Gemini']

print("\n=== AI + Education ===")
for t in items:
    title = str(t.get('title') or "")
    desc = str(t.get('description') or "")
    text = title + " " + desc
    if any(akw in text for akw in ai_kws) and any(pkw in text for pkw in edu_kws):
        print(f"[{t.get('source_name', 'N/A')}] {title}")

