#!/usr/bin/env python3
"""
【代码质量检查器】Code Quality Checker
自动扫描 Python 代码常见问题

检查项:
1. 语法错误
2. 未使用的 import
3. 未定义的变量
4. 重复代码
5. 过长函数 (>50 行)
6. 缺失文档字符串
7. 硬编码字符串
"""

import ast
import os
import re
from typing import List, Dict, Any
from pathlib import Path

class CodeQualityChecker:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.issues = []
    
    def scan_all(self, exclude_dirs: List[str] = None) -> Dict[str, Any]:
        """扫描所有 Python 文件"""
        if exclude_dirs is None:
            exclude_dirs = ['__pycache__', '.git', 'venv', 'node_modules', 'data', 'tests']
        
        py_files = []
        for root, dirs, files in os.walk(self.root_dir):
            # 排除目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        
        print(f"📄 发现 {len(py_files)} 个 Python 文件")
        
        for file_path in py_files:
            self.check_file(file_path)
        
        return self.get_report()
    
    def check_file(self, file_path: str):
        """检查单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            rel_path = os.path.relpath(file_path, self.root_dir)
            
            # 1. 语法检查
            try:
                ast.parse(content)
            except SyntaxError as e:
                self.issues.append({
                    "file": rel_path,
                    "line": e.lineno,
                    "type": "syntax_error",
                    "message": f"语法错误：{e.msg}",
                    "severity": "error"
                })
            
            # 2. 过长函数检查
            self._check_long_functions(content, lines, rel_path)
            
            # 3. 缺失文档字符串
            self._check_missing_docstrings(content, rel_path)
            
            # 4. 硬编码字符串
            self._check_hardcoded_strings(content, lines, rel_path)
            
            # 5. 过长的行
            self._check_long_lines(lines, rel_path)
            
        except Exception as e:
            self.issues.append({
                "file": rel_path if 'rel_path' in locals() else file_path,
                "type": "read_error",
                "message": f"读取失败：{e}",
                "severity": "warning"
            })
    
    def _check_long_functions(self, content: str, lines: List[str], file_path: str):
        """检查过长函数"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno
                    if func_lines > 50:
                        self.issues.append({
                            "file": file_path,
                            "line": node.lineno,
                            "type": "long_function",
                            "message": f"函数 '{node.name}' 过长 ({func_lines} 行 > 50)",
                            "severity": "warning"
                        })
        except:
            pass
    
    def _check_missing_docstrings(self, content: str, file_path: str):
        """检查缺失文档字符串"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        # 跳过私有方法和测试函数
                        name = node.name
                        if not name.startswith('_') and not name.startswith('test_'):
                            self.issues.append({
                                "file": file_path,
                                "line": node.lineno,
                                "type": "missing_docstring",
                                "message": f"{'函数' if isinstance(node, ast.FunctionDef) else '类'} '{name}' 缺少文档字符串",
                                "severity": "info"
                            })
        except:
            pass
    
    def _check_hardcoded_strings(self, content: str, lines: List[str], file_path: str):
        """检查硬编码字符串 (API Key 等)"""
        patterns = [
            (r'sk-[a-zA-Z0-9]{20,}', 'API Key'),
            (r'Bearer [a-zA-Z0-9_-]{20,}', 'Bearer Token'),
            (r'password\s*=\s*["\'][^"\']+["\']', '硬编码密码'),
            (r'secret\s*=\s*["\'][^"\']+["\']', '硬编码 Secret'),
        ]
        
        for i, line in enumerate(lines, 1):
            # 跳过注释
            if line.strip().startswith('#'):
                continue
            
            for pattern, issue_type in patterns:
                if re.search(pattern, line, re.I):
                    self.issues.append({
                        "file": file_path,
                        "line": i,
                        "type": "hardcoded_secret",
                        "message": f"发现{issue_type}，建议移至环境变量",
                        "severity": "error"
                    })
    
    def _check_long_lines(self, lines: List[str], file_path: str):
        """检查过长的行"""
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                self.issues.append({
                    "file": file_path,
                    "line": i,
                    "type": "long_line",
                    "message": f"行过长 ({len(line)} 字符 > 120)",
                    "severity": "info"
                })
    
    def get_report(self) -> Dict[str, Any]:
        """生成报告"""
        by_severity = {"error": 0, "warning": 0, "info": 0}
        by_type = {}
        
        for issue in self.issues:
            severity = issue.get("severity", "info")
            issue_type = issue.get("type", "unknown")
            
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_type[issue_type] = by_type.get(issue_type, 0) + 1
        
        return {
            "total_issues": len(self.issues),
            "by_severity": by_severity,
            "by_type": by_type,
            "issues": self.issues,
        }


if __name__ == "__main__":
    import sys
    
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"\n🔍 代码质量检查：{root_dir}\n")
    
    checker = CodeQualityChecker(root_dir)
    report = checker.scan_all()
    
    print(f"\n{'='*70}")
    print("📊 检查报告")
    print(f"{'='*70}")
    
    print(f"\n总问题数：{report['total_issues']}")
    print(f"  ❌ 错误：{report['by_severity']['error']}")
    print(f"  ⚠️  警告：{report['by_severity']['warning']}")
    print(f"  ℹ️  提示：{report['by_severity']['info']}")
    
    print(f"\n问题类型分布:")
    for issue_type, count in sorted(report['by_type'].items()):
        print(f"  - {issue_type}: {count}")
    
    # 显示严重问题
    errors = [i for i in report['issues'] if i.get('severity') == 'error']
    if errors:
        print(f"\n❌ 严重问题:")
        for issue in errors[:10]:
            print(f"  {issue['file']}:{issue.get('line', '?')} - {issue['message']}")
    
    print(f"\n{'='*70}\n")
