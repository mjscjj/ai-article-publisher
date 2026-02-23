"""
飞书审查集成模块 (Human-in-the-loop)
用于生成飞书文档并监听人类审查意见
"""
import os
import json
import time

def send_to_feishu_for_review(article_md: str, title: str) -> str:
    # 模拟把内容发给飞书。由于真正对接飞书需要AppSecret或通过网关，
    # 我们这里可以通过一个桥接文件，通知OpenClaw的守护Agent去处理。
    print(f"🔄 正在通过 OpenClaw 桥接发送到飞书文档...")
    
    # 将需求写入一个队列文件，由外面的 OpenClaw Agent 读取并执行 feishu_doc 动作
    task = {
        "action": "create_feishu_doc",
        "title": title,
        "content": article_md,
        "status": "pending",
        "timestamp": time.time()
    }
    
    os.makedirs("output/tasks", exist_ok=True)
    task_file = f"output/tasks/feishu_review_{int(time.time())}.json"
    with open(task_file, "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False)
        
    print(f"✅ 飞书文档创建请求已挂起 ({task_file})")
    print(f"👉 （需配置 OpenClaw 监控助手读取该任务并调用 feishu_doc 插件）")
    
    return task_file

def check_feishu_doc_status(task_file: str) -> bool:
    """检查文档人类是否已经审核通过"""
    if not os.path.exists(task_file):
        return False
    with open(task_file, "r", encoding="utf-8") as f:
        task = json.load(f)
    if task.get("status") == "approved":
        return True
    return False
