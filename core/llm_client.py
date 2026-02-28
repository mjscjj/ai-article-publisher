#!/usr/bin/env python3
"""
【V4 核心】统一 AI 调用客户端 (SDK)
正式换装 Kimi-2.5 (moonshot/kimi-k2.5) 引擎。
原生支持 Thinking (深度思考/推理模式)。
"""
import json
import os
import urllib.request

AI_BASE_URL = "https://api.moonshot.cn/v1/chat/completions"
# 直连 Moonshot 基座
# API Key 应从环境变量读取：export MOONSHOT_API_KEY="sk-xxx"
AI_BASE_KEY = os.environ.get("MOONSHOT_API_KEY", "sk-tjG07oY0FqrzooJ8ymKVJeoLeGY8AuMORFjQATO2RdNmFmQw")

def ask_ai(prompt: str, system_prompt: str = "") -> str:
    """
    使用 Kimi-2.5 驱动端到端管线
    强制开启原生 Thinking (深度思考/推理模式) 行为。
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_BASE_KEY}"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
        
    data = {
        "model": "kimi-k2.5",
        "messages": messages
        # Kimi-2.5 requires default temperature (1.0), so we drop it
    }
    
    try:
        req = urllib.request.Request(
            AI_BASE_URL,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
            if "choices" in result and len(result["choices"]) > 0:
                msg = result["choices"][0]["message"]
                
                content = msg.get("content", "")
                reasoning = msg.get("reasoning_content", "")
                
                final_output = ""
                if reasoning:
                    final_output += f"【🧠 Kimi 2.5 内部推演回路 (Thinking...)】\n> " + "\n> ".join(reasoning.splitlines()) + "\n\n"
                    final_output += "【🖋️ Kimi 2.5 最终执行出稿】\n"
                
                final_output += content
                return final_output
            else:
                return f"API 异常: {result}"
    except Exception as e:
        return f"调用失败: {str(e)}"
