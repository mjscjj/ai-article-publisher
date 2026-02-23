#!/usr/bin/env python3
"""
Main Agent 进度检查脚本
每 30 分钟执行一次，共 8 次
"""

import json
import os
import sys
from datetime import datetime, timedelta

STATE_FILE = "/root/.openclaw/workspace-writer/monitor_state.json"
MEMORY_FILE = "/root/.openclaw/workspace-writer/memory/2026-02-21.md"

def load_state():
    """加载监控状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_state(state):
    """保存监控状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def check_progress(state):
    """检查子代理进度"""
    print(f"\n{'='*60}")
    print(f"🔍 Main Agent 进度检查 #{state['completedChecks'] + 1}/{state['totalChecks']}")
    print(f"{'='*60}\n")
    
    # 检查项目文件是否有更新
    project_dir = "/root/.openclaw/workspace-writer/ai-article-publisher"
    
    files_to_check = [
        "pipeline.py",
        "reviewer.py", 
        "topic_scorer.py",
        "hotnews_storage.py",
        "multi_publish.js"
    ]
    
    print("📁 检查文件状态...")
    for f in files_to_check:
        filepath = os.path.join(project_dir, f)
        if os.path.exists(filepath):
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            print(f"  ✅ {f} - 最后修改: {mtime.strftime('%H:%M:%S')}")
        else:
            print(f"  ❌ {f} - 不存在")
    
    # 检查输出目录
    output_dir = os.path.join(project_dir, "output")
    if os.path.exists(output_dir):
        outputs = os.listdir(output_dir)
        print(f"\n📝 输出文件: {len(outputs)} 个")
        for o in outputs[:5]:
            print(f"  - {o}")
    
    # 更新检查次数
    state['completedChecks'] += 1
    state['lastCheckTime'] = datetime.now().isoformat()
    
    if state['completedChecks'] < state['totalChecks']:
        next_check = datetime.now() + timedelta(minutes=state['intervalMinutes'])
        state['nextCheckTime'] = next_check.isoformat()
        print(f"\n⏰ 下次检查: {next_check.strftime('%H:%M')}")
    else:
        state['status'] = 'completed'
        print(f"\n✅ 所有检查完成！")
    
    save_state(state)
    
    # 生成催促消息
    elapsed = (datetime.now() - datetime.fromisoformat(state['startTime'])).total_seconds() / 60
    elapsed = int(elapsed)
    
    message = f"""
🔔 Main Agent 进度检查 #{state['completedChecks']}/{state['totalChecks']}

你已经工作了 {elapsed} 分钟！

{'✅ 所有检查已完成！' if state['status'] == 'completed' else '请继续完成以下任务：'}

- 检查并修复 pipeline.py 的 bug
- 完善 reviewer.py 的审查逻辑
- 测试 multi_publish.js 的发布功能
- 更新项目文档

{'任务完成！' if state['status'] == 'completed' else '如有问题，请立即报告。'}
"""
    
    print(message)
    return message

def main():
    state = load_state()
    if not state:
        print("❌ 未找到监控状态文件")
        sys.exit(1)
    
    if state['status'] == 'completed':
        print("✅ 监控任务已完成")
        sys.exit(0)
    
    check_progress(state)

if __name__ == "__main__":
    main()
