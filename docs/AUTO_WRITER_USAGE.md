# 自动化写作使用指南

## 🚀 概述

AI Article Publisher 提供完整的自动化写作流程：

```
选题 → 搜索数据 → 生成切入角 → 提炼观点 → 构建结构 → 写作 → 排版 → 保存
```

## 📋 快速开始

### 1. 基础用法

```python
from core.auto_writer import AutoWriter

# 创建写作引擎
writer = AutoWriter(use_llm=True)  # True=使用 Kimi，False=规则生成

# 一键写作
result = writer.write_full_article("人工智能对教育的冲击")

# 查看结果
print(f"话题：{result['topic']}")
print(f"切入角：{result['angle']['title']}")
print(f"核心观点：{result['viewpoint']['content']}")
print(f"字数：{result['stats']['word_count']}")
print(f"文件：{result['files']['markdown']}")
```

### 2. 提供自定义事实

```python
facts = [
    "教育部发布 AI+ 教育指导意见",
    "60% 高校已开设 AI 相关课程",
    "教师担心被 AI 取代"
]

result = writer.write_full_article(
    topic="人工智能对教育的冲击",
    facts=facts,
    style="commercial_deep"
)
```

### 3. 批量写作

```python
topics = [
    "AI 编程课进入中小学课堂",
    "大学 AI 专业爆冷还是爆热",
    "教育公平在 AI 时代的新挑战"
]

results = []
for topic in topics:
    result = writer.write_full_article(topic)
    results.append(result)
    
print(f"完成 {len(results)} 篇文章")
```

## 🔧 进阶用法

### 分步执行

```python
from core.auto_writer import AutoWriter

writer = AutoWriter()

# Step 1: 从 RAG 搜索数据
facts = writer.rag.search("AI 教育", top_k=5)

# Step 2: 生成切入角
angles = writer.angle_gen.generate_angles("AI 教育", facts)
best_angle = writer.angle_gen.recommend_best(angles)

# Step 3: 提炼观点
viewpoints = writer.viewpoint_ext.extract_viewpoints(
    "AI 教育", facts, best_angle['type']
)
best_viewpoint = writer.viewpoint_ext.recommend_best(viewpoints)

# Step 4: 推荐结构
rec = writer.narrative_opt.recommend_structure(best_angle['type'], "AI 教育")

# Step 5: 写作
if writer.use_llm:
    draft = writer._write_with_llm(
        "AI 教育", best_angle, best_viewpoint, ...
    )
else:
    draft = writer._write_with_rules(...)

# Step 6: 排版
html = writer.markdown_to_html_simple(draft)
```

### 自定义写作风格

```python
# 可用风格:
# - commercial_deep: 商业深度 (SCQA + 晚点风)
# - news_fast: 新闻快讯 (倒金字塔)
# - story_feature: 故事特写 (英雄之旅)
# - academic_edu: 学术教育 (SCQA + 幽默)
# - analysis_report: 分析报告 (SCQA + 数据)

result = writer.write_full_article(
    topic="AI 教育",
    style="academic_edu"  # 切换风格
)
```

### 与 RAG 集成

```python
# 写作前积累素材
writer.rag.add_material(
    category="golden_sentence",
    content="AI 不会取代你，但会用 AI 的人会",
    description="通用金句"
)

# 写作时使用 RAG 数据
result = writer.write_full_article("AI 教育")
# 自动从 RAG 搜索相关事实

# 写作后保存成果
writer.rag.add_article(
    title=result['angle']['title'],
    content=result['draft'],
    topic=result['topic']
)
```

## 📊 输出结果

### 返回结构

```python
{
    "topic": "人工智能对教育的冲击",
    "angle": {
        "type": "human",
        "type_name": "人物型",
        "title": "我采访了 90 个中层管理者...",
        "core_viewpoint": "...",
        "opening_hook": "...",
        "score": 88
    },
    "viewpoint": {
        "type": "judgment",
        "type_name": "判断型",
        "content": "...",
        "intensity": 9,
        "spreadability": 8
    },
    "outline": {
        "topic": "...",
        "viewpoint": "...",
        "structure": "英雄之旅",
        "sections": [
            {
                "order": 1,
                "name": "平凡世界",
                "guidance": "...",
                "word_count": 400
            },
            ...
        ]
    },
    "draft": "# 标题\n\n正文...",
    "html": "<section>...</section>",
    "stats": {
        "char_count": 2500,
        "word_count": 1250,
        "facts_used": 5,
        "structure": "英雄之旅"
    },
    "files": {
        "markdown": "output/article_20260228_123456.md",
        "html": "output/article_20260228_123456.html"
    }
}
```

### 文件输出

- **Markdown**: `output/article_YYYYMMDD_HHMMSS.md`
- **HTML**: `output/article_YYYYMMDD_HHMMSS.html`
- **RAG 存储**: `data/rag/documents.json`

## 🎯 最佳实践

### 1. 写作前准备

```python
# 积累领域素材
writer.rag.add_material("case_study", "某 AI 教育案例...")
writer.rag.add_material("data_point", "60% 高校开设 AI 课程")
writer.rag.add_material("golden_sentence", "金句...")

# 写作时自动使用这些素材
```

### 2. 质量检查

```python
result = writer.write_full_article(topic)

# 检查质量
if result['stats']['word_count'] < 1500:
    print("⚠️ 文章偏短，建议补充案例")

if result['stats']['facts_used'] < 3:
    print("⚠️ 事实不足，建议增加数据")
```

### 3. 人工审核

```python
# 生成后人工审核
print("核心观点:", result['viewpoint']['content'])
print("开篇钩子:", result['angle']['opening_hook'])
print("金句:", result['angle'].get('golden_sentence', ''))

# 满意后发布
# publish_to_wechat(result['html'])
```

## ⚙️ 配置选项

### 使用 LLM vs 规则

```python
# 使用 Kimi-2.5 (高质量，需要 API)
writer = AutoWriter(use_llm=True)

# 使用规则生成 (零成本，质量一般)
writer = AutoWriter(use_llm=False)
```

### 输出目录

```python
# 自定义输出目录
writer.output_dir = "/path/to/output"
```

## 🔍 故障排查

### RAG 无数据

```python
# 检查 RAG 统计
stats = writer.rag.stats()
print(stats)

# 如果为空，先添加素材
writer.rag.add_material(...)
```

### LLM 调用失败

```python
# 降级到规则生成
writer = AutoWriter(use_llm=False)
result = writer.write_full_article(topic)
```

### 文章质量不佳

```python
# 1. 提供更多事实
facts = [...]  # 5-10 条高质量事实
result = writer.write_full_article(topic, facts=facts)

# 2. 切换写作风格
result = writer.write_full_article(topic, style="story_feature")

# 3. 人工润色
draft = result['draft']
# 手动修改...
```

## 📝 完整示例

```python
from core.auto_writer import AutoWriter

# 1. 初始化
writer = AutoWriter(use_llm=True)

# 2. 准备素材
writer.rag.add_material(
    category="data_point",
    content="60% 高校已开设 AI 相关课程",
    description="AI 教育普及率"
)

writer.rag.add_material(
    category="case_study",
    content="某教师用 AI 批改作业，效率提升 3 倍",
    description="AI 提效案例"
)

# 3. 写作
result = writer.write_full_article(
    topic="人工智能对教育的冲击",
    style="commercial_deep"
)

# 4. 检查质量
print(f"字数：{result['stats']['word_count']}")
print(f"事实：{result['stats']['facts_used']}")
print(f"结构：{result['stats']['structure']}")

# 5. 保存成果
writer.rag.add_article(
    title=result['angle']['title'],
    content=result['draft'],
    topic=result['topic'],
    tags=["AI", "教育"]
)

# 6. 发布 (需要时)
# publish_to_wechat(result['html'])
```

---

*最后更新：2026-02-28*
