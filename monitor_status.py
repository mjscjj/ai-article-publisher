#!/usr/bin/env python3
"""
项目状态监控脚本
定时检查项目状态并记录
"""

import os
import sys
import json
import subprocess
from datetime import datetime

PROJECT_DIR = "/root/.openclaw/workspace-writer/ai-article-publisher"

def check_project_status():
    """检查项目状态"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # 1. 检查关键文件是否存在
    files_to_check = [
        'pipeline.py',
        'pipeline_config.json',
        'data_store.py',
        'deep_research.py',
        'feishu_integration.py',
        'api_server.py',
        'tests/api/test_pipeline_api.py',
        'tests/e2e/test_ui_e2e.py'
    ]
    
    for f in files_to_check:
        path = f"{PROJECT_DIR}/{f}"
        status['checks'][f] = os.path.exists(path)
        
    # 2. 检查数据存储
    db_path = f"{PROJECT_DIR}/data/articles.db"
    status['checks']['database'] = os.path.exists(db_path)
    
    # 3. 运行语法检查
    try:
        result = subprocess.run(
            ['python3', '-m', 'py_compile', f'{PROJECT_DIR}/pipeline.py'],
            capture_output=True,
            timeout=10
        )
        status['checks']['pipeline_syntax'] = result.returncode == 0
    except:
        status['checks']['pipeline_syntax'] = False
        
    # 4. 检查 API 服务器
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:8899/health'],
            capture_output=True,
            timeout=5
        )
        status['checks']['api_server'] = b'ok' in result.stdout
    except:
        status['checks']['api_server'] = False
        
    # 5. 统计测试用例数量
    try:
        # API 测试
        with open(f"{PROJECT_DIR}/tests/api/test_pipeline_api.py", 'r') as f:
            api_test_content = f.read()
            status['checks']['api_test_cases'] = api_test_content.count('def test_')
            
        # E2E 测试
        with open(f"{PROJECT_DIR}/tests/e2e/test_ui_e2e.py", 'r') as f:
            e2e_test_content = f.read()
            status['checks']['e2e_test_cases'] = e2e_test_content.count('def test_')
    except:
        status['checks']['api_test_cases'] = 0
        status['checks']['e2e_test_cases'] = 0
        
    # 6. 检查输出目录
    output_dir = f"{PROJECT_DIR}/output"
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        status['checks']['output_files'] = len(files)
    else:
        status['checks']['output_files'] = 0
        
    return status


def main():
    print("="*60)
    print(f"🔍 项目状态检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    status = check_project_status()
    
    # 打印状态
    print("\n📋 检查结果:")
    for key, value in status['checks'].items():
        icon = "✅" if value else "❌"
        print(f"  {icon} {key}: {value}")
        
    # 保存状态
    os.makedirs(f"{PROJECT_DIR}/output", exist_ok=True)
    status_file = f"{PROJECT_DIR}/output/monitor_status.json"
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    print(f"\n📁 状态已保存: {status_file}")
    
    # 总结
    passed = sum(1 for v in status['checks'].values() if v)
    total = len(status['checks'])
    print(f"\n📊 通过率: {passed}/{total} ({passed*100//total}%)")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
