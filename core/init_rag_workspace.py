#!/usr/bin/env python3
"""
RAG 工作空间初始化脚本
创建专用的 ai-article-publisher 工作空间
"""

import requests
import json

BASE_URL = "http://43.134.234.4:3001"
API_KEY = "sk-WaUmgZsMxgeHOpp8SJxK1rmVQxiwfiDJ"

def create_workspace():
    """创建工作空间"""
    url = f"{BASE_URL}/api/v1/workspace"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": "AI Article Publisher",
        "slug": "ai-article-publisher"
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    
    print(f"状态码：{resp.status_code}")
    print(f"响应：{resp.text}")
    
    if resp.status_code in [200, 201]:
        result = resp.json()
        print(f"\n✅ 工作空间创建成功!")
        print(f"   ID: {result.get('id', 'N/A')}")
        print(f"   Name: {result.get('name', 'N/A')}")
        print(f"   Slug: {result.get('slug', 'N/A')}")
        return result
    else:
        print(f"\n❌ 工作空间创建失败")
        return None

if __name__ == "__main__":
    create_workspace()
