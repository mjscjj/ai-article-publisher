import json

with open('/root/.openclaw/workspace-writer/ai-article-publisher/data/ai_topics.json', 'r') as f:
    topics = json.load(f)

edu_kws = ['教育', '学校', '老师', '学生', '大学', '文科', '理科', '辅导', '学习', '考试', '科研', '高等教育', '培训班']
psy_kws = ['心理', '情感', '情绪', '精神', '孤独', '抑郁', '焦虑', '陪伴', '压力', '治愈', '共情']

print("=== AI + Education ===")
for t in topics:
    if 'title' in t and any(kw in t['title'] for kw in edu_kws):
        print(f"[{t.get('platform', 'N/A')}] {t['title']}")

print("\n=== AI + Psychology ===")
for t in topics:
    if 'title' in t and any(kw in t['title'] for kw in psy_kws):
        print(f"[{t.get('platform', 'N/A')}] {t['title']}")

