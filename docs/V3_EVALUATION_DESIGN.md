# 工作评价机制设计方案

> 创建时间：2026-03-02  
> 模型：DeepSeek V3 (深度分析)  
> 目标：对 AI 生成的文章/选题/热点进行智能评估

---

## 📊 评价体系

### 评价维度

| 维度 | 权重 | 说明 |
|------|------|------|
| **内容质量** | 30% | 准确性/深度/数据支撑 |
| **结构逻辑** | 25% | 框架清晰/层次分明/过渡自然 |
| **表达文采** | 20% | 语言流畅/修辞运用/金句 |
| **传播价值** | 15% | 话题性/共鸣点/传播潜力 |
| **创新独特** | 10% | 视角新颖/差异化/独特见解 |

### 评分等级

| 等级 | 分数 | 说明 | 处理 |
|------|------|------|------|
| S | 90-100 | 爆款潜质 | 优先发布 + 重点推广 |
| A | 80-89 | 优质内容 | 正常发布 |
| B | 70-79 | 合格作品 | 修改后发布 |
| C | 60-69 | 需要改进 | 返回重写 |
| D | 0-59 | 质量较差 | 废弃/大改 |

---

## 🤖 DeepSeek 评价模型

### 模型选择

**主模型**: `deepseek/deepseek-chat` (高性价比)
**备用模型**: `deepseek/deepseek-r1-0528:free` (免费)

### API 配置

```python
DEEPSEEK_CONFIG = {
    'base_url': 'https://api.deepseek.com',
    'api_key': os.getenv('DEEPSEEK_API_KEY'),
    'model': 'deepseek-chat',
    'max_tokens': 2000,
    'temperature': 0.3  # 评价需要稳定输出
}
```

### 评价 Prompt 模板

```
你是一位资深的内容质量评估专家，拥有 10 年媒体从业经验。

请对以下文章进行专业评估：

【文章标题】
{title}

【文章内容】
{content}

【评估要求】
1. 从 5 个维度打分 (0-100):
   - 内容质量 (30%): 准确性、深度、数据支撑
   - 结构逻辑 (25%): 框架清晰、层次分明、过渡自然
   - 表达文采 (20%): 语言流畅、修辞运用、金句
   - 传播价值 (15%): 话题性、共鸣点、传播潜力
   - 创新独特 (10%): 视角新颖、差异化、独特见解

2. 给出总体评分和等级 (S/A/B/C/D)

3. 指出 3 个优点

4. 指出 3 个改进建议

5. 给出最终推荐 (优先发布/正常发布/修改后发布/返回重写/废弃)

请严格按照以下 JSON 格式输出:
{
  "scores": {
    "content": 85,
    "structure": 80,
    "expression": 75,
    "viral": 90,
    "innovation": 70
  },
  "total_score": 82,
  "grade": "A",
  "strengths": ["优点 1", "优点 2", "优点 3"],
  "improvements": ["建议 1", "建议 2", "建议 3"],
  "recommendation": "正常发布",
  "comment": "总体评价"
}
```

---

## 🏗️ 技术实现

### 核心模块

```
core/
├── evaluation_service.py      # 评价服务
├── deepseek_client.py         # DeepSeek 客户端
└── evaluation_prompts.py      # Prompt 模板库

api/v3/
└── evaluation.py              # 评价 API

models/
└── evaluation.py              # 评价数据模型

frontend/
└── v3_evaluation.html         # 评价界面
```

### 评价流程

```
1. 用户提交文章/选题
   ↓
2. 调用 DeepSeek API 进行智能评估
   ↓
3. 解析评分结果
   ↓
4. 存储评价记录
   ↓
5. 返回评估报告
   ↓
6. 可视化展示 (雷达图 + 建议)
```

### 数据库设计

```sql
-- 评价记录表
CREATE TABLE evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    target_type VARCHAR(50),      -- article/topic
    target_id VARCHAR(64),        -- 目标 ID
    model_used VARCHAR(50),       -- 使用的模型
    total_score FLOAT,            -- 总分
    grade VARCHAR(10),            -- 等级
    content_score FLOAT,          -- 内容分
    structure_score FLOAT,        -- 结构分
    expression_score FLOAT,       -- 表达分
    viral_score FLOAT,            -- 传播分
    innovation_score FLOAT,       -- 创新分
    strengths JSON,               -- 优点列表
    improvements JSON,            -- 改进建议
    recommendation VARCHAR(50),   -- 推荐操作
    comment TEXT,                 -- 总体评价
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_target (target_type, target_id),
    INDEX idx_score (total_score),
    INDEX idx_grade (grade)
);
```

---

## 📱 前端界面

### 评价页面功能

1. **文章输入**: 粘贴文章或选择已有文章
2. **一键评估**: 调用 DeepSeek 进行智能评价
3. **雷达图展示**: 5 维度可视化
4. **详细报告**: 优点/建议/推荐
5. **历史对比**: 查看历史评价记录
6. **批量评估**: 多篇同时评估

---

## 🔄 与现有系统集成

### 集成点

| 模块 | 集成方式 |
|------|---------|
| **写作工厂** | 写作完成后自动评估 |
| **选题模块** | 选题评分后二次评估 |
| **发布流程** | 评估达标才允许发布 |
| **数据看板** | 展示评估统计 |

### 自动化规则

```python
# 发布前强制评估
if article.total_score < 70:
    return "需要修改后才能发布"
elif article.total_score >= 85:
    return "优先发布 + 重点推广"
else:
    return "正常发布"
```

---

## 💰 成本控制

### 评估成本

| 模型 | 单次评估 | 1000 次 |
|------|---------|--------|
| deepseek-chat | ¥0.02 | ¥20 |
| deepseek-r1-free | ¥0 | ¥0 |

### 优化策略

1. **缓存机制**: 相同文章不重复评估
2. **分级评估**: 
   - 初稿用免费模型
   - 终稿用付费模型
3. **批量评估**: 合并请求降低成本

---

## 📊 成功指标

| 指标 | 目标值 |
|------|--------|
| 评估准确率 | > 85% (与人工对比) |
| 响应时间 | < 10 秒 |
| 用户满意度 | > 90% |
| 成本/篇 | < ¥0.05 |

---

*下一步：实现核心模块*
