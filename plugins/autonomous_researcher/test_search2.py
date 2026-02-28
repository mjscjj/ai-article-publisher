#!/usr/bin/env python3
import sys
import os

sys.path.append("/root/.openclaw/workspace-writer/ai-article-publisher/core")
from llm_client import ask_ai
from researcher import AutonomousResearcher

def run_test():
    print("==================================================")
    print("🔥 正在启动 V3 外网深海探针测试 (Duckduckgo Researcher)")
    print("==================================================\n")
    
    # max_depth=2 会让它强行去爬取第二层（如果AI觉得第一层没干货）
    agent = AutonomousResearcher(llm_callable=ask_ai, max_depth=2, max_urls_per_query=2)
    test_topic = "马斯克收购X(推特)后的2025年真实营收数据和裁员后遗症"
    
    agent.run(test_topic)

if __name__ == "__main__":
    run_test()
