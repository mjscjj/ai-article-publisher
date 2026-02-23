#!/usr/bin/env python3
"""
AI Article Publisher - 端到端工作流
热点采集 → 智能选题 → 内容创作 → 审查订正 → 草稿发布
"""

import json
import sys
import argparse
import subprocess
import os
from datetime import datetime
from typing import List, Dict, Optional

# 导入模块
sys.path.insert(0, '/root/.openclaw/workspace-writer/ai-article-publisher')
from topic_scorer import rank_topics
from reviewer import review_article, generate_fix_report

# 配置
PROJECT_DIR = "/root/.openclaw/workspace-writer/ai-article-publisher"
OUTPUT_DIR = f"{PROJECT_DIR}/output"

import json
import os

CONFIG_FILE = f"{PROJECT_DIR}/pipeline_config.json"
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        PIPELINE_CONFIG = json.load(f)
except Exception:
    PIPELINE_CONFIG = {"modules": {}}

FETCH_SCRIPT = "/root/.openclaw/workspace/skills/wemp-operator/scripts/content/fetch_news.py"

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)





try:
    from feishu_integration import send_to_feishu_for_review
except ImportError:
    send_to_feishu_for_review = None

try:
    from deep_research import execute_deep_research
except ImportError:
    execute_deep_research = None

# ============================================
# Phase 1: 热点采集
# ============================================

def phase1_collect(sources: List[str], limit: int = 10) -> List[Dict]:
    """采集热点"""
    print("\n" + "=" * 60)
    print("Phase 1: 热点采集")
    print("=" * 60)
    
    all_items = []
    
    for source in sources:
        try:
            cmd = ["python3", FETCH_SCRIPT, "--source", source, "--limit", str(limit)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                items = json.loads(result.stdout)
                all_items.extend(items)
                print(f"  [{source}] ✅ 获取 {len(items)} 条")
            else:
                print(f"  [{source}] ❌ 失败")
        except Exception as e:
            print(f"  [{source}] ❌ 错误: {str(e)[:30]}")
    
    print(f"\n采集总计: {len(all_items)} 条")
    return all_items

# ============================================
# Phase 2: 智能选题
# ============================================

def phase2_select(items: List[Dict], keywords: List[str], top_n: int = 5) -> List[Dict]:
    """智能选题"""
    print("\n" + "=" * 60)
    print("Phase 2: 智能选题")
    print("=" * 60)
    
    ranked = rank_topics(items, keywords, top_n=top_n)
    
    print(f"\n推荐选题 TOP {top_n}:")
    for i, topic in enumerate(ranked, 1):
        title = topic['title'][:40] + "..." if len(topic['title']) > 40 else topic['title']
        print(f"  {i}. {title}")
        print(f"     分数: {topic['total']} | {topic['recommendation']}")
    
    return ranked

# ============================================
# Phase 3: 内容创作 (模拟 - 实际使用 AI)
# ============================================

def phase3_create(topic: Dict, style: str = "技术干货", config: Dict = None) -> str:
    """创作内容（实际调用 AI）"""
    print("\n" + "=" * 60)
    print("Phase 3: 内容创作")
    
    if config and config.get("modules", {}).get("deep_research", False):
        print("🔍 触发 [Deep Research] 深度融合检索机制...")
        try:
            if execute_deep_research:
                research_material = execute_deep_research(topic, config)
                # 拿到丰富大纲！将研究材料混入 topic 的 description 中
                topic['description'] = research_material
            else:
                print("⚠️ 未找到 execute_deep_research 函数")
        except Exception as e:
            print(f"⚠️ [Deep Research] 运行失败，回退至普通创作: {e}")

    print("=" * 60)
    
    print(f"\n选题: {topic['title']}")
    print(f"风格: {style}")
    print("\n⏳ 正在创作... (实际使用 wechat-article-skill)")
    
    # 模拟生成的内容（实际应调用 AI）
    article = f"""
# {topic['title']}

## 引言

{topic['title']}是当前热门话题。本文将从多个角度分析这个问题。

## 核心观点

### 1. 背景介绍

随着技术的发展，这个领域正在快速变化。我们需要了解其基本概念和发展历程。

### 2. 关键分析

从专业角度来看，有几个关键点值得注意：
- 技术层面的创新
- 市场需求的变化
- 用户行为的转变

### 3. 实践建议

对于普通读者，以下是一些建议：
1. 持续学习新知识
2. 关注行业动态
3. 亲自实践验证

## 总结

{topic['title']}是一个值得深入探讨的话题。希望本文能给你带来启发。

---

*来源: {topic['source']}*
"""
    
    print(f"✅ 文章生成完成 ({len(article)} 字)")
    return article

# ============================================
# Phase 4: 审查订正
# ============================================

def phase4_review(article: str, auto_fix: bool = False, config: Dict = None) -> Dict:
    """审查文章"""
    print("\n" + "=" * 60)
    print("Phase 4: 审查订正")
    if config and config.get("modules", {}).get("multi_agent_review", False):
        print("👥 触发 [Multi-Agent Review] 多终端博弈模块... (Stub)")

    print("=" * 60)
    
    result = review_article(article, verbose=True)
    
    if not result["quality"]["can_publish"]:
        print("\n" + generate_fix_report(result))
    
    return result

# ============================================
# Phase 5: 发布准备
# ============================================

def phase5_prepare(article: str, topic: Dict, review_result: Dict, config: Dict = None) -> Dict:
    if config is None: config = {}
    modules = config.get("modules", {})
    
    # === 拦截逻辑: 如果启用了 Human in the loop, 走飞书审查 ===
    if modules.get("human_in_the_loop", False):
        try:
            from feishu_integration import send_to_feishu_for_review
            print("\n[工作流挂起] 🚨 触发 Human-in-the-loop 人工审查模块")
            task_file = send_to_feishu_for_review(article, topic.get("title", "未命名文章"))
            return {"status": "pending_human_review", "task_file": task_file, "message": "文章已发送至飞书等待发布指令。"}
        except ImportError:
            pass

    """发布准备"""
    print("\n" + "=" * 60)
    print("Phase 5: 发布准备")
    print("=" * 60)
    
    if not review_result["quality"]["can_publish"]:
        print("❌ 文章未通过审查，无法发布")
        return {"status": "failed", "reason": "审查未通过"}
    
    # 准备发布数据
    publish_data = {
        "title": topic['title'][:50],  # 标题限制
        "author": "AI Article Publisher",
        "digest": article[:120].replace('\n', ' '),
        "content": article,
        "source": topic.get('source', ''),
        "url": topic.get('url', ''),
        "quality_score": review_result["quality"]["score"],
        "timestamp": datetime.now().isoformat()
    }
    
    # 保存发布数据
    output_file = f"{OUTPUT_DIR}/publish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(publish_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 发布数据已准备")
    print(f"   标题: {publish_data['title']}")
    print(f"   摘要: {publish_data['digest'][:50]}...")
    print(f"   质量分: {publish_data['quality_score']}")
    print(f"\n📄 发布数据已保存: {output_file}")
    print("\n⚠️ 需要配置公众号凭据才能实际发布")
    print("   使用 wechat-article-skill 执行发布")
    
    return {"status": "ready", "file": output_file, "data": publish_data}

# ============================================
# 完整工作流
# ============================================

def run_full_workflow(
    sources: List[str],
    keywords: List[str],
    style: str = "技术干货",
    top_n: int = 5,
    auto_publish: bool = False
) -> Dict:
    """运行完整工作流"""
    
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " AI Article Publisher - 完整工作流 ".center(56) + "║")
    print("║" + f" {datetime.now().strftime('%Y-%m-%d %H:%M')} ".center(56) + "║")
    print("╚" + "═" * 58 + "╝")
    
    # Phase 1: 采集
    items = phase1_collect(sources, limit=10)
    if not items:
        return {"status": "failed", "phase": "collect", "error": "未采集到内容"}
    
    # Phase 2: 选题
    topics = phase2_select(items, keywords, top_n)
    if not topics:
        return {"status": "failed", "phase": "select", "error": "无合适选题"}
    
    # Phase 3: 创作（使用第一个选题）
    selected_topic = topics[0]
    article = phase3_create(selected_topic, style, PIPELINE_CONFIG)
    
    # Phase 4: 审查
    review_result = phase4_review(article, PIPELINE_CONFIG)
    
    # Phase 5: 发布准备
    publish_result = phase5_prepare(article, selected_topic, review_result, PIPELINE_CONFIG)
    
    # 总结
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " 工作流完成 ".center(56) + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║ 采集: {len(items)} 条 → 选题: {len(topics)} 个".ljust(59) + "║")
    print(f"║ 创作: {len(article)} 字 → 审查: {review_result['quality']['score']} 分".ljust(59) + "║")
    print(f"║ 状态: {publish_result['status']} ".ljust(59) + "║")
    print("╚" + "═" * 58 + "╝")
    
    return {
        "status": "success",
        "items_collected": len(items),
        "topics_selected": len(topics),
        "article_length": len(article),
        "quality_score": review_result["quality"]["score"],
        "publish_ready": review_result["quality"]["can_publish"],
        "publish_file": publish_result.get("file")
    }

# ============================================
# 主程序
# ============================================

def main():
    parser = argparse.ArgumentParser(description='AI Article Publisher 完整工作流')
    parser.add_argument('--sources', '-s', default='weibo,hackernews,github',
                       help='数据源（逗号分隔）')
    parser.add_argument('--keywords', '-k', default='AI,技术,学习',
                       help='关注关键词（逗号分隔）')
    parser.add_argument('--style', default='技术干货', help='写作风格')
    parser.add_argument('--top', '-n', type=int, default=5, help='选题数量')
    parser.add_argument('--auto', action='store_true', help='自动模式（跳过确认）')
    args = parser.parse_args()
    
    sources = [s.strip() for s in args.sources.split(',')]
    keywords = [k.strip() for k in args.keywords.split(',') if k.strip()]
    
    result = run_full_workflow(
        sources=sources,
        keywords=keywords,
        style=args.style,
        top_n=args.top,
        auto_publish=args.auto
    )
    
    # 保存结果
    result_file = f"{OUTPUT_DIR}/workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 工作流结果已保存: {result_file}")

if __name__ == '__main__':
    main()
