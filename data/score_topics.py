import json
import sys
import os

# 确保能 import core.llm_client
sys.path.append('/root/.openclaw/workspace-writer/ai-article-publisher')
from core.llm_client import ask_ai

topics = [
    "专家称AI时代文科比理科吃香",
    "谷歌教育推出新计划，将为美国600万教师提供免费Gemini培训",
    "刘维户口本只剩自己，花3个月片酬用AI生成家人团聚，看哭全网！",
    "00后华裔天才造AI月老，斯坦福5000名学霸脱单上瘾！全美十大名校疯抢",
    "《飞驰人生3》张弛宇强战胜AI加持的赛车，「人定胜AI」思潮会成为新时代的愚公移山精神吗？"
]

prompt_template = """
你是一个资深的新媒体爆款推手。请根据[新闻价值(news_value), 用户契合度(user_match), 预期影响(expected_impact), 写作难度(difficulty), 竞争度(competition)]五个维度(满分均为10分)对以下微信公众号选题进行打分。
综合分(overall_score)为5个维度的加权平均*10(满分100)。
请返回纯JSON结果，严格遵循以下结构：
{
  "topics": [
    {
       "title": "...",
       "dimensions": {
          "news_value": 0,
          "user_match": 0,
          "expected_impact": 0,
          "difficulty": 0,
          "competition": 0
       },
       "overall_score": 0,
       "analysis": "10-15字的简评"
    }
  ]
}
待打分选题列表：
""" + json.dumps(topics, ensure_ascii=False)

res = ask_ai(prompt_template, "你必须严格只输出合法的JSON。")
print(res)
