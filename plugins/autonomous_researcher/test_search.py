#!/usr/bin/env python3
import sys
import os

# 把上一级目录加到路径以便引入大语言模型
sys.path.append("/root/.openclaw/workspace-writer/ai-article-publisher/core")
from llm_client import ask_ai
from researcher_cn import AutonomousResearcherCN

def run_test():
    print("==================================================")
    print("🔥 正在启动 V3 国内三轨探针测试 (Triad-CN Researcher)")
    print("==================================================\n")
    
    # 实例化我们的中国版研究特工，给它装载局域网内的 GPT-4o-mini 或 Gemini 作为大脑
    agent = AutonomousResearcherCN(llm_callable=ask_ai)
    
    # 我们抛出一个极具商业张力、且需要结合最新热点的数据命题
    test_topic = "2025年年轻人为什么都在逃离一线城市回老家考公？真实收入和生存现状"
    
    # 启动全自动打捞和 AI 反思聚合
    fact_pack = agent.run(test_topic)
    
    print("\n✅ 测试结束。如果以上过程没有发生致命报错，并成功打印出了多视角的 Fact-Pack，说明当前的搜索能力链条（AI拆词 -> 并发爬取 -> 洗稿 -> 压制汇聚）在无代理裸连的情况下是完全连通且可用的！")

if __name__ == "__main__":
    run_test()
