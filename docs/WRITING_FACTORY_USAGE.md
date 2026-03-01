# 写作工厂使用指南

> 创建时间：2026-03-01  
> 版本：v3.0.0  
> 完成度：95%

---

## 📚 目录

1. [快速开始](#快速开始)
2. [写作技巧库](#写作技巧库)
3. [优化改进器](#优化改进器)
4. [质量评估](#质量评估)
5. [完整示例](#完整示例)

---

## 🚀 快速开始

### 1. 导入模块

```python
from core.writing_factory import (
    Outliner,           # 大纲生成
    DraftWriter,        # 初稿撰写
    WritingOptimizer,   # 优化改进
    QualityChecker,     # 质量评估
    TechniqueFactory    # 写作技巧
)
```

### 2. 完整写作流程

```python
# 1. 生成大纲
outliner = Outliner(model='v3')
outline = outliner.generate(
    title='AI 教育的未来',
    description='AI 技术在教育领域的应用与影响',
    style='新闻报道',
    structure='总分总'
)

# 2. 撰写初稿
writer = DraftWriter(model='v3')
draft = writer.write(outline, style='新闻报道')

# 3. 质量评估
checker = QualityChecker()
quality_report = checker.check(draft['content'])
print(f"质量评分：{quality_report['total_score']}")

# 4. 优化改进
optimizer = WritingOptimizer(model='v3')
optimized = optimizer.optimize(draft['content'], optimization_type='all')

# 5. 最终评估
final_report = checker.check(optimized['optimized'])
print(f"优化后评分：{final_report['total_score']}")
```

---

## ✍️ 写作技巧库

### 10 种写作技巧

| 技巧 | 说明 | 适用场景 |
|------|------|---------|
| SCQA 架构 | 情境/冲突/问题/答案 | 文章/提案/报告 |
| 金字塔原理 | 结论先行，分层论据 | 摘要/演示/ memo |
| 故事化叙述 | 人物/冲突/转折/结局 | 品牌故事/案例 |
| 数据驱动 | 用数据支撑观点 | 数据文章/报告 |
| 对比手法 | 突出差异 | 竞品对比/前后对比 |
| 引用权威 | 借权威增强说服力 | 专家引用/研究引用 |
| 金句打造 | 创造易传播的句子 | Slogan/标题 |
| 情绪调动 | 激发情感共鸣 | 共情内容/激励 |
| 悬念设置 | 制造好奇心 | 神秘开头/预告 |
| 行动号召 | 促使立即行动 | CTA/营销文案 |

### 使用示例

```python
from core.writing_factory.technique_prompts import render_prompt

# 使用 SCQA 架构生成文章 Prompt
prompt = render_prompt(
    technique='scqa',
    template='article',
    topic='AI 教育的未来',
    situation_points=['AI 技术快速发展', '教育行业面临变革'],
    complication_points=['传统教育模式落后', '学生需求多样化'],
    question_points=['如何利用 AI 改进教育？'],
    answer_points=['个性化学习', '智能辅导', '教育公平']
)

print(prompt)
```

### 40 个模板列表

```python
from core.writing_factory.technique_prompts import list_all_prompts

all_prompts = list_all_prompts()
for technique, templates in all_prompts.items():
    print(f"\n{technique}:")
    for template_id in templates:
        print(f"  - {template_id}")
```

---

## 🔧 优化改进器

### 6 大优化功能

| 功能 | 说明 | 使用场景 |
|------|------|---------|
| AI 痕迹清除 | 移除套话 | 所有 AI 生成内容 |
| 金句增强 | 添加传播点 | 需要传播的文章 |
| 数据补充 | 增加说服力 | 观点类文章 |
| 案例丰富 | 提升可读性 | 理论类文章 |
| 开头优化 | 增强吸引力 | 所有文章 |
| 结尾升华 | 提升价值 | 所有文章 |

### 使用示例

```python
from core.writing_factory.optimizer import WritingOptimizer

optimizer = WritingOptimizer(model='v3')

# 1. AI 痕迹清除
result = optimizer.optimize(content, optimization_type='ai_clean')
print("移除套话:", result['removed_cliches'])

# 2. 金句增强
result = optimizer.optimize(content, optimization_type='golden_sentence')
print("新增金句:", result['golden_sentences'])

# 3. 全面优化
result = optimizer.optimize(content, optimization_type='all')
print("优化后:", result['optimized'])
```

### 批量优化

```python
from core.writing_factory.optimizer import optimize_batch

contents = ['文章 1', '文章 2', '文章 3']
results = optimize_batch(contents, optimization_type='all')

for i, result in enumerate(results):
    print(f"文章{i+1}优化完成")
```

---

## 📊 质量评估

### 5 维评估体系

| 维度 | 权重 | 说明 |
|------|------|------|
| 内容质量 | 35% | 长度、段落、信息密度 |
| 结构逻辑 | 25% | 段落组织、逻辑连接 |
| 表达文采 | 20% | 句式变化、词汇丰富 |
| 传播价值 | 15% | 标题吸引力、时效性 |
| 创新独特 | 5% | 独特观点、案例支撑 |

### 使用示例

```python
from core.writing_factory.quality_checker import QualityChecker

checker = QualityChecker()

# 单篇评估
report = checker.check(article_content)
print(f"总分：{report['total_score']}")
print(f"等级：{report['grade']}")
print(f"各维度得分：{report['dimension_scores']}")

# 批量评估
reports = checker.check_batch([article1, article2, article3])
for report in reports:
    print(f"评分：{report['total_score']} - {report['grade']}")
```

### 评分等级

| 等级 | 分数 | 说明 |
|------|------|------|
| S | 90-100 | 爆款潜质 |
| A | 80-89 | 优质文章 |
| B | 70-79 | 合格作品 |
| C | 60-69 | 需要改进 |
| D | 0-59 | 质量较差 |

---

## 📝 完整示例

### 从零到一写文章

```python
from core.writing_factory import *

# 1. 确定选题
topic = {
    'title': 'AI 编程课与教育公平',
    'description': '探讨 AI 编程课程如何促进教育公平',
    'industry': '教育',
    'angle': '深度分析'
}

# 2. 生成大纲
outliner = Outliner(model='v3')
outline = outliner.generate(
    title=topic['title'],
    description=topic['description'],
    style='商业分析',
    structure='问题 - 分析 - 解决'
)

# 3. 撰写初稿
writer = DraftWriter(model='v3')
draft = writer.write(outline, style='商业分析')

# 4. 质量评估
checker = QualityChecker()
initial_score = checker.check(draft['content'])
print(f"初稿评分：{initial_score['total_score']}")

# 5. 优化改进
optimizer = WritingOptimizer(model='v3')
optimized = optimizer.optimize(draft['content'], optimization_type='all')

# 6. 最终评估
final_score = checker.check(optimized['optimized'])
print(f"终稿评分：{final_score['total_score']}")
print(f"提升：{final_score['total_score'] - initial_score['total_score']}分")
```

---

## 🎯 最佳实践

### 1. 选择合适的写作技巧

- **商业分析** → 金字塔原理 + 数据驱动
- **品牌故事** → 故事化叙述 + 情绪调动
- **产品发布** → SCQA 架构 + 行动号召
- **观点评论** → 对比手法 + 引用权威

### 2. 优化顺序建议

```
初稿 → AI 痕迹清除 → 质量评估 → 金句增强 → 数据补充 → 最终评估
```

### 3. 质量提升技巧

- 初稿完成后至少优化 2 轮
- 重点关注开头和结尾
- 每 500 字至少 1 个金句
- 每个观点至少 1 个数据支撑

---

## 📚 API 使用

### RESTful API

```bash
# 生成大纲
curl -X POST http://43.134.234.4:8000/api/v3/writing/outline \
  -H "Content-Type: application/json" \
  -d '{"title":"AI 教育","style":"新闻报道"}'

# 撰写初稿
curl -X POST http://43.134.234.4:8000/api/v3/writing/draft \
  -H "Content-Type: application/json" \
  -d '{"outline":{...}}'

# 优化文章
curl -X POST http://43.134.234.4:8000/api/v3/writing/optimize \
  -H "Content-Type: application/json" \
  -d '{"content":"...","type":"all"}'

# 质量评估
curl -X POST http://43.134.234.4:8000/api/v3/writing/quality/check \
  -H "Content-Type: application/json" \
  -d '{"content":"..."}'
```

---

## 🔗 相关文档

- [WRITING_API.md](WRITING_API.md) - API 详细文档
- [V3_MODULE_DESIGN.md](V3_MODULE_DESIGN.md) - V3 架构设计
- [MISSING_FEATURES.md](MISSING_FEATURES.md) - 缺失功能清单

---

*写作工厂已完成 95%，可立即投入使用* ✅
