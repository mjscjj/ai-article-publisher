import json

with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/hotnews/daily/2026-02-24_unified.json', 'r') as f:
    data = json.load(f)

items = data.get('items', [])
psy_kws = ['心理', '情感', '情绪', '孤独', '疗愈', '陪伴', '抑郁', '精神', '压力', '恋爱', '脱单', '结婚', '失眠']
ai_kws = ['AI', '人工智能', '大模型', 'GPT', 'Sora', 'Claude', '生成式', '大语言模型', 'Gemini']

print("\n=== AI + Psychology / Emotions ===")
for t in items:
    title = str(t.get('title') or "")
    desc = str(t.get('description') or "")
    text = title + " " + desc
    if any(akw in text for akw in ai_kws) and any(pkw in text for pkw in psy_kws):
        print(f"[{t.get('source_name', 'N/A')}] {title}")

