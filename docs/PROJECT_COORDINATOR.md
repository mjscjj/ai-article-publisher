# AI 项目协调者 - 使用说明

> 创建时间：2026-03-02  
> 模型：DeepSeek V3  
> 角色：项目决策者 + 进度协调者

---

## 🤖 角色定位

**AI Project Coordinator** 是项目的智能决策者和协调者，负责：

1. **每日站会** - 自动评估项目状态
2. **智能决策** - 基于数据做出 Go/No-Go 决策
3. **进度跟踪** - 监控开发进度和质量
4. **风险预警** - 识别潜在风险并提前预警
5. **资源分配** - 优化任务优先级
6. **紧急处理** - 突发问题快速响应

---

## 🚀 快速开始

### 每日站会 (推荐每天执行)

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher
python3 core/project_coordinator.py
```

**输出**:
- 项目状态评估
- 今日决策
- 任务优先级 (P0/P1/P2)
- 风险识别

### API 调用

```bash
# 启动 API 服务
uvicorn api/v3/coordinator_api.py:app --host 0.0.0.0 --port 8003

# 每日站会
curl -X POST http://43.134.234.4:8003/api/v3/coordinator/daily-standup

# 做出决策
curl -X POST http://43.134.234.4:8003/api/v3/coordinator/decide \
  -H "Content-Type: application/json" \
  -d '{"context": {"issue": "是否继续开发写作工厂模块？"}}'

# 评价并改进
curl -X POST http://43.134.234.4:8003/api/v3/coordinator/evaluate

# 紧急模式
curl -X POST http://43.134.234.4:8003/api/v3/coordinator/emergency \
  -H "Content-Type: application/json" \
  -d '{"issue": "严重 Bug 导致系统崩溃"}'
```

---

## 📋 核心功能

### 1. 每日站会

**时间**: 每天早上自动执行

**内容**:
- 收集项目状态 (Git/文件/进度)
- 评估当前进度
- 识别风险
- 生成今日决策
- 分配任务优先级

**输出示例**:
```json
{
  "date": "2026-03-02",
  "progress_eval": {
    "score": 85,
    "status": "正常推进"
  },
  "decisions": [
    "继续当前开发节奏",
    "优先完成评价系统",
    "增加测试覆盖到 80%"
  ],
  "priorities": {
    "P0": ["完成评价 API", "修复 Bug"],
    "P1": ["完善文档"],
    "P2": ["代码重构"]
  }
}
```

### 2. 智能决策

**场景**:
- 是否继续某个功能开发？
- 是否需要调整优先级？
- 是否接受技术债务？
- 是否需要额外资源？

**决策类型**:
- **Go**: 继续执行
- **No-Go**: 停止/放弃
- **Pivot**: 调整方向

### 3. 评价改进

**流程**:
1. 执行全面 Review (代码/文档/进度/测试)
2. DeepSeek V3 评分
3. 生成改进计划
4. 协调者决策

**输出**:
- 5 维评分雷达图
- S/A/B/C/D 等级
- 改进计划 (P0/P1/P2)
- 下次 Review 时间

### 4. 紧急模式

**触发条件**:
- 严重 Bug
- 系统崩溃
- 数据丢失
- 安全漏洞

**响应时间**: < 1 分钟

**输出**:
- 严重性评分 (1-10)
- 紧急行动项
- 影响评估
- 恢复时间预估

---

## 🔧 配置

### 模型配置

```python
# 使用 DeepSeek V3 (推荐)
coordinator = ProjectCoordinator(model='v3')

# 使用免费模型
coordinator = ProjectCoordinator(model='free')
```

### 定时任务

```bash
# 每天 8 点执行站会
0 8 * * * cd /root/.openclaw/workspace-writer/ai-article-publisher && python3 core/project_coordinator.py

# 每周日生成状态报告
0 9 * * 0 cd /root/.openclaw/workspace-writer/ai-article-publisher && python3 -c "from core.project_coordinator import ProjectCoordinator; c = ProjectCoordinator(); c.generate_status_report(7)"
```

---

## 📊 决策日志

**位置**: `decisions/decisions_YYYYMMDD.json`

**内容**:
- 每日站会报告
- 重大决策记录
- 紧急事件处理
- 评价改进历史

**查看**:
```bash
cat decisions/decisions_20260302.json
```

---

## 🎯 最佳实践

### 1. 每日站会坚持执行
- 每天早上第一件事情
- 根据决策安排当日工作
- 晚上复盘完成情况

### 2. 重大决策前咨询
- 功能开发前询问是否值得
- 遇到技术难题请求决策
- 资源不足时申请支持

### 3. 定期评价改进
- 每周至少 1 次全面 Review
- 根据改进计划调整
- 跟踪改进效果

### 4. 紧急情况立即报告
- 不要自行处理严重问题
- 立即触发紧急模式
- 按协调者指示执行

---

## 📈 成功指标

| 指标 | 目标值 |
|------|--------|
| 决策准确率 | > 85% |
| 风险识别率 | > 90% |
| 项目延期率 | < 10% |
| 团队满意度 | > 90% |

---

## 🤝 与人类协作

**协调者职责**:
- 数据分析
- 风险评估
- 优先级建议
- 进度跟踪

**人类职责**:
- 最终决策拍板
- 创造性工作
- 团队沟通
- 资源协调

**协作模式**:
```
协调者分析 → 给出建议 → 人类拍板 → 协调者跟踪执行
```

---

*AI 协调者不是替代人类，而是增强决策质量*
