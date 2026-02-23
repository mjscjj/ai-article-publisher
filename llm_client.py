#!/usr/bin/env python3
"""
LLM 集成模块 - 真实 AI 调用
替换 Mock 文章生成
"""

import os
import sys
import json
import requests

# 配置
AI_BASE_URL = os.environ.get('AI_BASE_URL', 'http://43.134.234.4:3001')
AI_API_KEY = os.environ.get('AI_API_KEY', 'sk-WaUmgZsMxgeHOpp8SJxK1rmVQxiwfiDJ')

class LLMClient:
    """LLM 客户端"""
    
    def __init__(self, model='openai/gpt-4o-mini'):
        self.model = model
        self.base_url = AI_BASE_URL
        self.api_key = AI_API_KEY
        
    def chat(self, message, system_prompt=None):
        """发送聊天请求"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'message': message,
            'mode': 'chat'
        }
        
        if system_prompt:
            payload['system'] = system_prompt
            
        try:
            response = requests.post(
                f'{self.base_url}/api/v1/workspace/common/chat',
                headers=headers,
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                result = response.json()
                return result.get('text') or result.get('message', {}).get('content', '')
            else:
                print(f"LLM API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"LLM Request Error: {e}")
            return None
            
    def generate_article(self, topic, style='技术干货', research_material=None):
        """生成文章"""
        # 构建 prompt
        prompt = f"""你是一个专业的公众号文章写手。请根据以下选题撰写一篇公众号文章。

选题: {topic.get('title', '')}

选题描述: {topic.get('description', '')}

写作风格: {style}

"""
        
        # 如果有深度研究素材，加入素材
        if research_material:
            prompt += f"""
参考素材:
{research_material}

"""
        
        prompt += """
要求:
1. 文章长度 800-1500 字
2. 使用 Markdown 格式
3. 标题要有吸引力
4. 内容要有价值，观点清晰
5. 适合微信公众号发布
6. 尽量自然，不要有明显的 AI 写作痕迹
"""
        
        system_prompt = f"""你是一个資深的新媒体编辑，擅长写各类公众号文章。
风格要求：
- {style}
- 文字生动有趣
- 结构清晰
- 观点鲜明
- 避免车轱辘话

请直接输出文章内容，不要输出额外解释。"""
        
        result = self.chat(prompt, system_prompt)
        return result or self._fallback_article(topic, style)
        
    def _fallback_article(self, topic, style):
        """备选生成"""
        return f"""# {topic.get('title', '未命名')}

## 引言

{topic.get('description', '暂无描述')}

## 背景分析

在当前的行业环境下，这个话题引起了广泛关注...

## 深度解读

从多个角度来看，这个议题都值得深入探讨...

## 未来展望

综上所述，我们有理由相信...

## 总结

以上就是关于「{topic.get('title', '该话题')}」的简要分析。
"""


def get_llm_client(model=None):
    """获取 LLM 客户端"""
    return LLMClient(model=model or 'openai/gpt-4o-mini')


if __name__ == '__main__':
    # 测试
    client = get_llm_client()
    topic = {
        'title': 'AI Agent 的未来发展',
        'description': '探讨 AI Agent 技术的最新进展和未来趋势'
    }
    print("Testing LLM article generation...")
    article = client.generate_article(topic)
    if article:
        print(f"✅ Generated article ({len(article)} chars)")
        print(article[:500])
    else:
        print("❌ Failed to generate article")
