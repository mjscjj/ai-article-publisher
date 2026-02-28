import sqlite3
import json
from datetime import datetime

db_path = '/root/.openclaw/workspace-writer/ai-article-publisher/data/articles.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT title, source, url FROM hotspots WHERE date(created_at) >= '2026-02-23' AND (title LIKE '%AI%' OR title LIKE '%人工智能%' OR title LIKE '%大模型%')")
rows = c.fetchall()

edu_kws = ['教育', '学校', '老师', '学生', '大学', '文科', '理科', '学习', '考试', '科研', '高等教育']
psy_kws = ['心理', '情感', '情绪', '精神', '孤独', '抑郁', '焦虑', '陪伴', '压力', '治愈']

edu_topics = []
psy_topics = []

for r in rows:
    title = r['title']
    if any(kw in title for kw in edu_kws):
        edu_topics.append({'title': title, 'source': r['source']})
    if any(kw in title for kw in psy_kws):
        psy_topics.append({'title': title, 'source': r['source']})

print("\n=== AI + Education ===")
for t in edu_topics:
    print(f"[{t['source']}] {t['title']}")

print("\n=== AI + Psychology ===")
for t in psy_topics:
    print(f"[{t['source']}] {t['title']}")

