#!/usr/bin/env python3
"""
统一数据调度器
协调所有采集器按时运行

作者: AI Article Publisher
创建时间: 2026-02-23
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def run_collector(name: str, script: str) -> Dict[str, Any]:
    """运行采集器"""
    print(f"\n{'='*50}")
    print(f"🚀 运行: {name}")
    print(f"{'='*50}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ['python3', script],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        elapsed = time.time() - start_time
        success = result.returncode == 0
        
        return {
            "name": name,
            "script": script,
            "success": success,
            "elapsed": round(elapsed, 2),
            "output": result.stdout[-500:] if result.stdout else "",
            "error": result.stderr[-500:] if result.stderr else ""
        }
    except subprocess.TimeoutExpired:
        return {
            "name": name,
            "script": script,
            "success": False,
            "elapsed": 300,
            "error": "Timeout after 300s"
        }
    except Exception as e:
        return {
            "name": name,
            "script": script,
            "success": False,
            "elapsed": 0,
            "error": str(e)
        }


def run_all_collectors() -> Dict[str, Any]:
    """运行所有采集器"""
    collectors = [
        ("DailyHotApi 热榜", "sources/dailyhot_collector.py"),
        ("RSSHub 扩展", "sources/extended_collectors_v2.py"),
        ("视频热门", "sources/video_collector.py"),
        ("图文内容", "sources/content_collector.py"),
        ("热词采集", "sources/hotword_collector.py"),
    ]
    
    results = {
        "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "collectors": {},
        "summary": {
            "total": len(collectors),
            "success": 0,
            "failed": 0,
            "total_time": 0
        }
    }
    
    for name, script in collectors:
        result = run_collector(name, script)
        results['collectors'][name] = result
        results['summary']['total_time'] += result['elapsed']
        
        if result['success']:
            results['summary']['success'] += 1
            print(f"✅ {name} 完成 ({result['elapsed']}s)")
        else:
            results['summary']['failed'] += 1
            print(f"❌ {name} 失败: {result['error'][:50]}")
    
    results['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return results


def save_run_report(results: Dict, output_dir: str = "data/reports"):
    """保存运行报告"""
    os.makedirs(output_dir, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    report_file = f"{output_dir}/run_{today}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return report_file


def print_summary(results: Dict):
    """打印摘要"""
    print(f"\n{'='*60}")
    print(f"📊 运行摘要")
    print(f"{'='*60}")
    print(f"开始时间: {results['start_time']}")
    print(f"结束时间: {results['end_time']}")
    print(f"总耗时: {results['summary']['total_time']}s")
    print(f"成功: {results['summary']['success']}/{results['summary']['total']}")
    print(f"{'='*60}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 统一数据调度器")
    print("="*60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行所有采集器
    results = run_all_collectors()
    
    # 打印摘要
    print_summary(results)
    
    # 保存报告
    report_file = save_run_report(results)
    print(f"\n📁 报告已保存: {report_file}")


if __name__ == '__main__':
    main()