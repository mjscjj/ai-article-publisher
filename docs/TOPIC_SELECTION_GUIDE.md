# 智能选题系统使用指南

> 版本: 1.0.0
> 更新时间: 2026-02-22

---

## ⚠️ 成本控制说明

### 所有组件均免费

| 模块 | 技术方案 | 费用 |
|------|----------|------|
| 基础评分 | 本地规则引擎 | **$0** |
| 趋势预测 | 简单统计规则 | **$0** |
| LLM分析 | OpenRouter DeepSeek R1 免费模型 | **$0** |
| **总计** | - | **$0** |

### LLM 配置

**模型**: `openrouter/deepseek/deepseek-r1-0528:free`
**别名**: `deepseek-free`
**费用**: 完全免费

**配置方法**:
```bash
# 设置环境变量
export OPENROUTER_API_KEY="your-openrouter-api-key"

# 或在代码中设置
import os
os.environ["OPENROUTER_API_KEY"] = "your-key"
```

**获取 API Key**: https://openrouter.ai/keys

---

## 快速开始

### 1. 基础使用（无LLM）

```bash
# 分析热点数据中的选题
cd /root/.openclaw/workspace-writer/ai-article-publisher

# 不使用 LLM，纯本地计算
python3 topic_selector.py \
  --input data/hotnews/daily/2026-02-22.json \
  --top 10 \
  --no-llm

# 费用: $0
```

### 2. 完整使用（含LLM分析）

```bash
# 设置 API Key
export OPENROUTER_API_KEY="sk-or-..."

# 完整分析
python3 topic_selector.py \
  --input data/hotnews/daily/2026-02-22.json \
  --top 5 \
  --domains "教育,心理学,AI"

# 费用: $0 (DeepSeek R1 免费)
```

### 3. 仅趋势分析

```bash
python3 trend_analyzer.py \
  --input data/hotnews/daily/2026-02-22.json \
  --top 10

# 费用: $0
```

### 4. 仅LLM分析

```bash
export OPENROUTER_API_KEY="sk-or-..."

python3 topic_analyzer.py \
  --input data/hotnews/daily/2026-02-22.json \
  --top 5 \
  --domains "教育,心理学,AI"

# 费用: $0 (DeepSeek R1 免费)
```

---

## 输出示例

```
======================================================================
智能选题选择器 v1.0.0
======================================================================
候选选题: 100 个
返回数量: 5 个
使用 LLM: 是

组件配置:
  - 基础评分: rules (免费)
  - 趋势分析: simple_rules (免费)
  - LLM分析: deepseek-free (免费)
总成本: $0
======================================================================

[1/10] 分析: AI 编程助手对比：Claude vs GPT-4...
    基础评分: 85
    趋势评分: 78 (上升)
    LLM评分: 88 (推荐)
    ✅ 综合评分: 84.5 (强烈推荐)

🔥 【1】AI 编程助手对比：Claude vs GPT-4
    来源: 少数派 | 分类: 科技
    综合评分: 84.5 (强烈推荐)
    分项: 基础85 + 趋势78 + LLM88
    趋势: 上升 | 爆发期 (预计持续 2-3 天)
    发布建议: 尽快发布
    写作角度:
      - 产品对比: Claude vs GPT-4，谁更适合编程？

======================================================================
成本说明:
- 基础评分: $0 (本地规则)
- 趋势分析: $0 (本地计算)
- LLM分析: $0 (DeepSeek R1 免费模型)
- 总成本: $0
======================================================================
```

---

## 模块说明

### topic_selector.py - 统一入口

**功能**: 整合基础评分 + 趋势分析 + LLM 分析

**参数**:
- `--input, -i`: 输入 JSON 文件路径
- `--output, -o`: 输出格式 (text/json)
- `--top, -n`: 返回数量 (默认 5)
- `--domains, -d`: 用户关注领域 (逗号分隔)
- `--no-llm`: 不使用 LLM 分析
- `--quiet, -q`: 安静模式

**评分权重**:
- 基础评分: 30%
- 趋势评分: 30%
- LLM 评分: 40%

---

### topic_analyzer.py - LLM 分析器

**功能**: 使用 LLM 进行选题质量评估

**依赖**: OpenRouter API Key

**输出**:
- 新闻价值评分
- 用户匹配度评分
- 竞争分析
- 写作难度
- 预期效果
- 写作角度建议
- 风险提示

**费用**: $0 (DeepSeek R1 免费)

---

### trend_analyzer.py - 趋势分析器

**功能**: 分析热点趋势和生命周期

**算法**: 简单统计规则 (不使用复杂模型)

**输出**:
- 增长率
- 衰减因子
- 趋势方向 (上升/平稳/下降)
- 生命周期预测
- 最佳发布时机

**费用**: $0 (本地计算)

---

## 集成到 Pipeline

```python
# 在 pipeline.py 中使用

from topic_selector import select_topics

# 加载热点数据
topics = load_hotnews()

# 选择最佳选题
selected = select_topics(
    topics,
    user_profile={
        "domains": ["教育", "心理学", "AI"],
        "style": "深度分析",
    },
    top_n=5,
    use_llm=True,
)

# 获取最佳选题
best_topic = selected[0]
print(f"推荐选题: {best_topic['title']}")
print(f"综合评分: {best_topic['final_score']}")
```

---

## 注意事项

### 1. LLM API Key 配置

**必须配置** OpenRouter API Key 才能使用 LLM 分析:
```bash
export OPENROUTER_API_KEY="sk-or-..."
```

如果未配置，LLM 分析会被跳过，但仍可使用基础评分和趋势分析。

### 2. 频率限制

DeepSeek R1 免费模型可能有请求频率限制:
- 建议每次分析不超过 10 个选题
- 批量分析时已内置 1 秒延迟

### 3. 评分权重调整

可在 `topic_selector.py` 中调整权重:
```python
SELECTOR_CONFIG["weights"] = {
    "base_score": 0.4,   # 提高基础评分权重
    "trend_score": 0.3,
    "llm_score": 0.3,    # 降低 LLM 权重
}
```

---

## 成本对比

| 方案 | 模型 | 费用/100次请求 |
|------|------|---------------|
| **当前方案** | DeepSeek R1 免费 | **$0** |
| GPT-4 | OpenAI GPT-4 | ~$3-5 |
| Claude 3.5 | Anthropic | ~$2-4 |
| DeepSeek V3 | DeepSeek 付费 | ~$0.1-0.5 |

**节省成本**: 100%

---

## 文件结构

```
ai-article-publisher/
├── topic_selector.py      # 统一入口 (10KB)
├── topic_analyzer.py      # LLM 分析器 (10KB)
├── trend_analyzer.py      # 趋势分析器 (8KB)
├── topic_scorer.py        # 基础评分 (已有)
├── pipeline.py            # 工作流 (已有)
└── docs/
    └── TOPIC_SELECTION_GUIDE.md  # 本文档
```

---

*最后更新: 2026-02-22*