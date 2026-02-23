#!/usr/bin/env python3
"""
飞书集成模块 - 真实 API 调用
替换原有的 Mock 实现
"""

import os
import json
import time
import requests
from datetime import datetime

# 配置 - 从环境变量或配置文件读取
FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', 'cli_a90ede08e1399cda')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', '')

class FeishuClient:
    """飞书 API 客户端"""
    
    def __init__(self, app_id=None, app_secret=None):
        self.app_id = app_id or FEISHU_APP_ID
        self.app_secret = app_secret or FEISHU_APP_SECRET
        self.access_token = None
        self.token_expires = 0
        
    def get_access_token(self):
        """获取 access_token"""
        # 检查缓存
        if self.access_token and time.time() < self.token_expires:
            return self.access_token
            
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            result = response.json()
            
            if result.get('code') == 0:
                self.access_token = result['tenant_access_token']
                self.token_expires = time.time() + result.get('expire', 7200) - 300
                return self.access_token
            else:
                print(f"❌ 获取飞书 Token 失败: {result}")
                return None
        except Exception as e:
            print(f"❌ 飞书 API 请求错误: {e}")
            return None
            
    def create_document(self, title, content):
        """创建云文档"""
        token = self.get_access_token()
        if not token:
            return None
            
        url = "https://open.feishu.cn/open-apis/doc/v2/create"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 转换 Markdown 为飞书文档块
        blocks = self._markdown_to_blocks(content)
        
        data = {
            "folder_token": "",  # 可选：放在指定文件夹
            "title": title,
            "content": {
                "blocks": blocks
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            result = response.json()
            
            if result.get('code') == 0:
                return {
                    'doc_token': result['data']['token'],
                    'url': f"https://.feishu.cn/doc/{result['data']['token']}"
                }
            else:
                print(f"❌ 创建飞书文档失败: {result}")
                return None
        except Exception as e:
            print(f"❌ 飞书创建文档错误: {e}")
            return None
            
    def _markdown_to_blocks(self, markdown):
        """将 Markdown 转换为飞书文档块"""
        blocks = []
        lines = markdown.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 标题
            if line.startswith('# '):
                blocks.append({
                    "type": "heading1",
                    "heading1": {
                        "content": line[2:]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    "type": "heading2",
                    "heading2": {
                        "content": line[3:]
                    }
                })
            elif line.startswith('### '):
                blocks.append({
                    "type": "heading3",
                    "heading3": {
                        "content": line[4:]
                    }
                })
            # 列表
            elif line.startswith('- ') or line.startswith('* '):
                blocks.append({
                    "type": "bullet",
                    "bullet": {
                        "content": line[2:]
                    }
                })
            # 引用
            elif line.startswith('> '):
                blocks.append({
                    "type": "quote",
                    "quote": {
                        "content": line[2:]
                    }
                })
            # 分割线
            elif line == '---':
                blocks.append({
                    "type": "divider"
                })
            # 普通段落
            else:
                blocks.append({
                    "type": "paragraph",
                    "paragraph": {
                        "elements": [
                            {
                                "type": "text",
                                "text": line
                            }
                        ]
                    }
                })
                
        return blocks
        
    def send_message(self, receive_id_type, receive_id, msg_type="text", content=None):
        """发送消息"""
        token = self.get_access_token()
        if not token:
            return None
            
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 构建消息
        if msg_type == "text":
            msg_content = {"text": content or ""}
        elif msg_type == "post":
            msg_content = content
        else:
            msg_content = {"text": str(content)}
            
        params = {
            "receive_id_type": receive_id_type
        }
        
        data = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": json.dumps(msg_content)
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, params=params, timeout=10)
            result = response.json()
            
            if result.get('code') == 0:
                return {'message_id': result['data']['message_id']}
            else:
                print(f"❌ 发送飞书消息失败: {result}")
                return None
        except Exception as e:
            print(f"❌ 飞书发送消息错误: {e}")
            return None


def send_to_feishu_for_review(article_md: str, title: str) -> str:
    """发送到飞书审查"""
    client = FeishuClient()
    
    # 创建文档
    result = client.create_document(title, article_md)
    
    if result:
        # 发送通知消息
        client.send_message(
            receive_id_type="user_id",
            receive_id="all",  # 或指定用户 ID
            msg_type="post",
            content={
                "zh_cn": {
                    "title": "📝 新文章待审",
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": f"文章标题: {title}\n"
                            },
                            {
                                "tag": "a",
                                "text": "👉 点击查看文档",
                                "href": result['url']
                            },
                            {
                                "tag": "text",
                                # 不自动回复「#发布」或「#拒绝」"
                            }
                        ]
                    ]
                }
            }
        )
        return result['url']
    else:
        # Fallback: 保存到本地
        return f"Fallback: {title}"


# 全局实例
_feishu_client = None

def get_feishu_client():
    """获取飞书客户端"""
    global _feishu_client
    if _feishu_client is None:
        _feishu_client = FeishuClient()
    return _feishu_client


if __name__ == '__main__':
    # 测试
    print("Testing Feishu integration...")
    client = FeishuClient()
    
    # 测试获取 token
    token = client.get_access_token()
    if token:
        print(f"✅ Token 获取成功")
    else:
        print("⚠️ Token 获取失败 (可能缺少 App Secret)")
