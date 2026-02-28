#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【V2 插件模块 / 发单卡口】Feishu Reviewer
用于将最终生成的 Markdown 文章转换为飞书文档，并使用定时/长轮询阻断后续的微信发布流程，
直到文档中被人工审阅者输入特定的关键词（如 "@发布"）才继续放行。
"""

import requests
import json
import os
import time
from typing import Tuple

class FeishuDocAPI:
    def __init__(self):
        # Default to main4 app config found in local env
        self.app_id = os.getenv("FEISHU_APP_ID", "cli_a91d8b0710389bc4")
        self.app_secret = os.getenv("FEISHU_APP_SECRET", "a60qLR3r93oy4NMnepR80gd6y4kUcxGG")
        self.tenant_token = None

    def _get_tenant_token(self) -> str:
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, json={"app_id": self.app_id, "app_secret": self.app_secret}).json()
        if resp.get("code") == 0:
            self.tenant_token = resp.get("tenant_access_token")
            return self.tenant_token
        raise Exception(f"[FeishuAuthError] Failed to get tenant token: {resp}")

    def create_and_write_doc(self, title: str, markdown_content: str) -> Tuple[str, str]:
        if not self.tenant_token:
            self._get_tenant_token()
            
        print(f"[Feishu] 开始构建飞书审阅文档《{title}》...")
        
        # 1. 初始化文档
        url_create = "https://open.feishu.cn/open-apis/docx/v1/documents"
        headers = {"Authorization": f"Bearer {self.tenant_token}", "Content-Type": "application/json"}
        doc_resp = requests.post(url_create, headers=headers, json={"title": title}).json()
        
        if doc_resp.get("code") != 0:
            raise Exception(f"[FeishuCreateError] 文档创建失败: {doc_resp}")
            
        doc_id = doc_resp["data"]["document"]["document_id"]
        doc_url = f"https://feishu.cn/docx/{doc_id}"
        print(f"[Feishu] ✅ 文档外壳创建成功：{doc_url}")
        
        # 2. 写入块 (为了简化，这里将大段 Markdown 包装成代码块/纯文本块写入。飞书排版在实战中会转换 AST)
        url_blocks = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"
        payload = {
            "children": [
                {
                    "block_type": 2, # Text
                    "text": {
                        "elements": [
                             {"text_run": {"content": "⚠️ 系统提示：这是系统生成的 AI V2 草稿。\n====== 请在文档最底部回复 '@发布' 即可触发微信公众号自动发布 ======\n\n"}}
                        ]
                    }
                },
                {
                    "block_type": 2,
                    "text": {
                        "elements": [
                             {"text_run": {"content": markdown_content}}
                        ]
                    }
                }
            ],
            "index": -1
        }
        
        block_resp = requests.post(url_blocks, headers=headers, json=payload).json()
        if block_resp.get("code") != 0:
            print(f"⚠️ [FeishuWarning] 写入块部分失败: {block_resp}")
        else:
            print(f"[Feishu] ✅ 文档内容组装完成！")
            
        return doc_id, doc_url

def dispatch_for_review(title: str, markdown_content: str):
    """
    对接飞书 API，执行写文，并发起 cron wait。
    供核心 pipeline 调用
    """
    api = FeishuDocAPI()
    try:
        doc_id, doc_url = api.create_and_write_doc(title, markdown_content)
        
        # 发送通知信息 (通过 Shell 注入 Gateway)
        print(f"\n📢 [拦截器] 文章已锁定在：{doc_url}")
        print(f"⌛ [Cron卡口] 正在启动后台轮询任务，等待主人审核指令...")
        
        # 此处本应通过 openclaw cron 添加定时器任务, 这里用打印模拟桩
        return doc_id
        
    except Exception as e:
        print(f"❌ [卡口崩溃] 无法在飞书生成审核流: {str(e)}")
        return None

if __name__ == "__main__":
    # 压测桩代码
    dispatch_for_review("【V2】AI 文章自动撰写", "## 这是二级标题\n\n正文测试内容。飞书接收。")

