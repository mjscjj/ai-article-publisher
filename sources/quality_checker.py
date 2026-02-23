#!/usr/bin/env python3
"""
数据质量检测器
检测采集数据的质量、去重、完整性

作者: AI Article Publisher
创建时间: 2026-02-23
"""

import json
import os
from datetime import datetime
from collections import Counter
from typing import Dict, List, Any


def check_data_quality(data: Dict) -> Dict[str, Any]:
    """检测数据质量"""
    issues = []
    stats = {
        "total": 0,
        "valid": 0,
        "invalid": 0,
        "duplicates": 0,
        "missing_fields": {}
    }
    
    items = data.get('items', data.get('videos', data.get('contents', [])))
    stats['total'] = len(items)
    
    seen_titles = set()
    required_fields = ['title', 'url', 'platform']
    
    for item in items:
        # 检查必填字段
        missing = [f for f in required_fields if not item.get(f)]
        if missing:
            stats['invalid'] += 1
            for f in missing:
                stats['missing_fields'][f] = stats['missing_fields'].get(f, 0) + 1
            continue
        
        # 检查重复
        title = item.get('title', '')
        if title in seen_titles:
            stats['duplicates'] += 1
        else:
            seen_titles.add(title)
            stats['valid'] += 1
    
    # 生成问题报告
    if stats['invalid'] > stats['total'] * 0.1:
        issues.append(f"无效数据比例过高: {stats['invalid']}/{stats['total']}")
    
    if stats['duplicates'] > stats['total'] * 0.2:
        issues.append(f"重复数据比例过高: {stats['duplicates']}/{stats['total']}")
    
    return {
        "stats": stats,
        "issues": issues,
        "quality_score": round(stats['valid'] / max(stats['total'], 1) * 100, 2)
    }


def analyze_all_data(data_dir: str = "data") -> Dict[str, Any]:
    """分析所有数据质量"""
    report = {
        "analyze_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "sources": {},
        "summary": {
            "total_items": 0,
            "avg_quality": 0
        }
    }
    
    # 检查各类数据
    data_files = {
        "dailyhot": f"{data_dir}/hotnews/daily/{datetime.now().strftime('%Y-%m-%d')}_dailyhot.json",
        "rsshub": f"{data_dir}/hotnews/daily/{datetime.now().strftime('%Y-%m-%d')}_extended.json",
        "videos": f"{data_dir}/videos/{datetime.now().strftime('%Y-%m-%d')}.json",
        "contents": f"{data_dir}/contents/{datetime.now().strftime('%Y-%m-%d')}.json",
        "hotwords": f"{data_dir}/hotwords/{datetime.now().strftime('%Y-%m-%d')}.json"
    }
    
    quality_scores = []
    total_items = 0
    
    for source_name, file_path in data_files.items():
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            quality = check_data_quality(data)
            report['sources'][source_name] = {
                "file": file_path,
                "total": quality['stats']['total'],
                "valid": quality['stats']['valid'],
                "quality_score": quality['quality_score'],
                "issues": quality['issues']
            }
            
            total_items += quality['stats']['total']
            quality_scores.append(quality['quality_score'])
    
    report['summary']['total_items'] = total_items
    report['summary']['avg_quality'] = round(sum(quality_scores) / max(len(quality_scores), 1), 2) if quality_scores else 0
    
    return report


def print_quality_report(report: Dict):
    """打印质量报告"""
    print(f"\n{'='*60}")
    print(f"📊 数据质量报告")
    print(f"{'='*60}")
    print(f"分析时间: {report['analyze_time']}")
    print(f"总数据量: {report['summary']['total_items']} 条")
    print(f"平均质量: {report['summary']['avg_quality']}%")
    print(f"{'='*60}\n")
    
    for source, info in report['sources'].items():
        status = "✅" if info['quality_score'] >= 90 else "⚠️" if info['quality_score'] >= 70 else "❌"
        print(f"{status} {source}: {info['total']} 条, 质量 {info['quality_score']}%")
        if info['issues']:
            for issue in info['issues']:
                print(f"   ⚠️ {issue}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("📊 数据质量检测器")
    print("="*60)
    
    # 分析数据
    report = analyze_all_data()
    
    # 打印报告
    print_quality_report(report)
    
    # 保存报告
    os.makedirs("data/reports", exist_ok=True)
    report_file = f"data/reports/quality_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 报告已保存: {report_file}")


if __name__ == '__main__':
    main()