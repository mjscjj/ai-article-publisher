import sys
import os
import json

sys.path.append('/root/.openclaw/workspace-writer/ai-article-publisher')
from core.llm_client import ask_ai

def main():
    print("🚀 [3-Day Discovery] 启动最近3天全量大盘分析机 (AI + 教育)...")
    
    dates = ['2026-02-22', '2026-02-23', '2026-02-24']
    base_dir = '/root/.openclaw/workspace-writer/ai-article-publisher/data/hotnews/daily/'
    
    all_items = []
    
    for d in dates:
        for suffix in ['_unified.json', '.json', '_selected.json']:
            path = os.path.join(base_dir, f"{d}{suffix}")
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict) and 'items' in data:
                            all_items.extend(data['items'])
                        elif isinstance(data, list):
                            all_items.extend(data)
                        print(f"✅ 成功挂载矿池切片: {path}")
                    break
                except Exception as e:
                    pass
                    
    print(f"📡 成功拉取3天总矿池，总体量: {len(all_items)} 条底层数据数据。")
    
    ai_kws = ['大模型', 'AI', '人工智能', 'GPT', 'Sora', 'Gemini', 'Claude', '生成式', '智能体', 'Agent', '代码', '编程']
    edu_kws = ['教育', '学校', '老师', '教师', '学生', '大学', '文科', '理科', '辅导', '学习', '考试', '科研', '高等教育', '中小学', '课堂', '学霸', '清华', '北大', '斯坦福', '常春藤']
    
    filtered_items = []
    seen_titles = set()
    
    for t in all_items:
        title = str(t.get('title') or t.get('title_cn') or "")
        desc = str(t.get('description') or "")
        text = title + " " + desc
        
        if not title or title in seen_titles:
            continue
            
        has_ai = any(kw in text.upper() for kw in ai_kws)
        has_edu = any(kw in text for kw in edu_kws)
        
        if has_ai and has_edu:
            filtered_items.append({"title": title, "source": t.get('source_name', t.get('source', '网络'))})
            seen_titles.add(title)
            
    top_items = filtered_items[:50]
    
    print(f"🧹 漏斗过滤完成，沉淀出 {len(filtered_items)} 条纯粹的【AI + 教育】高热度交叉数据。正在唤醒主编级大模型...\n")
    
    prompt = f"""
    你是一个极其敏锐的晚点/虎嗅级科技商业主编，且对“AI技术与教育体系的历史性碰撞”有极深洞察。
    这是过去3天（2026-02-22至2026-02-24）从全网抓取的真实热点数据切片：
    {json.dumps(top_items, ensure_ascii=False)}
    
    请从中挖掘出 3 个具有极强爆发力、能刺穿家庭或行业焦虑的微信公众号深度长文选题。
    这3个选题不要停留于表面的“技术真神奇”，必须从社会阶层、教育倒挂、焦虑剥削、系统性塌方等极其锋利的角度切入。
    
    请严格且只输出纯 JSON 格式：
    {{
      "proposals": [
        {{
           "topic_name": "极其锋利、带隐喻悬念的主标题",
           "source_events": ["触发此选题的2-3条原始新闻事实说明"],
           "angle": "切入角度说明（如何刺穿行业伪装/戳中焦虑）",
           "pain_point": "打中的核心社会心理痛点",
           "expected_impact": 9,
           "difficulty": 8
        }}
      ]
    }}
    """
    
    res_str = ask_ai(prompt, "请且仅输出一段合法的 JSON 字符串，不要带 markdown 代码块套壳，不要包含任何多余文字。")
    print("=================== 原始 JSON 返回 ===================")
    print(res_str.strip())
    print("======================================================\n")

if __name__ == "__main__":
    main()
