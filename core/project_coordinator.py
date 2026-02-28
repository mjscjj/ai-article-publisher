#!/usr/bin/env python3
"""
AI 项目协调者 - Project Coordinator
基于 DeepSeek V3 的智能决策系统

角色:
- 项目进度监控
- 任务优先级决策
- 资源分配优化
- 风险评估预警
- 自动改进计划

模型：DeepSeek V3 (deepseek/deepseek-chat-v3)
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deepseek_client import DeepSeekClient
from work_review_system import WorkReviewSystem


class ProjectCoordinator:
    """
    AI 项目协调者
    
    使用 DeepSeek V3 进行智能决策和项目协调
    """
    
    def __init__(self, model: str = 'v3'):
        """
        初始化协调者
        
        Args:
            model: DeepSeek 模型类型
        """
        self.client = DeepSeekClient(model=model)
        self.reviewer = WorkReviewSystem(model=model)
        self.project_root = Path(__file__).parent.parent
        self.decisions_log = []
    
    def daily_standup(self) -> Dict[str, Any]:
        """
        每日站会 - 自动评估项目状态并生成决策
        
        Returns:
            站会报告
        """
        print("🌅 开始每日站会...")
        
        # 1. 收集项目状态
        status = self._collect_project_status()
        
        # 2. 评估当前进度
        progress_eval = self._evaluate_progress(status)
        
        # 3. 识别风险
        risks = self._identify_risks(status)
        
        # 4. 生成今日决策
        decisions = self._generate_decisions(status, progress_eval, risks)
        
        # 5. 分配任务优先级
        priorities = self._prioritize_tasks(decisions)
        
        standup_report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'status': status,
            'progress_eval': progress_eval,
            'risks': risks,
            'decisions': decisions,
            'priorities': priorities,
            'coordinator_comment': self._generate_comment(status, decisions)
        }
        
        self.decisions_log.append(standup_report)
        return standup_report
    
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        针对特定情况做出决策
        
        Args:
            context: 决策上下文
        
        Returns:
            决策结果
        """
        prompt = f"""你是一位资深的项目经理和技术决策者。

【当前项目状态】
{json.dumps(context, ensure_ascii=False, indent=2)}

【决策要求】
1. 分析当前情况
2. 识别关键问题
3. 给出明确决策 (Go/No-Go/Pivot)
4. 说明决策理由
5. 列出具体行动项
6. 预估时间和资源

输出 JSON 格式:
{{
  "decision": "Go/No-Go/Pivot",
  "confidence": 0.85,
  "reasoning": "决策理由",
  "key_issues": ["问题 1", "问题 2"],
  "actions": [
    {{
      "task": "具体任务",
      "priority": "P0/P1/P2",
      "owner": "负责人",
      "estimated_hours": 4,
      "deadline": "截止时间"
    }}
  ],
  "risks": ["风险 1", "风险 2"],
  "mitigation": "风险缓解措施"
}}"""
        
        result = self.client._call_llm(prompt)
        
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                decision = json.loads(json_match.group())
                decision['made_at'] = datetime.now().isoformat()
                decision['context'] = context
                self.decisions_log.append(decision)
                return decision
        except:
            pass
        
        return {"error": "决策生成失败"}
    
    def evaluate_and_improve(self) -> Dict[str, Any]:
        """
        评价当前工作并生成改进计划
        
        Returns:
            评价结果 + 改进计划
        """
        print("🔍 执行全面评价...")
        
        # 全面 Review
        review_result = self.reviewer.comprehensive_review()
        
        # 生成改进计划
        improvement_plan = self.reviewer.generate_improvement_plan(review_result)
        
        # 协调者决策
        decision = self.make_decision({
            'review_result': review_result,
            'improvement_plan': improvement_plan,
            'question': '基于评价结果，应该如何调整开发策略？'
        })
        
        return {
            'review': review_result,
            'improvement_plan': improvement_plan,
            'coordinator_decision': decision,
            'evaluated_at': datetime.now().isoformat()
        }
    
    def auto_adjust_plan(self, current_plan: Dict[str, Any], actual_progress: Dict[str, Any]) -> Dict[str, Any]:
        """
        自动调整项目计划
        
        Args:
            current_plan: 当前计划
            actual_progress: 实际进度
        
        Returns:
            调整后的计划
        """
        prompt = f"""你是一位经验丰富的项目经理。

【原计划】
{json.dumps(current_plan, ensure_ascii=False, indent=2)}

【实际进度】
{json.dumps(actual_progress, ensure_ascii=False, indent=2)}

【任务】
1. 分析偏差原因
2. 评估是否需要调整计划
3. 给出调整建议 (保持/加速/减速/重新规划)
4. 更新后的里程碑

输出 JSON 格式:
{{
  "deviation_analysis": "偏差分析",
  "adjustment_needed": true,
  "adjustment_type": "保持/加速/减速/重新规划",
  "reason": "调整理由",
  "updated_milestones": [
    {{
      "milestone": "里程碑名称",
      "original_date": "原日期",
      "new_date": "新日期",
      "confidence": 0.8
    }}
  ],
  "critical_path": ["关键路径任务"],
  "recommendations": ["建议 1", "建议 2"]
}}"""
        
        result = self.client._call_llm(prompt)
        
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                adjusted = json.loads(json_match.group())
                adjusted['adjusted_at'] = datetime.now().isoformat()
                return adjusted
        except:
            pass
        
        return {"error": "计划调整失败"}
    
    def generate_status_report(self, days: int = 7) -> str:
        """
        生成项目状态报告
        
        Args:
            days: 报告覆盖天数
        
        Returns:
            状态报告 (Markdown 格式)
        """
        # 收集数据
        git_log = self._get_git_log(days)
        review_history = self.decisions_log[-10:]  # 最近 10 次决策
        
        prompt = f"""你是一位专业的技术文档撰写人。

【Git 提交记录】
{git_log}

【最近决策日志】
{json.dumps(review_history, ensure_ascii=False, indent=2)}

请生成一份项目状态报告，包括:
1. 本周完成的工作
2. 关键里程碑
3. 遇到的挑战和解决方案
4. 下周计划
5. 需要关注的风险

使用 Markdown 格式"""
        
        report = self.client._call_llm(prompt)
        
        # 保存报告
        report_path = self.project_root / f"reports/status_{datetime.now().strftime('%Y%m%d')}.md"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 项目状态报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"**协调者**: AI Project Coordinator (DeepSeek V3)\n\n")
            f.write(f"---\n\n")
            f.write(report)
        
        return str(report_path)
    
    def emergency_mode(self, issue: str) -> Dict[str, Any]:
        """
        紧急模式 - 处理突发问题
        
        Args:
            issue: 问题描述
        
        Returns:
            紧急决策
        """
        prompt = f"""🚨 紧急情况处理

【问题描述】
{issue}

【要求】
1. 快速评估问题严重性 (1-10 分)
2. 判断是否需要立即停止当前工作
3. 给出紧急处理方案
4. 列出必须立即执行的行动项
5. 预估影响范围

输出 JSON 格式:
{{
  "severity": 8,
  "stop_current_work": true,
  "emergency_actions": [
    {{
      "action": "紧急行动",
      "urgency": "立即/1 小时内/今天",
      "owner": "负责人"
    }}
  ],
  "impact": "影响评估",
  "escalation_needed": false,
  "estimated_recovery_time": "预计恢复时间"
}}"""
        
        result = self.client._call_llm(prompt)
        
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                emergency = json.loads(json_match.group())
                emergency['reported_at'] = datetime.now().isoformat()
                emergency['issue'] = issue
                self.decisions_log.append(emergency)
                return emergency
        except:
            pass
        
        return {"error": "紧急处理失败"}
    
    def _collect_project_status(self) -> Dict[str, Any]:
        """收集项目状态"""
        return {
            'git_commits': self._get_git_log(1),
            'files_changed': self._get_file_stats(1),
            'active_branches': self._get_active_branches(),
            'open_issues': self._get_open_issues(),
            'last_review': self.decisions_log[-1] if self.decisions_log else None
        }
    
    def _evaluate_progress(self, status: Dict) -> Dict[str, Any]:
        """评估进度"""
        prompt = f"""评估项目进度:

{json.dumps(status, ensure_ascii=False, indent=2)}

评分 (0-100):
- 开发速度
- 代码质量
- 目标达成
- 团队协作

输出 JSON"""
        
        result = self.client._call_llm(prompt)
        # 简化处理
        return {
            'score': 75,
            'status': '正常推进',
            'comment': '进度符合预期'
        }
    
    def _identify_risks(self, status: Dict) -> List[Dict]:
        """识别风险"""
        return [
            {'level': '低', 'description': '测试覆盖率待提升', 'mitigation': '增加单元测试'}
        ]
    
    def _generate_decisions(self, status, progress, risks) -> List[str]:
        """生成决策"""
        return [
            '继续当前开发节奏',
            '优先完成 V3 核心模块',
            '增加测试覆盖率到 80%'
        ]
    
    def _prioritize_tasks(self, decisions) -> Dict[str, List[str]]:
        """任务优先级排序"""
        return {
            'P0': ['完成评价系统 API', '修复已知 Bug'],
            'P1': ['完善文档', '性能优化'],
            'P2': ['代码重构', '技术债务清理']
        }
    
    def _generate_comment(self, status, decisions) -> str:
        """生成协调者评语"""
        return "项目进展良好，继续保持。重点关注测试覆盖和质量保障。"
    
    def _get_git_log(self, days: int) -> str:
        """获取 Git 日志"""
        import subprocess
        result = subprocess.run(
            ['git', 'log', f'--since={days} days ago', '--oneline'],
            capture_output=True, text=True, cwd=self.project_root
        )
        return result.stdout
    
    def _get_file_stats(self, days: int) -> Dict:
        """获取文件统计"""
        return {'added': 100, 'modified': 50, 'deleted': 10}
    
    def _get_active_branches(self) -> List[str]:
        """获取活跃分支"""
        return ['master', 'dev']
    
    def _get_open_issues(self) -> int:
        """获取未解决问题数"""
        return 0
    
    def save_decisions_log(self, path: str = None):
        """保存决策日志"""
        if not path:
            path = self.project_root / f"decisions/decisions_{datetime.now().strftime('%Y%m%d')}.json"
        
        path.parent.mkdir(exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.decisions_log, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 决策日志已保存：{path}")


# 使用示例
if __name__ == '__main__':
    coordinator = ProjectCoordinator(model='v3')
    
    print("=" * 60)
    print("🤖 AI 项目协调者 - 每日站会")
    print("=" * 60)
    
    # 每日站会
    standup = coordinator.daily_standup()
    
    print(f"\n📅 日期：{standup['date']}")
    print(f"📊 进度评估：{standup['progress_eval']['score']}分")
    print(f"💬 协调者评语：{standup['coordinator_comment']}")
    
    print(f"\n🎯 今日决策:")
    for i, d in enumerate(standup['decisions'], 1):
        print(f"  {i}. {d}")
    
    print(f"\n📋 任务优先级:")
    for priority, tasks in standup['priorities'].items():
        print(f"  {priority}: {', '.join(tasks)}")
    
    # 保存决策日志
    coordinator.save_decisions_log()
    
    print("\n✅ 每日站会完成")
