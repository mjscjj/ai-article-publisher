"""Article Generator V2 - writer_agents.py

并行织肉厂：将三段大纲并发写作后拼接为完整初稿。
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List

try:
    import httpx
except Exception:  # pragma: no cover - optional dependency
    httpx = None  # type: ignore


OPENROUTER_API_KEY = "sk-or-v1-3592..."  # placeholder (replace in runtime env if needed)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
CHEAP_FALLBACK_MODEL = "openai/gpt-4o-mini"


def _build_prompt(section: Dict[str, Any], fact_pack: Dict[str, Any]) -> str:
    name = section.get("name", "未命名小节")
    guidance = section.get("guidance", "")
    quote_req = section.get("quote_req", "")
    facts = json.dumps(fact_pack, ensure_ascii=False)
    return (
        "你是一个专业写作助理，负责撰写文章的一个小节。"
        f"\n\n【小节标题】{name}"
        f"\n【写作方向】{guidance}"
        f"\n【必须引用的上游事实】{quote_req}"
        "\n\n【资料包】\n"
        f"{facts}\n\n"
        "请输出该小节的完整正文，语言自然、信息密度高。"
    )


async def _worker_write(section: Dict[str, Any], fact_pack: Dict[str, Any]) -> str:
    """单段写作 worker。若缺少 httpx，则模拟并发耗时。"""

    prompt = _build_prompt(section, fact_pack)

    if httpx is None:
        await asyncio.sleep(0.2)
        return f"[MOCK正文] {section.get('name', '未命名小节')}\n{prompt[:120]}..."

    payload = {
        "model": CHEAP_FALLBACK_MODEL,
        "messages": [
            {"role": "system", "content": "你是高效写作者。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # fallback to mock on error
            await asyncio.sleep(0.2)
            return f"[MOCK正文-异常兜底] {section.get('name','未命名小节')} ({exc})"


async def parallel_drafting(outline: Dict[str, Any], fact_pack: Dict[str, Any]) -> str:
    """并发生成 3 个小节正文并拼接返回"""

    sections: List[Dict[str, Any]] = outline.get("sections", [])
    if len(sections) != 3:
        raise ValueError("outline['sections'] 长度必须为 3")

    tasks = [
        _worker_write(sections[0], fact_pack),
        _worker_write(sections[1], fact_pack),
        _worker_write(sections[2], fact_pack),
    ]
    part1, part2, part3 = await asyncio.gather(*tasks)
    return "\n\n".join([part1, part2, part3])


if __name__ == "__main__":
    mock_outline = {
        "title": "示例标题",
        "sections": [
            {"name": "开篇", "guidance": "引出话题", "quote_req": "引用事实 A"},
            {"name": "中段", "guidance": "展开论证", "quote_req": "引用事实 B"},
            {"name": "结尾", "guidance": "总结与展望", "quote_req": "引用事实 C"},
        ],
    }
    mock_fact_pack = {"facts": ["事实 A", "事实 B", "事实 C"]}
    print(asyncio.run(parallel_drafting(mock_outline, mock_fact_pack)))
