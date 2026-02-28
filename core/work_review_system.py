#!/usr/bin/env python3
"""
DeepSeek V3 全面 Review 系统
对所有工作产出进行智能评价和持续改进

评价范围:
- 代码质量 (Code Review)
- 文档质量 (Documentation Review)
- 测试覆盖 (Test Coverage Review)
- 项目进度 (Progress Review)
- 架构设计 (Architecture Review)

模型: DeepSeek V3 (deepseek/deepseek-chat-v3)
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deepseek_client import DeepSeekClient


class WorkReviewSystem:
    """
    工作评价系统
    
    使用 DeepSeek V3 对所有工作产出进行全面评价
    """
    
    def __init__(self, model: str = 'v3'):
        """
        初始化评价系统
        
        Args:
            model: DeepSeek 模型类型
        """
        self.client = DeepSeekClient(model=model)
        self.project_root = Path(__file__).parent.parent
        self.review_results = []
    
    def review_code(self, file_paths: List[str] = None) -> Dict[str, Any]:
        """
        代码质量评价
        
        Args:
            file_paths: 要评价的文件路径列表
        
        Returns:
            评价结果
        """
        if not file_paths:
            # 自动获取最近修改的 Python 文件
            file_paths = self._get_recent_python_files()
        
        code_contents = []
        for fp in file_paths:
            try:
                with open(self.project_root / fp, 'r', encoding='utf-8') as f:
                    code_contents.append(f"文件：{fp}\n{f.read()}")
            except Exception as e:
                print(f"⚠️  读取失败 {fp}: {e}")
        
        if not code_contents:
            return {"error": "没有可评价的代码文件"}
        
        prompt = self._build_code_review_prompt(code_contents)
        result = self.client.evaluate_article("代码 Review", "\n\n".join(code_contents), evaluation_type='code_review')
        
        result['review_type'] = 'code'
        result['files_reviewed'] = file_paths
        result['reviewed_at'] = datetime.now().isoformat()
        
        self.review_results.append(result)
        return result
    
    def review_documentation(self, doc_paths: List[str] = None) -> Dict[str, Any]:
        """
        文档质量评价
        
        Args:
            doc_paths: 要评价的文档路径列表
        
        Returns:
            评价结果
        """
        if not doc_paths:
            # 自动获取 Markdown 文档
            doc_paths = self._get_markdown_documents()
        
        doc_contents = []
        for dp in doc_paths:
            try:
                with open(self.project_root / dp, 'r', encoding='utf-8') as f:
                    doc_contents.append(f"文档：{dp}\n{f.read()[:3000]}")  # 限制长度
            except Exception as e:
                print(f"⚠️  读取失败 {dp}: {e}")
        
        if not doc_contents:
            return {"error": "没有可评价的文档"}
        
        prompt = self._build_doc_review_prompt(doc_contents)
        result = self.client.evaluate_article("文档 Review", "\n\n".join(doc_contents), evaluation_type='doc_review')
        
        result['review_type'] = 'documentation'
        result['docs_reviewed'] = doc_paths
        result['reviewed_at'] = datetime.now().isoformat()
        
        self.review_results.append(result)
        return result
    
    def review_progress(self, days: int = 7) -> Dict[str, Any]:
        """
        项目进度评价
        
        Args:
            days: 评价最近 N 天的进度
        
        Returns:
            评价结果
        """
        # 获取 Git 提交历史
        git_log = self._get_git_log(days)
        
        # 获取文件变更统计
        file_stats = self._get_file_stats(days)
        
        prompt = self._build_progress_review_prompt(git_log, file_stats, days)
        result = self.client.evaluate_article(
            f"{days}天项目进度 Review",
            f"Git 提交:\n{git_log}\n\n文件变更:\n{json.dumps(file_stats, ensure_ascii=False, indent=2)}",
            evaluation_type='progress_review'
        )
        
        result['review_type'] = 'progress'
        result['period_days'] = days
        result['reviewed_at'] = datetime.now().isoformat()
        
        self.review_results.append(result)
        return result
    
    def review_tests(self, test_paths: List[str] = None) -> Dict[str, Any]:
        """
        测试覆盖评价
        
        Args:
            test_paths: 测试文件路径列表
        
        Returns:
            评价结果
        """
        if not test_paths:
            test_paths = self._get_test_files()
        
        test_contents = []
        for tp in test_paths:
            try:
                with open(self.project_root / tp, 'r', encoding='utf-8') as f:
                    test_contents.append(f"测试：{tp}\n{f.read()}")
            except Exception as e:
                print(f"⚠️  读取失败 {tp}: {e}")
        
        if not test_contents:
            return {"error": "没有可评价的测试文件"}
        
        # 运行测试获取覆盖率
        coverage_result = self._run_tests_with_coverage()
        
        test_files_str = '\n\n'.join(test_contents[:3])
        coverage_str = json.dumps(coverage_result, ensure_ascii=False, indent=2)
        result = self.client.evaluate_article(
            "测试覆盖 Review",
            f"测试文件:\n{test_files_str}\n\n覆盖率报告:\n{coverage_str}",
            evaluation_type='test_review'
        )
        
        result['review_type'] = 'tests'
        result['tests_reviewed'] = test_paths
        result['coverage'] = coverage_result
        result['reviewed_at'] = datetime.now().isoformat()
        
        self.review_results.append(result)
        return result
    
    def comprehensive_review(self) -> Dict[str, Any]:
        """
        全面综合评价
        
        Returns:
            综合评价结果
        """
        print("🔍 开始全面 Review...")
        
        # 1. 代码评价
        print("  📝 评价代码质量...")
        code_review = self.review_code()
        
        # 2. 文档评价
        print("  📄 评价文档质量...")
        doc_review = self.review_documentation()
        
        # 3. 进度评价
        print("  📊 评价项目进度...")
        progress_review = self.review_progress(days=7)
        
        # 4. 测试评价
        print("  🧪 评价测试覆盖...")
        test_review = self.review_tests()
        
        # 5. 综合评分
        total_score = (
            code_review.get('total_score', 0) * 0.35 +
            doc_review.get('total_score', 0) * 0.20 +
            progress_review.get('total_score', 0) * 0.25 +
            test_review.get('total_score', 0) * 0.20
        )
        
        comprehensive_result = {
            'review_type': 'comprehensive',
            'total_score': round(total_score, 1),
            'grade': self._calculate_grade(total_score),
            'sub_reviews': {
                'code': code_review,
                'documentation': doc_review,
                'progress': progress_review,
                'tests': test_review
            },
            'overall_strengths': self._merge_strengths([
                code_review.get('strengths', []),
                doc_review.get('strengths', []),
                progress_review.get('strengths', []),
                test_review.get('strengths', [])
            ]),
            'overall_improvements': self._merge_improvements([
                code_review.get('improvements', []),
                doc_review.get('improvements', []),
                progress_review.get('improvements', []),
                test_review.get('improvements', [])
            ]),
            'recommendation': self._generate_recommendation(total_score),
            'reviewed_at': datetime.now().isoformat()
        }
        
        self.review_results.append(comprehensive_result)
        return comprehensive_result
    
    def generate_improvement_plan(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成改进计划
        
        Args:
            review_result: Review 结果
        
        Returns:
            改进计划
        """
        prompt = f"""基于以下 Review 结果，生成具体的改进计划:

【总体评分】{review_result.get('total_score', 0)} 分 ({review_result.get('grade', 'E')}级)

【优点】
{json.dumps(review_result.get('overall_strengths', []), ensure_ascii=False, indent=2)}

【改进建议】
{json.dumps(review_result.get('overall_improvements', []), ensure_ascii=False, indent=2)}

请生成详细的改进计划，包括:
1. 优先级排序 (P0/P1/P2)
2. 具体行动项
3. 预计耗时
4. 验收标准

输出 JSON 格式:
{{
  "improvement_plan": [
    {{
      "priority": "P0",
      "action": "具体行动",
      "estimated_hours": 2,
      "acceptance_criteria": "验收标准"
    }}
  ],
  "next_review_date": "下次 Review 时间"
}}"""
        
        result = self.client._call_llm(prompt)
        
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                plan = json.loads(json_match.group())
                plan['generated_at'] = datetime.now().isoformat()
                return plan
        except:
            pass
        
        return {"error": "生成改进计划失败"}
    
    def save_review_report(self, output_path: str = None):
        """保存 Review 报告"""
        if not output_path:
            output_path = self.project_root / f"reviews/review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.review_results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Review 报告已保存：{output_path}")
        return output_path
    
    def _get_recent_python_files(self, limit: int = 10) -> List[str]:
        """获取最近修改的 Python 文件"""
        result = subprocess.run(
            ['git', 'log', '--name-only', '--since=7 days ago', '--', '*.py'],
            capture_output=True, text=True, cwd=self.project_root
        )
        
        files = set()
        for line in result.stdout.split('\n'):
            if line.endswith('.py') and 'core/' in line:
                files.add(line.strip())
        
        return list(files)[:limit]
    
    def _get_markdown_documents(self) -> List[str]:
        """获取 Markdown 文档"""
        docs = []
        for pattern in ['docs/*.md', 'README.md', 'PROGRESS.md']:
            docs.extend([str(p) for p in self.project_root.glob(pattern)])
        return docs
    
    def _get_test_files(self) -> List[str]:
        """获取测试文件"""
        return [str(p) for p in self.project_root.glob('tests/*.py')]
    
    def _get_git_log(self, days: int) -> str:
        """获取 Git 提交历史"""
        result = subprocess.run(
            ['git', 'log', f'--since={days} days ago', '--oneline'],
            capture_output=True, text=True, cwd=self.project_root
        )
        return result.stdout
    
    def _get_file_stats(self, days: int) -> Dict[str, int]:
        """获取文件变更统计"""
        result = subprocess.run(
            ['git', 'stat', f'--since={days} days ago'],
            capture_output=True, text=True, cwd=self.project_root
        )
        
        stats = {'added': 0, 'modified': 0, 'deleted': 0}
        for line in result.stdout.split('\n'):
            if 'insertion' in line.lower():
                stats['added'] = int(line.split()[0]) if line.split()[0].isdigit() else 0
            elif 'deletion' in line.lower():
                stats['deleted'] = int(line.split()[0]) if line.split()[0].isdigit() else 0
        
        return stats
    
    def _run_tests_with_coverage(self) -> Dict[str, Any]:
        """运行测试并获取覆盖率"""
        try:
            result = subprocess.run(
                ['python3', '-m', 'pytest', 'tests/', '--cov=core', '--cov-report=json'],
                capture_output=True, text=True, cwd=self.project_root, timeout=60
            )
            
            # 读取覆盖率报告
            cov_file = self.project_root / 'htmlcov/coverage.json'
            if cov_file.exists():
                with open(cov_file) as f:
                    return json.load(f)
            
            return {'percent_covered': 0, 'error': '未找到覆盖率报告'}
        except Exception as e:
            return {'percent_covered': 0, 'error': str(e)}
    
    def _build_code_review_prompt(self, code_contents: List[str]) -> str:
        """构建代码 Review Prompt"""
        return f"""你是一位资深的高级工程师，拥有 10 年代码 Review 经验。

请对以下代码进行专业 Review:

{code_contents[:3]}  # 限制数量

【Review 维度】
1. 代码质量 (30%): 可读性/可维护性/代码规范
2. 架构设计 (25%): 模块划分/解耦程度/扩展性
3. 错误处理 (20%): 异常处理/边界条件/容错能力
4. 性能优化 (15%): 时间复杂度/空间复杂度/优化空间
5. 测试覆盖 (10%): 单元测试/集成测试/覆盖率

【输出要求】
1. 5 个维度打分 (0-100)
2. 总体评分和等级 (S/A/B/C/D)
3. 3 个代码优点
4. 3 个改进建议
5. 具体代码示例 (如何改进)

输出 JSON 格式"""
    
    def _build_doc_review_prompt(self, doc_contents: List[str]) -> str:
        """构建文档 Review Prompt"""
        return f"""你是一位资深技术文档专家。

请对以下文档进行专业 Review:

{doc_contents[:3]}

【Review 维度】
1. 内容完整性 (30%): 信息全面/细节充分
2. 结构清晰度 (25%): 逻辑清晰/层次分明
3. 表达准确性 (20%): 用词准确/无歧义
4. 可读性 (15%): 易于理解/示例充分
5. 实用性 (10%): 可操作性/参考价值

输出 JSON 格式评分"""
    
    def _build_progress_review_prompt(self, git_log: str, file_stats: Dict, days: int) -> str:
        """构建进度 Review Prompt"""
        return f"""你是一位资深的项目经理。

请对过去{days}天的项目进度进行 Review:

【Git 提交】
{git_log}

【文件变更】
{json.dumps(file_stats, ensure_ascii=False, indent=2)}

【Review 维度】
1. 开发效率 (30%): 提交频率/产出量
2. 代码质量 (25%): 提交信息/代码审查
3. 进度控制 (20%): 计划完成度/里程碑
4. 团队协作 (15%): 代码审查/文档更新
5. 技术债务 (10%): 重构/优化/bug 修复

输出 JSON 格式评分"""
    
    def _calculate_grade(self, score: float) -> str:
        """计算等级"""
        if score >= 90: return 'S'
        if score >= 80: return 'A'
        if score >= 70: return 'B'
        if score >= 60: return 'C'
        return 'D'
    
    def _merge_strengths(self, strengths_list: List[List[str]]) -> List[str]:
        """合并优点"""
        all_strengths = []
        for strengths in strengths_list:
            all_strengths.extend(strengths[:2])  # 每个维度取前 2 个
        return list(dict.fromkeys(all_strengths))[:5]  # 去重，最多 5 个
    
    def _merge_improvements(self, improvements_list: List[List[str]]) -> List[str]:
        """合并改进建议"""
        all_improvements = []
        for improvements in improvements_list:
            all_improvements.extend(improvements[:2])
        return list(dict.fromkeys(all_improvements))[:5]
    
    def _generate_recommendation(self, score: float) -> str:
        """生成推荐"""
        if score >= 90: return "优秀 - 保持当前节奏，可适当加速"
        if score >= 80: return "良好 - 持续改进，重点关注薄弱环节"
        if score >= 70: return "合格 - 需要加强代码质量和测试覆盖"
        if score >= 60: return "需要改进 - 建议放慢速度，提升质量"
        return "需要重视 - 立即调整开发策略"


# 使用示例
if __name__ == '__main__':
    reviewer = WorkReviewSystem(model='v3')
    
    # 全面 Review
    print("=" * 60)
    print("🚀 DeepSeek V3 全面工作 Review")
    print("=" * 60)
    
    result = reviewer.comprehensive_review()
    
    print(f"\n📊 总体评分：{result['total_score']} 分 ({result['grade']}级)")
    print(f"💡 推荐：{result['recommendation']}")
    
    print(f"\n✅ 优点:")
    for s in result['overall_strengths']:
        print(f"  - {s}")
    
    print(f"\n🔧 改进建议:")
    for s in result['overall_improvements']:
        print(f"  - {s}")
    
    # 生成改进计划
    print(f"\n📋 生成改进计划...")
    plan = reviewer.generate_improvement_plan(result)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    
    # 保存报告
    reviewer.save_review_report()
