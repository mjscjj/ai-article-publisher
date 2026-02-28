#!/usr/bin/env python3
"""
智能选题数据模型 - Topic Models
V3 智能选题模块数据模型定义

包含:
- Topic: 选题主表模型
- TopicScore: 评分记录模型 (5 维评分)
- Industry: 行业配置模型
- Angle: 角度配置模型

数据库：MySQL (youmind 数据库)
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# ============================================
# 枚举定义
# ============================================

class GradeEnum(str, Enum):
    """评分等级枚举"""
    S = "S"  # 90-100: 爆款潜质
    A = "A"  # 75-89: 优质选题
    B = "B"  # 60-74: 合格选题
    C = "C"  # 40-59: 需要改进
    D = "D"  # 0-39: 不建议采用


# ============================================
# 评分模型
# ============================================

class TopicScore(BaseModel):
    """
    选题评分模型
    
    对应数据库表：topic_scores
    
    5 维评分模型:
    - 热度分 (30%): 基于平台热度
    - 潜力分 (25%): 趋势预测
    - 匹配分 (20%): 与账号定位匹配度
    - 新颖分 (15%): 独特性/差异化
    - 可行分 (10%): 素材充足度
    """
    
    id: Optional[int] = Field(None, description="评分记录 ID")
    topic_id: str = Field(..., description="关联选题 ID")
    
    # 5 维评分 (0-100)
    heat: float = Field(0.0, ge=0, le=100, description="热度分 (30%)")
    potential: float = Field(0.0, ge=0, le=100, description="潜力分 (25%)")
    match: float = Field(0.0, ge=0, le=100, description="匹配分 (20%)")
    novelty: float = Field(0.0, ge=0, le=100, description="新颖分 (15%)")
    feasibility: float = Field(0.0, ge=0, le=100, description="可行分 (10%)")
    
    # 总分和等级
    total: float = Field(0.0, description="总分 (0-100)")
    grade: str = Field("C", description="评分等级 (S/A/B/C/D)")
    
    # 评分时间
    scored_at: datetime = Field(default_factory=datetime.now, description="评分时间")
    
    # 评分详情 (可选)
    details: Optional[Dict[str, Any]] = Field(None, description="评分详情/备注")
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "topic_id": "topic_001",
                "heat": 85.0,
                "potential": 78.0,
                "match": 90.0,
                "novelty": 72.0,
                "feasibility": 88.0,
                "total": 82.5,
                "grade": "A",
                "scored_at": "2026-03-02T10:00:00",
                "details": {"heat_source": "微博热榜", "trend": "上升"}
            }
        }
    
    @classmethod
    def calculate_score(
        cls,
        heat: float,
        potential: float,
        match: float,
        novelty: float,
        feasibility: float
    ) -> float:
        """
        计算加权总分
        
        权重:
        - 热度分：30%
        - 潜力分：25%
        - 匹配分：20%
        - 新颖分：15%
        - 可行分：10%
        """
        return (
            heat * 0.30 +
            potential * 0.25 +
            match * 0.20 +
            novelty * 0.15 +
            feasibility * 0.10
        )
    
    @classmethod
    def get_grade(cls, total: float) -> str:
        """根据总分获取等级"""
        if total >= 90:
            return GradeEnum.S.value
        elif total >= 75:
            return GradeEnum.A.value
        elif total >= 60:
            return GradeEnum.B.value
        elif total >= 40:
            return GradeEnum.C.value
        else:
            return GradeEnum.D.value
    
    def update_total(self):
        """更新总分和等级"""
        self.total = self.calculate_score(
            self.heat, self.potential, self.match, self.novelty, self.feasibility
        )
        self.grade = self.get_grade(self.total)
    
    @classmethod
    def from_database_row(cls, row: Dict[str, Any]) -> "TopicScore":
        """从数据库行记录创建模型实例"""
        # 注意：match 是 MySQL 保留字，查询时需要用反引号，但返回的 dict 键名仍然是'match'
        return cls(
            id=row.get('id'),
            topic_id=row['topic_id'],
            heat=row.get('heat', 0.0),
            potential=row.get('potential', 0.0),
            match=row.get('match', 0.0),  # pymysql 会返回原始列名
            novelty=row.get('novelty', 0.0),
            feasibility=row.get('feasibility', 0.0),
            total=row.get('total', 0.0),
            grade=row.get('grade', 'C'),
            scored_at=row.get('scored_at', datetime.now()),
            details=json.loads(row['details']) if row.get('details') and isinstance(row.get('details'), str) else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.dict()


# ============================================
# 行业配置模型
# ============================================

class Industry(BaseModel):
    """
    行业配置模型
    
    对应数据库表：topic_industries
    
    字段说明:
    - id: 行业 ID
    - name: 行业名称
    - code: 行业代码 (唯一标识)
    - description: 行业描述
    - data_sources: 数据源配置 (JSON)
    - score_weights: 评分权重配置 (JSON)
    - enabled: 是否启用
    """
    
    id: Optional[int] = Field(None, description="行业 ID")
    name: str = Field(..., max_length=50, description="行业名称")
    code: str = Field(..., max_length=50, description="行业代码")
    description: Optional[str] = Field(None, description="行业描述")
    data_sources: Optional[Dict[str, Any]] = Field(None, description="数据源配置")
    score_weights: Optional[Dict[str, float]] = Field(None, description="评分权重配置")
    enabled: bool = Field(True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "教育",
                "code": "education",
                "description": "K12 教育、高等教育、职业教育等",
                "data_sources": {"platforms": ["知乎", "公众号"], "keywords": ["教育", "学校"]},
                "score_weights": {"heat": 0.3, "potential": 0.25, "match": 0.2, "novelty": 0.15, "feasibility": 0.1},
                "enabled": True,
                "created_at": "2026-03-01T10:00:00"
            }
        }
    
    @classmethod
    def from_database_row(cls, row: Dict[str, Any]) -> "Industry":
        """从数据库行记录创建模型实例"""
        return cls(
            id=row.get('id'),
            name=row['name'],
            code=row['code'],
            description=row.get('description'),
            data_sources=json.loads(row['data_sources']) if row.get('data_sources') and isinstance(row.get('data_sources'), str) else None,
            score_weights=json.loads(row['score_weights']) if row.get('score_weights') and isinstance(row.get('score_weights'), str) else None,
            enabled=bool(row.get('enabled', True)),
            created_at=row.get('created_at', datetime.now()),
            updated_at=row.get('updated_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.dict()


# ============================================
# 角度配置模型
# ============================================

class Angle(BaseModel):
    """
    角度配置模型
    
    对应数据库表：topic_angles
    
    8 种标准切入角度:
    - deep_analysis: 深度分析
    - data_interpretation: 数据解读
    - opinion_comment: 观点评论
    - knowledge_pop: 知识科普
    - humor_tease: 幽默调侃
    - risk_warning: 风险警示
    - trend_forecast: 趋势预测
    - human_story: 人物故事
    """
    
    id: Optional[int] = Field(None, description="角度 ID")
    name: str = Field(..., max_length=50, description="角度名称")
    code: str = Field(..., max_length=50, description="角度代码")
    description: Optional[str] = Field(None, description="角度描述")
    icon: Optional[str] = Field(None, description="图标 emoji")
    prompt_template: Optional[str] = Field(None, description="AI 提示词模板")
    enabled: bool = Field(True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "深度分析",
                "code": "deep_analysis",
                "description": "事件背后的原因/逻辑/本质",
                "icon": "🔍",
                "prompt_template": "请深度分析{topic}背后的原因和逻辑...",
                "enabled": True,
                "created_at": "2026-03-01T10:00:00"
            }
        }
    
    @classmethod
    def from_database_row(cls, row: Dict[str, Any]) -> "Angle":
        """从数据库行记录创建模型实例"""
        return cls(
            id=row.get('id'),
            name=row['name'],
            code=row['code'],
            description=row.get('description'),
            icon=row.get('icon'),
            prompt_template=row.get('prompt_template'),
            enabled=bool(row.get('enabled', True)),
            created_at=row.get('created_at', datetime.now())
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.dict()


# ============================================
# 选题主表模型
# ============================================

class Topic(BaseModel):
    """
    选题主表模型
    
    对应数据库表：topics
    
    字段说明:
    - id: 选题唯一标识
    - title: 选题标题
    - industry: 所属行业
    - angle: 切入角度
    - source_hotnews: 来源热点 ID 列表
    - description: 选题描述
    - key_points: 核心要点
    - score: 关联评分
    - status: 选题状态
    """
    
    id: str = Field(..., description="选题唯一标识")
    title: str = Field(..., max_length=500, description="选题标题")
    industry: str = Field(..., max_length=50, description="所属行业")
    angle: str = Field(..., max_length=50, description="切入角度")
    source_hotnews: Optional[List[str]] = Field(None, description="来源热点 ID 列表")
    description: Optional[str] = Field(None, description="选题描述")
    key_points: Optional[List[str]] = Field(None, description="核心要点")
    
    # 评分 (可以是 TopicScore 对象或总分)
    score: Optional[TopicScore] = Field(None, description="评分详情")
    score_total: Optional[float] = Field(None, description="总分 (冗余字段，便于排序)")
    grade: Optional[str] = Field(None, description="评分等级 (冗余字段)")
    
    # 状态
    status: str = Field("draft", description="选题状态 (draft/reviewed/approved/rejected)")
    
    # 时间
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    # 扩展字段
    extra_data: Optional[Dict[str, Any]] = Field(None, description="扩展数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "topic_001",
                "title": "AI 如何重塑 K12 教育",
                "industry": "教育",
                "angle": "深度分析",
                "source_hotnews": ["weibo_12345", "zhihu_67890"],
                "description": "探讨 AI 技术在 K12 教育中的应用和影响",
                "key_points": ["AI 教育现状", "技术应用场景", "未来发展趋势"],
                "score": {"total": 82.5, "grade": "A"},
                "score_total": 82.5,
                "grade": "A",
                "status": "draft",
                "created_at": "2026-03-02T10:00:00"
            }
        }
    
    @classmethod
    def from_database_row(
        cls, 
        row: Dict[str, Any], 
        score_row: Optional[Dict[str, Any]] = None
    ) -> "Topic":
        """
        从数据库行记录创建模型实例
        
        Args:
            row: topics 表查询结果
            score_row: topic_scores 表查询结果 (可选)
        """
        # 解析 source_hotnews (JSON 数组)
        source_hotnews = None
        if row.get('source_hotnews'):
            if isinstance(row['source_hotnews'], str):
                source_hotnews = json.loads(row['source_hotnews'])
            else:
                source_hotnews = row['source_hotnews']
        
        # 解析 key_points (JSON 数组)
        key_points = None
        if row.get('key_points'):
            if isinstance(row['key_points'], str):
                key_points = json.loads(row['key_points'])
            else:
                key_points = row['key_points']
        
        # 解析 extra_data (JSON 对象)
        extra_data = None
        if row.get('extra_data'):
            if isinstance(row['extra_data'], str):
                extra_data = json.loads(row['extra_data'])
            else:
                extra_data = row['extra_data']
        
        # 构建评分对象
        score = None
        if score_row:
            score = TopicScore.from_database_row(score_row)
        
        return cls(
            id=row['id'],
            title=row['title'],
            industry=row['industry'],
            angle=row['angle'],
            source_hotnews=source_hotnews,
            description=row.get('description'),
            key_points=key_points,
            score=score,
            score_total=row.get('score_total'),
            grade=row.get('grade'),
            status=row.get('status', 'draft'),
            created_at=row.get('created_at', datetime.now()),
            updated_at=row.get('updated_at'),
            extra_data=extra_data
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = self.dict()
        # 处理嵌套的 score 对象
        if self.score and isinstance(self.score, TopicScore):
            data['score'] = self.score.to_dict()
        return data
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        import json
        from datetime import datetime
        
        data = self.to_dict()
        # 处理 datetime 序列化
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        return json.dumps(data, ensure_ascii=False, default=str)


# ============================================
# 辅助数据模型
# ============================================

class TopicComparison(BaseModel):
    """选题对比结果模型"""
    
    topics: List[Topic] = Field(..., description="对比的选题列表")
    comparison: Dict[str, Any] = Field(..., description="对比分析结果")
    recommendation: str = Field(..., description="推荐建议")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topics": [...],
                "comparison": {
                    "avg_score": 75.5,
                    "best_heat": "topic_001",
                    "best_potential": "topic_002"
                },
                "recommendation": "推荐 topic_001，热度最高且匹配度好"
            }
        }


class GenerateRequest(BaseModel):
    """选题生成请求模型"""
    
    industries: List[str] = Field(..., description="行业列表")
    angles: List[str] = Field(..., description="角度列表")
    hotnews_ids: Optional[List[str]] = Field(None, description="基于热点 ID 列表")
    count: int = Field(20, ge=1, le=100, description="生成数量")
    min_score: float = Field(60.0, ge=0, le=100, description="最低评分要求")
    
    class Config:
        json_schema_extra = {
            "example": {
                "industries": ["教育", "科技"],
                "angles": ["深度分析", "数据解读"],
                "hotnews_ids": ["weibo_12345", "zhihu_67890"],
                "count": 20,
                "min_score": 60.0
            }
        }


# ============================================
# 数据库表结构 SQL
# ============================================

CREATE_TABLE_SQL = """
-- 选题主表
CREATE TABLE IF NOT EXISTS topics (
    id VARCHAR(64) PRIMARY KEY COMMENT '选题唯一标识',
    title VARCHAR(500) NOT NULL COMMENT '选题标题',
    industry VARCHAR(50) NOT NULL COMMENT '所属行业',
    angle VARCHAR(50) NOT NULL COMMENT '切入角度',
    source_hotnews JSON COMMENT '来源热点 ID 列表',
    description TEXT COMMENT '选题描述',
    key_points JSON COMMENT '核心要点',
    score_total DECIMAL(5,2) COMMENT '总分 (冗余字段)',
    grade VARCHAR(10) COMMENT '评分等级',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '选题状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    extra_data JSON COMMENT '扩展数据',
    INDEX idx_industry (industry),
    INDEX idx_angle (angle),
    INDEX idx_score (score_total),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 评分记录表
CREATE TABLE IF NOT EXISTS topic_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id VARCHAR(64) NOT NULL COMMENT '关联选题 ID',
    heat DECIMAL(5,2) DEFAULT 0 COMMENT '热度分 (30%)',
    potential DECIMAL(5,2) DEFAULT 0 COMMENT '潜力分 (25%)',
    `match` DECIMAL(5,2) DEFAULT 0 COMMENT '匹配分 (20%)',
    novelty DECIMAL(5,2) DEFAULT 0 COMMENT '新颖分 (15%)',
    feasibility DECIMAL(5,2) DEFAULT 0 COMMENT '可行分 (10%)',
    total DECIMAL(5,2) DEFAULT 0 COMMENT '总分',
    grade VARCHAR(10) DEFAULT 'C' COMMENT '评分等级',
    scored_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '评分时间',
    details JSON COMMENT '评分详情',
    INDEX idx_topic (topic_id),
    INDEX idx_total (total),
    INDEX idx_grade (grade),
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 行业配置表
CREATE TABLE IF NOT EXISTS topic_industries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '行业名称',
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '行业代码',
    description TEXT COMMENT '行业描述',
    data_sources JSON COMMENT '数据源配置',
    score_weights JSON COMMENT '评分权重配置',
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 角度配置表
CREATE TABLE IF NOT EXISTS topic_angles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '角度名称',
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '角度代码',
    description TEXT COMMENT '角度描述',
    icon VARCHAR(20) COMMENT '图标 emoji',
    prompt_template TEXT COMMENT 'AI 提示词模板',
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_code (code),
    INDEX idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 初始化数据
-- 预置行业
INSERT INTO topic_industries (name, code, description, enabled) VALUES
('教育', 'education', 'K12 教育、高等教育、职业教育等', TRUE),
('科技', 'technology', '互联网、人工智能、数码科技等', TRUE),
('财经', 'finance', '金融、投资、理财、经济等', TRUE),
('娱乐', 'entertainment', '影视、音乐、明星、综艺等', TRUE),
('体育', 'sports', '体育赛事、运动员、健身等', TRUE),
('健康', 'health', '医疗健康、养生、心理等', TRUE),
('职场', 'career', '求职、职场技能、职业发展等', TRUE),
('生活', 'lifestyle', '生活方式、旅游、美食等', TRUE);

-- 预置角度
INSERT INTO topic_angles (name, code, description, icon, enabled) VALUES
('深度分析', 'deep_analysis', '事件背后的原因/逻辑/本质', '🔍', TRUE),
('数据解读', 'data_interpretation', '用数据说话，图表可视化', '📊', TRUE),
('观点评论', 'opinion_comment', '独特视角/争议性观点', '💡', TRUE),
('知识科普', 'knowledge_pop', '专业知识普及，易懂有趣', '🎓', TRUE),
('幽默调侃', 'humor_tease', '轻松有趣，梗文化', '😂', TRUE),
('风险警示', 'risk_warning', '提醒/避坑/注意事项', '⚠️', TRUE),
('趋势预测', 'trend_forecast', '未来走向/发展趋势', '🚀', TRUE),
('人物故事', 'human_story', '以人为核心的故事叙述', '👥', TRUE);
"""
