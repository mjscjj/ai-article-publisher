#!/usr/bin/env python3
"""
智能选题分析器
使用 LLM 进行选题质量评估、写作建议生成

⚠️ 成本控制: 使用 OpenRouter DeepSeek R1 免费模型
   模型: openrouter/deepseek/deepseek-r1-0528:free
   别名: deepseek-free
   费用: $0 (免费)

作者: AI Article Publisher
创建时间: 2026-02-22
"""

import json
import os
import sys
import argparse
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import re

# ============================================
# 成本控制配置
# ============================================
# 使用 OpenRouter DeepSeek R1 免费模型
# 模型 ID: openrouter/deepseek/deepseek-r1-0528:free
# 别名: deepseek-free
# 费用: 完全免费
# 限制: 可能有请求频率限制

LLM_CONFIG = {
    "provider": "openrouter",
    "model": "stepfun/step-3.5-flash:free",  # 免费模型 (更快的模型)
    "alias": "step-3.5-flash-free",
    "api_url": "https://openrouter.ai/api/v1/chat/completions",
    "cost_per_1k_tokens": 0.0,  # 免费
    "max_tokens": 4096,
    "temperature": 0.7,
}

# 从环境变量获取 API Key
# 设置方式: export OPENROUTER_API_KEY="your-key"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")


def call_llm(
    prompt: str,
    system_prompt: str = "",
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    """
    调用 LLM API
    
    ⚠️ 使用 DeepSeek R1 免费模型
    成本: $0
    """
    if not OPENROUTER_API_KEY:
        return '{"error": "未配置 OPENROUTER_API_KEY，请设置环境变量"}'
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/ai-article-publisher",
        "X-Title": "AI Article Publisher",
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": LLM_CONFIG["model"],
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    try:
        req = Request(
            LLM_CONFIG["api_url"],
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        
        with urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return json.dumps({"error": f"API 响应异常: {result}"})
                
    except Exception as e:
        return json.dumps({"error": f"API 调用失败: {str(e)}"})


def analyze_topic(
    topic: Dict,
    user_profile: Dict = None,
) -> Dict:
    """
    分析单个选题
    
    Args:
        topic: 选题信息 {title, source, score, ...}
        user_profile: 用户画像 {domains, style, audience, ...}
    
    Returns:
        分析结果 {score, analysis, angles, risks, ...}
    """
    user_profile = user_profile or {
        "domains": ["教育", "心理学", "AI"],
        "style": "深度分析",
        "audience": "职场人士、教育工作者",
    }
    
    system_prompt = """你是一位资深的内容运营专家，擅长选题策划和内容策略。
你的任务是分析选题的价值、可行性和写作建议。
请用 JSON 格式输出分析结果。"""

    prompt = f"""# 选题分析任务

## 选题信息
- 标题: {topic.get('title', '')}
- 来源: {topic.get('source', '')}
- 热度: {topic.get('score', '未知')}
- 分类: {topic.get('category', '未知')}

## 用户画像
- 专业领域: {', '.join(user_profile.get('domains', []))}
- 写作风格: {user_profile.get('style', '通用')}
- 目标受众: {user_profile.get('audience', '通用')}

## 分析要求
请从以下维度分析这个选题:

1. **新闻价值** (1-10分)
   - 时效性、重要性、影响力

2. **用户匹配度** (1-10分)
   - 与用户领域的相关性
   - 写作风格适配度

3. **竞争分析** (1-10分, 高分=竞争少)
   - 同选题文章数量
   - 差异化机会

4. **写作难度** (1-10分, 高分=易写)
   - 资料获取难度
   - 专业门槛

5. **预期效果** (1-10分)
   - 预计阅读量
   - 传播潜力

6. **写作角度建议** (3个角度)
   - 具体切入点
   - 标题建议

7. **风险提示**
   - 敏感点
   - 时效风险

## 输出格式
```json
{{
  "overall_score": 85,
  "dimensions": {{
    "news_value": 8,
    "user_match": 9,
    "competition": 7,
    "difficulty": 8,
    "expected_impact": 7
  }},
  "analysis": "一句话总结分析",
  "writing_angles": [
    {{"angle": "角度1", "title": "建议标题1"}},
    {{"angle": "角度2", "title": "建议标题2"}},
    {{"angle": "角度3", "title": "建议标题3"}}
  ],
  "risks": ["风险1", "风险2"],
  "recommendation": "强烈推荐/推荐/可以考虑/不推荐"
}}
```

请直接输出 JSON，不要有其他内容。"""

    response = call_llm(prompt, system_prompt)
    
    # 解析 JSON
    try:
        # 尝试提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(response)
        
        # 添加原始选题信息
        result["topic"] = topic.get("title", "")
        result["source"] = topic.get("source", "")
        result["model"] = LLM_CONFIG["alias"]
        result["cost"] = "$0 (免费)"
        
        return result
        
    except json.JSONDecodeError:
        return {
            "topic": topic.get("title", ""),
            "error": "JSON 解析失败",
            "raw_response": response,
            "model": LLM_CONFIG["alias"],
        }


def rank_topics(
    topics: List[Dict],
    user_profile: Dict = None,
    top_n: int = 10,
) -> List[Dict]:
    """
    批量分析并排序选题
    
    Args:
        topics: 选题列表
        user_profile: 用户画像
        top_n: 返回数量
    
    Returns:
        排序后的选题列表
    """
    print(f"\n{'='*60}")
    print(f"智能选题分析")
    print(f"{'='*60}")
    print(f"模型: {LLM_CONFIG['model']}")
    print(f"费用: 免费 ($0)")
    print(f"候选选题: {len(topics)} 个")
    print(f"{'='*60}\n")
    
    results = []
    
    for i, topic in enumerate(topics[:top_n * 2]):  # 分析 2 倍数量
        print(f"[{i+1}/{min(len(topics), top_n*2)}] 分析: {topic.get('title', '')[:30]}...")
        
        result = analyze_topic(topic, user_profile)
        
        if "error" not in result:
            results.append(result)
            print(f"    ✅ 评分: {result.get('overall_score', 0)} - {result.get('recommendation', '')}")
        else:
            print(f"    ❌ 分析失败: {result.get('error', '')}")
        
        # 避免触发频率限制
        if i < len(topics) - 1:
            time.sleep(1)
    
    # 按综合评分排序
    results.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
    
    return results[:top_n]


def generate_report(results: List[Dict], output_format: str = "text") -> str:
    """生成分析报告"""
    
    if output_format == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    # 文本报告
    lines = [
        "=" * 70,
        "智能选题分析报告",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"模型: {LLM_CONFIG['alias']} (免费)",
        "=" * 70,
        "",
    ]
    
    for i, result in enumerate(results, 1):
        lines.append(f"【{i}】{result.get('topic', '未知选题')}")
        lines.append(f"    来源: {result.get('source', '未知')}")
        lines.append(f"    综合评分: {result.get('overall_score', 0)} ({result.get('recommendation', '')})")
        
        dims = result.get("dimensions", {})
        if dims:
            lines.append(f"    维度: 新闻{dims.get('news_value', 0)} | 匹配{dims.get('user_match', 0)} | "
                        f"竞争{dims.get('competition', 0)} | 难度{dims.get('difficulty', 0)} | "
                        f"效果{dims.get('expected_impact', 0)}")
        
        lines.append(f"    分析: {result.get('analysis', '')}")
        
        angles = result.get("writing_angles", [])
        if angles:
            lines.append("    写作角度:")
            for angle in angles[:2]:
                lines.append(f"      - {angle.get('angle', '')}: {angle.get('title', '')}")
        
        risks = result.get("risks", [])
        if risks:
            lines.append(f"    风险: {', '.join(risks[:2])}")
        
        lines.append("")
    
    lines.extend([
        "=" * 70,
        "说明:",
        "- 综合评分 80+ : 强烈推荐",
        "- 综合评分 70+ : 推荐",
        "- 综合评分 60+ : 可以考虑",
        "- 综合评分 <60 : 不推荐",
        "",
        f"成本: $0 (使用免费模型 {LLM_CONFIG['alias']})",
        "=" * 70,
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='智能选题分析器')
    parser.add_argument('--input', '-i', help='输入JSON文件路径')
    parser.add_argument('--output', '-o', default='text', choices=['text', 'json'], help='输出格式')
    parser.add_argument('--top', '-n', type=int, default=5, help='输出数量')
    parser.add_argument('--domains', '-d', default='教育,心理学,AI', help='用户关注领域(逗号分隔)')
    parser.add_argument('--style', '-s', default='深度分析', help='写作风格')
    args = parser.parse_args()
    
    # 解析用户画像
    user_profile = {
        "domains": [d.strip() for d in args.domains.split(',')],
        "style": args.style,
        "audience": "职场人士、教育工作者",
    }
    
    # 读取输入
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            topics = json.load(f)
    else:
        # 示例数据
        topics = [
            {
                "title": "AI 编程助手对比：Claude vs GPT-4",
                "source": "少数派",
                "score": "10万阅读",
                "category": "科技",
            },
            {
                "title": "心理学研究：压力与认知的关系",
                "source": "ScienceDaily",
                "score": "高热度",
                "category": "心理学",
            },
            {
                "title": "如何提高学习效率？5个实用方法",
                "source": "知乎",
                "score": "5000赞同",
                "category": "教育",
            },
        ]
    
    # 分析排序
    results = rank_topics(topics, user_profile, top_n=args.top)
    
    # 输出报告
    report = generate_report(results, args.output)
    print(report)
    
    # 保存报告
    if args.input:
        output_file = args.input.replace('.json', '_analyzed.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存: {output_file}")


if __name__ == '__main__':
    main()