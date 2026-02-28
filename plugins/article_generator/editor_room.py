#!/usr/bin/env python3
"""
B-3 editor_room.py
毒舌主编 Ping-Pong Loop：最多 2 轮审查与改写。
"""

import json
import os
import re
from typing import Any, Dict

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")

# ============================
# 【主编视角代码区块】
# ============================
EDITOR_SYSTEM_PROMPT = (
    "你是挑剔的虎嗅主编，寻找文章废话与假大空。如果完美请返回带有【过审】二个字的JSON。"
    "\n输出必须是严格 JSON，格式示例："
    "{\"verdict\":\"【过审】\",\"issues\":[],\"rewrite_hint\":\"\"}"
    "\n若未过审：verdict 写【退回】，issues 用要点列出问题，rewrite_hint 给出具体改法。"
    "\n禁止输出除 JSON 外的任何文本。"
)

# ============================
# 【改写者视角区块】
# ============================
REWRITER_SYSTEM_PROMPT = (
    "你是资深改写者。依据主编的 JSON 意见对原文进行原地重构改写："
    "删除空话套话、压缩冗余、保留信息密度和逻辑清晰度。"
    "只输出改写后的完整正文，不要解释。"
)


def _call_llm(messages) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return ""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
    }
    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _safe_json_load(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except Exception:
        # 尝试提取第一个 JSON 块
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return {}


def _is_passed(editor_json: Dict[str, Any]) -> bool:
    verdict = str(editor_json.get("verdict", ""))
    raw = json.dumps(editor_json, ensure_ascii=False)
    return "过审" in verdict or "过审" in raw


def _fallback_editor_review(draft: str) -> Dict[str, Any]:
    # 简易启发式：出现典型空话则退回
    bad_phrases = ["然而在这个瞬息万变的时代", "值得注意的是", "不可忽视", "赋能", "生态", "引领"]
    hit = [p for p in bad_phrases if p in draft]
    if not hit:
        return {"verdict": "【过审】", "issues": [], "rewrite_hint": ""}
    return {
        "verdict": "【退回】",
        "issues": [f"存在空话套话：{', '.join(hit)}"],
        "rewrite_hint": "删掉无信息量的口号，直接给出事实与判断。",
    }


def _editor_review(draft: str) -> Dict[str, Any]:
    raw = _call_llm([
        {"role": "system", "content": EDITOR_SYSTEM_PROMPT},
        {"role": "user", "content": f"以下为待审稿件：\n{draft}"},
    ])
    if not raw:
        return _fallback_editor_review(draft)
    parsed = _safe_json_load(raw)
    return parsed if parsed else _fallback_editor_review(draft)


def _fallback_rewrite(draft: str, feedback: Dict[str, Any]) -> str:
    # 极简降级：去掉常见空话
    for p in ["然而在这个瞬息万变的时代", "值得注意的是", "不可忽视", "赋能", "生态", "引领"]:
        draft = draft.replace(p, "")
    return re.sub(r"\s+", " ", draft).strip()


def _rewrite_with_feedback(draft: str, feedback: Dict[str, Any]) -> str:
    raw = _call_llm([
        {"role": "system", "content": REWRITER_SYSTEM_PROMPT},
        {"role": "user", "content": "原文：\n" + draft},
        {"role": "user", "content": "主编意见(JSON)：\n" + json.dumps(feedback, ensure_ascii=False)},
    ])
    if not raw:
        return _fallback_rewrite(draft, feedback)
    return raw.strip()


def enter_editor_room(draft: str) -> str:
    """
    Ping-pong Loop：主编审查 -> 退回改写 -> 再审查，最多 2 轮。
    返回最终稿件（过审或达到最大轮次）。
    """
    current = draft
    for _ in range(2):
        feedback = _editor_review(current)
        if _is_passed(feedback):
            return current
        current = _rewrite_with_feedback(current, feedback)
    return current


if __name__ == "__main__":
    demo = (
        "然而在这个瞬息万变的时代，AI 正在赋能各行各业，"
        "值得注意的是这场变革不可忽视，它将引领一个全新的生态。"
    )
    first_feedback = _editor_review(demo)
    if _is_passed(first_feedback):
        print("主编反馈:", json.dumps(first_feedback, ensure_ascii=False))
        print("过审稿件:\n", demo)
    else:
        print("主编修改意见:", json.dumps(first_feedback, ensure_ascii=False))
        polished = enter_editor_room(demo)
        print("改后稿件:\n", polished)
