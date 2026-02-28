import json

try:
    with open('ai_topics.json', 'r', encoding='utf-8') as f:
        topics = json.load(f)

    keywords = ['心理', '情感', '情绪', '精神', '孤独', '抑郁', '焦虑', '陪伴']
    
    psy_topics = []
    for t in topics:
        title = t.get('title', '')
        if any(kw in title for kw in keywords):
            psy_topics.append(title)
            
    print(json.dumps(psy_topics, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Error: {e}")
