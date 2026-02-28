#!/usr/bin/env python3
"""
【 Autonomous Researcher (Triad-CN Version) 】
结合中国互联网生态特性的三轨制智能特工。
负责把大命题拆解为 3 条并行的情报航线：
1. 宏观政策/官媒 (Baidu MCP)
2. C端痛点/情绪共鸣 (Xiaohongshu MCP)
3. 行业杠精/高知社群 (RSSHub Zhihu/36kr)
"""
import json
import re

# 引入我们刚才创建的供应商
from providers.baidu_mcp import BaiduProvider
from providers.xiaohongshu_mcp import XiaohongshuProvider
from providers.rsshub import RSSHubProvider

class AutonomousResearcherCN:
    def __init__(self, llm_callable):
        self.llm = llm_callable
        self.baidu = BaiduProvider()
        self.xhs = XiaohongshuProvider()
        self.rss = RSSHubProvider()
        
    def _generate_triad_queries(self, topic):
        """让 AI 针对这三大护法产出特定角度的搜索词"""
        sys = "你是顶级的内容操盘手。返回合法的 JSON 对象。不准回答除了 JSON 以外的多余文字。"
        prompt = f"""
任务：为新商业文章【{topic}】配置三大社交阵地（百度新闻、小红书、知乎全网）的定向爆破搜索词。

百度：用于搜宏观政策、行业投融资（专业冰冷词汇）。
小红书：用于搜 C 端打工人的情绪共鸣、吐槽、搞钱或避坑（大白话情绪词汇）。
知乎：提取高赞的装逼金句与行业黑话（思辨型问题）。

返回格式:
{{
  "baidu": ["宏观词1"],
  "xiaohongshu": ["情绪词1"],
  "zhihu": ["思辨词1"]
}}
"""
        try:
            res = self.llm(prompt, sys)
            match = re.search(r'\{.*\}', res, re.S)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            print("拆词JSON出错", e)
        return {"baidu": [f"{topic} 政策趋势"], "xiaohongshu": [f"{topic} 焦虑真实体验"], "zhihu": [f"如何看待 {topic}"]}

    def _synthesize(self, topic, kb_data: dict):
        """将三轨情报压制为一炉"""
        raw_str = f"""
【百度新闻/官方来源】
{" / ".join(kb_data.get('baidu', []))}

【小红书真实痛点/避坑】
{" / ".join(kb_data.get('xiaohongshu', []))}

【知乎/行业深潜争论】
{" / ".join(kb_data.get('zhihu', []))}
"""
        prompt = f"这是系统爬虫从国内三大平台强行带回的关于【{topic}】的多维碎片：\n{raw_str[:15000]}\n\n【任务】请精炼成 4-6 条极具中国职场或商业切肤之痛的新闻事实/痛点包（Fact-Pack）。必须体现宏观冰冷对比个体伤痛的撕裂感。不准废话。"
        sys = "你是深网金牌编辑。"
        return self.llm(prompt, sys)

    def run(self, topic):
        print(f"\n🚀 [Autonomous Researcher Triad-CN] V3-三轨制国内探针组群启动！命题：{topic}")
        queries = self._generate_triad_queries(topic)
        print(f"🎯 AI 多维爆破指令已下达：\n  [百度] 扫雷词 -> {queries.get('baidu')}\n  [小红书] 情绪词 -> {queries.get('xiaohongshu')}\n  [知乎] 杠精词 -> {queries.get('zhihu')}\n")

        kb = {"baidu": [], "xiaohongshu": [], "zhihu": []}
        
        # 1. Baidu
        print(f"  🕷️ (轨迹 1) 启动 Baidu MCP 探测官媒/宏观面...")
        for q in queries.get("baidu", []):
            res = self.baidu.search(q)
            if isinstance(res, list): kb["baidu"].extend(res)
            
        # 2. 小红书
        print(f"  🕷️ (轨迹 2) 启动 Xiaohongshu MCP 收割打工人破防情绪...")
        for q in queries.get("xiaohongshu", []):
            res = self.xhs.search(q)
            if isinstance(res, list): kb["xiaohongshu"].extend(res)
            
        # 3. 知乎 RSS
        print(f"  🕷️ (轨迹 3) 启动 RSSHub 引擎抓取知乎高赞深文...")
        for q in queries.get("zhihu", []):
            res = self.rss.search(category="zhihu")
            if isinstance(res, list): kb["zhihu"].extend(res)
            
        print("\n🏭 [数据汇总] 宏观政策+个人痛点+专家争论 -> 开始跨平台熔炼...")
        fact_pack = self._synthesize(topic, kb)
        print("✅ =============== 终极三维调研包 (Triad Fact-Pack) ===============")
        print(fact_pack)
        print("=================================================================\n")
        return fact_pack

def test_cn_researcher():
    import sys
    sys.path.append("/root/.openclaw/workspace-writer/ai-article-publisher/core")
    from llm_client import ask_ai
    # 模拟一次实战命题
    r = AutonomousResearcherCN(llm_callable=ask_ai)
    r.run("人工智能大模型对教育文科专业的冲击真实痛点")

if __name__ == "__main__":
    test_cn_researcher()
