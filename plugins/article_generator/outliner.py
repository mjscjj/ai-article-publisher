#!/usr/bin/env python3
"""
B-1 outliner.py
依据 docs/V2_Research_And_Architecture/tech_module_details.md 规范：
- 输入：Fact-Pack dict
- 调用 LLM 一次生成 JSON Outline (title + 3 sections)
"""

import json
import os
import re
import requests
from typing import Dict, Any

# Moonshot API (Kimi-2.5)
AI_BASE_URL = "https://api.moonshot.cn/v1/chat/completions"
MODEL = "kimi-k2.5"

SYSTEM_PROMPT = (
    "你是一个冷酷的新闻骨架解剖手。必须输出严格的 JSON。"
    "格式必须为："
    "{\"title\": \"<标题>\", "
    "\"sections\": ["
    "{\"name\": \"<小节标题>\", "
    "\"guidance\": \"<写作方向>\", "
    "\"quote_req\": \"<必须引用的上游事实>\"}"
    "]}"
    "要求：sections 恰好 3 个，且每条都强关联 fact_pack 中的事实点。"
    "禁止输出除 JSON 外的任何文本。"
)


def _fallback_outline(fact_pack: Dict[str, Any], reason: str = "") -> Dict[str, Any]:
    title = (
        fact_pack.get("title")
        or fact_pack.get("topic")
        or fact_pack.get("headline")
        or "待定标题"
    )
    facts = fact_pack.get("facts") or fact_pack.get("items") or []
    def _pick(i: int) -> str:
        if isinstance(facts, list) and len(facts) > i:
            return str(facts[i])[:120]
        return "上游事实点未提供，需从 Fact-Pack 抽取"

    return {
        "title": title,
        "sections": [
            {
                "name": "现状与触发",
                "guidance": "交代事件背景与触发原因，强调时间线。",
                "quote_req": _pick(0),
            },
            {
                "name": "核心矛盾",
                "guidance": "拆解争议点或冲突逻辑，指出分歧。",
                "quote_req": _pick(1),
            },
            {
                "name": "影响与走向",
                "guidance": "评估影响范围与下一步走向预测。",
                "quote_req": _pick(2),
            },
        ],
        "_fallback": True,
        "_reason": reason,
    }


def _call_llm_once(fact_pack: Dict[str, Any]) -> str:
    api_key = os.environ.get("MOONSHOT_API_KEY") or "sk-tjG07oY0FqrzooJ8ymKVJeoLeGY8AuMORFjQATO2RdNmFmQw"

    user_prompt = (
        "基于以下 Fact-Pack 生成骨架。"\
        "Fact-Pack JSON：\n" + json.dumps(fact_pack, ensure_ascii=False)
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }

    resp = requests.post(AI_BASE_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _extract_json_from_response(raw: str) -> str:
    """从 LLM 响应中提取 JSON（处理前后缀废话）"""
    # 尝试匹配完整的 JSON 对象
    match = re.search(r'\{[\s\S]*\}', raw)
    if match:
        return match.group(0)
    # 如果没有找到，返回原始内容（让 json.loads 失败并触发降级）
    return raw.strip()


def generate_outline(fact_pack: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据 Fact-Pack 生成文章骨架。
    必须调用一次大模型；若无法调用则返回降级 Mock。
    """
    api_key = os.environ.get("MOONSHOT_API_KEY")
    if not api_key:
        return _fallback_outline(fact_pack, reason="MOONSHOT_API_KEY 未设置")

    try:
        raw = _call_llm_once(fact_pack)
        # 提取 JSON（处理 LLM 可能输出的前后缀）
        json_str = _extract_json_from_response(raw)
        outline = json.loads(json_str)
        
        # 验证结构
        if not isinstance(outline, dict):
            raise ValueError("outline 不是 dict")
        if "title" not in outline:
            raise ValueError("outline 缺少 title 字段")
        if "sections" not in outline or not isinstance(outline["sections"], list):
            raise ValueError("outline 缺少 sections 字段")
        
        return outline
    except Exception as e:
        print(f"[Outliner] ⚠️ LLM 解析失败：{e}")
        return _fallback_outline(fact_pack, reason=f"LLM 失败：{e}")


if __name__ == "__main__":
    # 桩测试
    demo_fact_pack = {
        "title": "AI 模型价格战升级",
        "facts": [
            "多家厂商在本周宣布下调 API 价格 30%-50%",
            "开发者社区对成本下降反响热烈，但担心服务稳定性",
            "行业分析称价格战可能导致小厂出清",
        ],
    }
    outline = generate_outline(demo_fact_pack)
    print(json.dumps(outline, ensure_ascii=False, indent=2))
