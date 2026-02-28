import sys
import json
import os

sys.path.append('/root/.openclaw/workspace-writer/ai-article-publisher')
from core.llm_client import ask_ai

def load_unified_data(date):
    """加载指定日期的unified数据"""
    path = f"/root/.openclaw/workspace-writer/ai-article-publisher/data/hotnews/daily/{date}_unified.json"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('items', [])
    except:
        return []

# 加载最近两天的数据
print("📡 正在加载 2月24日、25日 的热点数据...")
items_24 = load_unified_data('2026-02-24')
items_25 = load_unified_data('2026-02-25')
all_items = items_24 + items_25

print(f"✅ 共加载 {len(all_items)} 条热点数据")

# 筛选 AI + 青少年/教育/成长 相关关键词
ai_keywords = ['AI', '人工智能', '大模型', 'ChatGPT', 'Sora', '算法', '智能', 'AIGC', 'DeepSeek']
teen_keywords = ['青少年', '儿童', '孩子', '学生', '教育', '成长', '童年', '青春期', '小学生', '中学生', '00后', '10后', 'Z世代']

filtered_items = []
seen_titles = set()

for item in all_items:
    title = str(item.get('title', ''))
    desc = str(item.get('description', ''))
    text = (title + ' ' + desc).upper()
    
    if not title or title in seen_titles:
        continue
    
    has_ai = any(kw.upper() in text for kw in ai_keywords)
    has_teen = any(kw.upper() in text for kw in teen_keywords)
    
    if has_ai and has_teen:
        filtered_items.append({
            'title': title,
            'source': item.get('source_name', '未知'),
            'hot': item.get('hot', 'N/A')
        })
        seen_titles.add(title)

print(f"🎯 筛选出 {len(filtered_items)} 条【AI + 青少年/成长】交叉热点")

# 取前30条让Kimi分析
top_items = filtered_items[:30]

# 构建选题分析Prompt
prompt = f"""你是一位资深教育媒体主编，正在策划一期关于"AI与青少年成长"的专题。

以下是最近两天（2026-02-24至2026-02-25）从全网抓取的热点数据，已筛选出与AI和青少年/教育相关的交叉话题：

{json.dumps(top_items, ensure_ascii=False, indent=2)}

请从中挖掘出 3 个最具爆款潜力的选题，要求：
1. 必须切中当代青少年/家长的真实痛点
2. 要有新闻新鲜感（最好是最近48小时的新趋势）
3. 能引发教育界、科技界、家长群体的三方论战
4. 适合以"教育博士人设"（幽默风趣+学术深度）来撰写

请输出JSON格式：
{{
  "proposals": [
    {{
      "title": "锋利的文章主标题",
      "subtitle": "一句话副标题",
      "angle": "切入角度（100字内）",
      "why_hot": "为什么这个选题会爆（80字内）",
      "key_sources": ["引用的原始热点标题1", "热点标题2"]
    }}
  ]
}}"""

print("\n🧠 Kimi-2.5 正在分析选题...")
result = ask_ai(prompt, "你是一位眼光毒辣的教育媒体主编，擅长发现即将爆发的话题。只输出JSON，不要废话。")

# 清理并解析结果
clean_result = result.replace("```json", "").replace("```", "").strip()
if clean_result.startswith("【"):
    # 提取最终出稿部分
    if "【🖋️" in clean_result:
        clean_result = clean_result.split("【🖋️")[-1].strip()

try:
    proposals = json.loads(clean_result)
    print("\n" + "="*70)
    print("🎯 【AI + 青少年成长】智能选题墙")
    print("="*70)
    for i, p in enumerate(proposals.get('proposals', []), 1):
        print(f"\n[{i}] {p['title']}")
        print(f"    {p['subtitle']}")
        print(f"    ► 切入角: {p['angle']}")
        print(f"    ► 爆点: {p['why_hot']}")
    print("="*70)
    
    # 保存结果
    with open("/root/.openclaw/workspace-writer/ai-article-publisher/data/ai_teen_topic_proposals.json", "w", encoding="utf-8") as f:
        json.dump(proposals, f, ensure_ascii=False, indent=2)
        
except Exception as e:
    print(f"❌ 解析失败: {e}")
    print("原始输出:", result[:500])

