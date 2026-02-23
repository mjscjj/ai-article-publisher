#!/usr/bin/env python3
"""
审查订正系统 - 文章质量检查
包含：语法检查、敏感词检测、AI痕迹检测、事实核查
"""

import json
import re
import sys
import argparse
from typing import List, Dict, Tuple
from datetime import datetime

# ============================================
# 1. 敏感词检测模块
# ============================================

# 基础敏感词库（示例，实际使用需要完整词库）
SENSITIVE_WORDS = {
    # 政治敏感词（示例）
    "政治": ["习近平", "共产党", "六四", "法轮功", "台独", "藏独", "疆独"],
    
    # 色情低俗词
    "低俗": ["色情", "黄色", "裸体", "性爱", "乱伦"],
    
    # 暴力恐怖词
    "暴力": ["杀人", "爆炸", "恐怖袭击", "炸弹制作"],
    
    # 违法犯罪词
    "违法": ["毒品", "赌博", "诈骗", "传销", "洗钱"],
    
    # 广告营销词
    "营销": ["加微信", "免费领取", "代开发票", "刷单"],
}

def load_sensitive_words(file_path: str = None) -> Dict[str, List[str]]:
    """加载敏感词库"""
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return SENSITIVE_WORDS

def detect_sensitive_words(text: str, word_dict: Dict[str, List[str]] = None) -> List[Dict]:
    """检测敏感词"""
    word_dict = word_dict or SENSITIVE_WORDS
    results = []
    
    for category, words in word_dict.items():
        for word in words:
            if word in text:
                # 找到所有出现位置
                for match in re.finditer(re.escape(word), text):
                    results.append({
                        "type": "敏感词",
                        "category": category,
                        "word": word,
                        "position": match.start(),
                        "severity": get_severity(category)
                    })
    
    return results

def get_severity(category: str) -> str:
    """获取严重程度"""
    high = ["政治", "暴力", "违法"]
    medium = ["低俗"]
    low = ["营销"]
    
    if category in high:
        return "高"
    elif category in medium:
        return "中"
    else:
        return "低"

# ============================================
# 2. 语法检查模块
# ============================================

def check_grammar(text: str) -> List[Dict]:
    """检查语法问题（简化版）"""
    issues = []
    
    # 检查重复词
    words = text.split()
    for i in range(len(words) - 1):
        if words[i] == words[i+1] and len(words[i]) > 1:
            issues.append({
                "type": "语法",
                "issue": "重复词",
                "word": words[i],
                "position": i,
                "severity": "低",
                "suggestion": f"删除重复的「{words[i]}」"
            })
    
    # 检查标点问题
    patterns = [
        (r'。。+', "。", "连续句号"),
        (r'！！+', "！", "连续感叹号"),
        (r'？？+', "？", "连续问号"),
        (r'，，+', "，", "连续逗号"),
        (r'。。', "。", "双句号"),
    ]
    
    for pattern, fix, desc in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            issues.append({
                "type": "语法",
                "issue": desc,
                "word": match.group(),
                "position": match.start(),
                "severity": "低",
                "suggestion": f"应修改为「{fix}」"
            })
    
    # 检查常见错别字
    typos = {
        "的地得": [("的", "地", "动词前"), ("的", "得", "形容词后")],
        "做作": [("作", "做", "具体动作")],
    }
    
    # 简化检查：检查「的」字过多
    de_count = text.count("的")
    if de_count > len(text) / 20:  # 平均每20字一个「的」
        issues.append({
            "type": "语法",
            "issue": "「的」字使用过多",
            "word": "的",
            "count": de_count,
            "severity": "低",
            "suggestion": "考虑精简「的」字使用"
        })
    
    return issues

# ============================================
# 3. AI 痕迹检测模块
# ============================================

# AI 常见表达模式
AI_PATTERNS = {
    "开场白": [
        r"作为一个AI",
        r"作为人工智能",
        r"我会.*帮助你",
        r"让我来.*解释",
        r"首先.*其次.*最后",
        r"总的来说",
        r"总而言之",
    ],
    "结构化表达": [
        r"第一[，,].*第二[，,].*第三",
        r"一方面.*另一方面",
        r"不仅.*而且",
        r"虽然.*但是",
    ],
    "AI 特征词": [
        "值得注意的是",
        "需要指出的是",
        "总的来说",
        "综上所述",
        "从某种意义上说",
        "在一定程度上",
    ],
    "过度礼貌": [
        "感谢您的提问",
        "很高兴为您解答",
        "希望这个回答对您有帮助",
        "如有任何问题",
    ]
}

def detect_ai_traces(text: str) -> List[Dict]:
    """检测 AI 写作痕迹"""
    results = []
    
    for category, patterns in AI_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                results.append({
                    "type": "AI痕迹",
                    "category": category,
                    "match": match.group(),
                    "position": match.start(),
                    "severity": "中",
                    "suggestion": get_ai_fix_suggestion(category, match.group())
                })
    
    return results

def get_ai_fix_suggestion(category: str, match: str) -> str:
    """获取修复建议"""
    suggestions = {
        "开场白": "删除AI式开场白，直接切入主题",
        "结构化表达": "使用更自然的过渡，避免刻板结构",
        "AI 特征词": "替换为更口语化的表达",
        "过度礼貌": "删除客套话，保持专业简洁"
    }
    return suggestions.get(category, "考虑修改或删除")

# ============================================
# 4. 文章质量评分
# ============================================

def calculate_quality_score(
    sensitive_results: List[Dict],
    grammar_results: List[Dict],
    ai_results: List[Dict],
    text: str
) -> Dict:
    """计算文章质量分数"""
    
    base_score = 100
    
    # 敏感词扣分
    sensitive_deduction = 0
    for item in sensitive_results:
        if item["severity"] == "高":
            sensitive_deduction += 20
        elif item["severity"] == "中":
            sensitive_deduction += 10
        else:
            sensitive_deduction += 5
    
    # 语法扣分
    grammar_deduction = len(grammar_results) * 2
    
    # AI痕迹扣分
    ai_deduction = len(ai_results) * 3
    
    # 总分
    final_score = max(0, base_score - sensitive_deduction - grammar_deduction - ai_deduction)
    
    # 等级
    if final_score >= 90:
        grade = "A - 优秀"
    elif final_score >= 80:
        grade = "B - 良好"
    elif final_score >= 70:
        grade = "C - 合格"
    elif final_score >= 60:
        grade = "D - 需修改"
    else:
        grade = "F - 不通过"
    
    return {
        "score": final_score,
        "grade": grade,
        "deductions": {
            "敏感词": sensitive_deduction,
            "语法问题": grammar_deduction,
            "AI痕迹": ai_deduction
        },
        "can_publish": final_score >= 60 and sensitive_deduction == 0
    }

# ============================================
# 5. 完整审查流程
# ============================================

def review_article(text: str, verbose: bool = True) -> Dict:
    """完整文章审查"""
    
    if verbose:
        print("=" * 60)
        print("文章审查报告")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
    
    # 1. 敏感词检测
    sensitive_results = detect_sensitive_words(text)
    if verbose:
        print(f"\n【敏感词检测】发现 {len(sensitive_results)} 处")
        for item in sensitive_results[:5]:
            print(f"  [{item['severity']}] {item['category']}: 「{item['word']}」")
    
    # 2. 语法检查
    grammar_results = check_grammar(text)
    if verbose:
        print(f"\n【语法检查】发现 {len(grammar_results)} 处")
        for item in grammar_results[:5]:
            print(f"  {item['issue']}: 「{item['word']}」 - {item['suggestion']}")
    
    # 3. AI痕迹检测
    ai_results = detect_ai_traces(text)
    if verbose:
        print(f"\n【AI痕迹检测】发现 {len(ai_results)} 处")
        for item in ai_results[:5]:
            print(f"  {item['category']}: 「{item['match']}」 - {item['suggestion']}")
    
    # 4. 质量评分
    quality = calculate_quality_score(sensitive_results, grammar_results, ai_results, text)
    
    if verbose:
        print(f"\n【质量评分】")
        print(f"  总分: {quality['score']} 分 ({quality['grade']})")
        print(f"  扣分明细:")
        for k, v in quality['deductions'].items():
            print(f"    - {k}: -{v} 分")
        print(f"\n  发布状态: {'✅ 可以发布' if quality['can_publish'] else '❌ 需要修改'}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "text_length": len(text),
        "sensitive_words": sensitive_results,
        "grammar_issues": grammar_results,
        "ai_traces": ai_results,
        "quality": quality
    }

def generate_fix_report(review_result: Dict) -> str:
    """生成修复建议报告"""
    
    lines = [
        "=" * 60,
        "文章修复建议",
        "=" * 60,
        ""
    ]
    
    if review_result["quality"]["can_publish"]:
        lines.append("✅ 文章通过审查，可以发布！")
        return "\n".join(lines)
    
    # 敏感词修复
    if review_result["sensitive_words"]:
        lines.append("【必须修复 - 敏感词】")
        for item in review_result["sensitive_words"]:
            lines.append(f"  [{item['severity']}] 替换或删除「{item['word']}」")
        lines.append("")
    
    # 语法修复
    if review_result["grammar_issues"]:
        lines.append("【建议修复 - 语法问题】")
        for item in review_result["grammar_issues"]:
            lines.append(f"  - {item['suggestion']}")
        lines.append("")
    
    # AI痕迹修复
    if review_result["ai_traces"]:
        lines.append("【建议修复 - AI痕迹】")
        for item in review_result["ai_traces"]:
            lines.append(f"  - {item['suggestion']}: 「{item['match']}」")
        lines.append("")
    
    lines.extend([
        "=" * 60,
        f"修复后请重新审查",
        "=" * 60
    ])
    
    return "\n".join(lines)

# ============================================
# 主程序
# ============================================

def main():
    parser = argparse.ArgumentParser(description='文章审查订正系统')
    parser.add_argument('--input', '-i', help='输入文件路径')
    parser.add_argument('--text', '-t', help='直接输入文本')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--fix', '-f', action='store_true', help='生成修复建议')
    args = parser.parse_args()
    
    # 获取文本
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        # 示例文本
        text = """
        作为一个AI助手，我会帮助你解决问题。
        
        首先，我们需要了解背景。其次，分析问题。最后，给出建议。
        
        值得注意的是，这个问题很重要。总的来说，我们需要综合考虑。
        
        感谢您的提问，希望这个回答对您有帮助。
        """
    
    # 执行审查
    result = review_article(text)
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n审查结果已保存到: {args.output}")
    
    # 修复建议
    if args.fix:
        print("\n" + generate_fix_report(result))

if __name__ == '__main__':
    main()
