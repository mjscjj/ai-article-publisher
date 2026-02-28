# RAG 知识库使用指南

## 📚 概述

AI Article Publisher 集成了 RAG (检索增强生成) 知识库功能，用于:
- 积累写作素材 (金句/案例/数据)
- 存储历史文章
- 智能检索相关内容
- 辅助 AI 写作

## 🚀 快速开始

### 1. 导入 RAG 模块

```python
from core.rag_simple import get_rag

# 获取 RAG 实例
rag = get_rag()
```

### 2. 添加文章

```python
rag.add_article(
    title="AI 写作技巧：如何写出爆款文章",
    content="好的切入角是成功的一半...",
    topic="写作技巧",
    tags=["AI", "写作", "爆款"]
)
```

### 3. 添加素材

```python
# 金句素材
rag.add_material(
    category="golden_sentence",
    content="AI 不会取代你，但会用 AI 的人会",
    description="适合用于 AI 相关文章结尾"
)

# 案例素材
rag.add_material(
    category="case_study",
    content="某篇 AI 教育文章通过'60% 高校已开设 AI 课程'这个数据点，获得 10w+ 阅读",
    description="数据制造紧迫感"
)
```

### 4. 搜索

```python
# 全文搜索
results = rag.search("AI 写作", top_k=5)

# 按分类搜索
materials = rag.search("金句", category="material")
```

### 5. 问答

```python
result = rag.query("如何写出爆款文章？")
print(result["answer"])
print(result["sources"])
```

## 📊 数据统计

```python
stats = rag.stats()
print(f"总文档数：{stats['total_docs']}")
print(f"分类分布：{stats['by_category']}")
print(f"总字数：{stats['total_words']}")
```

## 🔧 高级用法

### 批量导入文章

```python
articles = [
    {"title": "文章 1", "content": "...", "topic": "技术"},
    {"title": "文章 2", "content": "...", "topic": "教育"},
]

for article in articles:
    rag.add_article(**article)
```

### 获取特定素材

```python
# 获取所有金句
golden_sentences = rag.get_materials("golden_sentence", limit=20)

# 获取所有案例
case_studies = rag.get_materials("case_study", limit=10)
```

### 与写作流程集成

```python
from core.rag_simple import get_rag
from core.angle_generator_lite import AngleGeneratorLite

# 初始化
rag = get_rag()
angle_gen = AngleGeneratorLite()

# 搜索相关素材
materials = rag.search("AI 教育", top_k=5)

# 基于素材生成切入角
facts = [m['snippet'] for m in materials]
angles = angle_gen.generate_angles("AI 教育", facts)
```

## 📁 数据存储

- **文档存储**: `data/rag/documents.json`
- **索引文件**: `data/rag/index.json`
- **缓存目录**: `data/rag_cache/`

## 🔍 搜索原理

使用改进的 BM25 算法:
- 中文按 2-4 字分词
- 标题匹配权重 ×3
- 支持分类过滤

## 💡 最佳实践

### 1. 及时积累素材

每次写作后，将好的金句、案例、数据保存到 RAG:

```python
# 写作完成后
rag.add_material("golden_sentence", best_sentence)
rag.add_material("case_study", case_used)
```

### 2. 写作前检索

开始写作前，先搜索相关素材:

```python
# 确定话题后
materials = rag.search(topic, top_k=10)
facts = [m['snippet'] for m in materials]
```

### 3. 分类管理

使用清晰的分类体系:
- `golden_sentence` - 金句
- `case_study` - 案例
- `data_point` - 数据
- `template` - 模板
- `quote` - 引用

### 4. 定期整理

定期检查和清理过时内容:

```python
# 查看统计
stats = rag.stats()

# 删除旧文档 (需要时)
# rag.documents.pop(index)
# rag._save_documents()
```

## 🔄 与 AnythingLLM 集成 (可选)

如果需要使用 AnythingLLM 的高级 RAG 功能:

```python
from core.rag_client import AnythingLLMClient

client = AnythingLLMClient(
    base_url="http://43.134.234.4:3001",
    api_key="sk-WaUmgZsMxgeHOpp8SJxK1rmVQxiwfiDJ"
)

# 上传文档
client.upload_document(content, filename, metadata)

# 语义搜索
results = client.search(query, top_k=5)

# 问答
result = client.query(question)
```

## ⚠️ 注意事项

1. **数据备份**: 定期备份 `data/rag/` 目录
2. **文档大小**: 单个文档建议不超过 10KB
3. **搜索性能**: 文档数超过 1000 时考虑优化索引
4. **字符编码**: 统一使用 UTF-8

## 📝 示例脚本

查看 `tests/e2e/test_rag_integration.py` 获取完整使用示例。

---

*最后更新：2026-02-28*
