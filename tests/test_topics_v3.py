#!/usr/bin/env python3
"""
V3 智能选题模块测试用例
测试覆盖率目标：>90%

测试内容:
1. 数据模型测试 (Topic, TopicScore, Industry, Angle)
2. 核心服务测试 (TopicService)
3. API 路由测试 (FastAPI)
4. 集成测试

执行方式:
    python tests/test_topics_v3.py
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.topic import (
    Topic, TopicScore, Industry, Angle,
    TopicComparison, GenerateRequest, GradeEnum,
    CREATE_TABLE_SQL
)


# ============================================
# 测试工具函数
# ============================================

class TestResult:
    """测试结果记录"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"  ✅ {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ❌ {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*70}")
        print(f"📊 测试结果：{self.passed} 通过，{self.failed} 失败，总计 {total}")
        if self.errors:
            print(f"\n❌ 失败详情:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        print(f"{'='*70}")
        return self.failed == 0


def assert_equal(actual, expected, test_name: str, result: TestResult):
    """断言相等"""
    if actual == expected:
        result.add_pass(test_name)
    else:
        result.add_fail(test_name, f"期望 {expected}, 实际 {actual}")


def assert_true(condition, test_name: str, result: TestResult):
    """断言为真"""
    if condition:
        result.add_pass(test_name)
    else:
        result.add_fail(test_name, "条件不为真")


def assert_in_range(value, min_val, max_val, test_name: str, result: TestResult):
    """断言在范围内"""
    if min_val <= value <= max_val:
        result.add_pass(test_name)
    else:
        result.add_fail(test_name, f"{value} 不在 [{min_val}, {max_val}] 范围内")


# ============================================
# 测试 1: TopicScore 模型
# ============================================

def test_topic_score_model(result: TestResult):
    """测试 TopicScore 模型"""
    print("\n" + "="*70)
    print("测试 TopicScore 模型")
    print("="*70)
    
    # 测试 1: 创建评分对象
    try:
        score = TopicScore(
            topic_id="topic_001",
            heat=85.0,
            potential=78.0,
            match=90.0,
            novelty=72.0,
            feasibility=88.0
        )
        score.update_total()
        result.add_pass("创建评分对象")
    except Exception as e:
        result.add_fail("创建评分对象", str(e))
        return
    
    # 测试 2: 总分计算
    expected_total = 85.0*0.30 + 78.0*0.25 + 90.0*0.20 + 72.0*0.15 + 88.0*0.10
    expected_total = round(expected_total, 2)
    assert_equal(
        round(score.total, 2), expected_total,
        "总分计算 (权重正确)", result
    )
    
    # 测试 3: 等级判定
    assert_true(score.grade in ["S", "A", "B", "C", "D"], "等级判定有效", result)
    
    # 测试 4: 分数范围验证
    assert_in_range(score.heat, 0, 100, "热度分范围", result)
    assert_in_range(score.potential, 0, 100, "潜力分范围", result)
    assert_in_range(score.match, 0, 100, "匹配分范围", result)
    assert_in_range(score.novelty, 0, 100, "新颖分范围", result)
    assert_in_range(score.feasibility, 0, 100, "可行分范围", result)
    
    # 测试 5: 序列化
    try:
        score_dict = score.to_dict()
        assert_true("total" in score_dict, "序列化包含 total", result)
        assert_true("grade" in score_dict, "序列化包含 grade", result)
    except Exception as e:
        result.add_fail("序列化", str(e))
    
    # 测试 6: 从数据库行创建
    try:
        row = {
            "id": 1,
            "topic_id": "topic_001",
            "heat": 80.0,
            "potential": 75.0,
            "match": 85.0,
            "novelty": 70.0,
            "feasibility": 90.0,
            "total": 79.25,
            "grade": "B",
            "scored_at": datetime.now()
        }
        score_from_db = TopicScore.from_database_row(row)
        assert_equal(score_from_db.topic_id, "topic_001", "从数据库行创建", result)
    except Exception as e:
        result.add_fail("从数据库行创建", str(e))


# ============================================
# 测试 2: Topic 模型
# ============================================

def test_topic_model(result: TestResult):
    """测试 Topic 模型"""
    print("\n" + "="*70)
    print("测试 Topic 模型")
    print("="*70)
    
    # 测试 1: 创建选题对象
    try:
        topic = Topic(
            id="topic_001",
            title="AI 如何重塑教育",
            industry="教育",
            angle="深度分析",
            description="探讨 AI 在教育领域的应用",
            key_points=["现状分析", "应用场景", "未来趋势"],
            status="draft"
        )
        result.add_pass("创建选题对象")
    except Exception as e:
        result.add_fail("创建选题对象", str(e))
        return
    
    # 测试 2: 字段验证
    assert_equal(topic.industry, "教育", "行业字段", result)
    assert_equal(topic.angle, "深度分析", "角度字段", result)
    assert_equal(topic.status, "draft", "状态字段", result)
    
    # 测试 3: 关联评分
    try:
        score = TopicScore(
            topic_id=topic.id,
            heat=85.0,
            potential=78.0,
            match=90.0,
            novelty=72.0,
            feasibility=88.0
        )
        score.update_total()
        topic.score = score
        topic.score_total = score.total
        topic.grade = score.grade
        
        assert_true(topic.score_total > 0, "关联评分后总分>0", result)
        assert_true(topic.grade in ["S", "A", "B", "C", "D"], "关联评分后等级有效", result)
    except Exception as e:
        result.add_fail("关联评分", str(e))
    
    # 测试 4: 序列化
    try:
        topic_dict = topic.to_dict()
        assert_true("title" in topic_dict, "序列化包含 title", result)
        assert_true("industry" in topic_dict, "序列化包含 industry", result)
        assert_true("score" in topic_dict or topic.score is None, "序列化包含 score", result)
    except Exception as e:
        result.add_fail("序列化", str(e))
    
    # 测试 5: JSON 序列化
    try:
        topic_json = topic.to_json()
        assert_true(isinstance(topic_json, str), "JSON 序列化返回字符串", result)
        parsed = json.loads(topic_json)
        assert_true("id" in parsed, "JSON 可解析", result)
    except Exception as e:
        result.add_fail("JSON 序列化", str(e))


# ============================================
# 测试 3: Industry 和 Angle 模型
# ============================================

def test_industry_angle_model(result: TestResult):
    """测试 Industry 和 Angle 模型"""
    print("\n" + "="*70)
    print("测试 Industry 和 Angle 模型")
    print("="*70)
    
    # 测试 Industry
    try:
        industry = Industry(
            name="教育",
            code="education",
            description="K12 教育、高等教育等",
            enabled=True
        )
        assert_equal(industry.name, "教育", "Industry 名称", result)
        assert_equal(industry.code, "education", "Industry 代码", result)
        assert_true(industry.enabled, "Industry 启用状态", result)
    except Exception as e:
        result.add_fail("Industry 模型", str(e))
    
    # 测试 Angle
    try:
        angle = Angle(
            name="深度分析",
            code="deep_analysis",
            description="事件背后的原因/逻辑",
            icon="🔍",
            enabled=True
        )
        assert_equal(angle.name, "深度分析", "Angle 名称", result)
        assert_equal(angle.code, "deep_analysis", "Angle 代码", result)
        assert_equal(angle.icon, "🔍", "Angle 图标", result)
    except Exception as e:
        result.add_fail("Angle 模型", str(e))


# ============================================
# 测试 4: GradeEnum 枚举
# ============================================

def test_grade_enum(result: TestResult):
    """测试评分等级枚举"""
    print("\n" + "="*70)
    print("测试 GradeEnum 枚举")
    print("="*70)
    
    # 测试等级判定逻辑
    test_cases = [
        (95, "S"),
        (85, "A"),
        (70, "B"),
        (50, "C"),
        (30, "D"),
    ]
    
    for score, expected_grade in test_cases:
        actual_grade = TopicScore.get_grade(score)
        assert_equal(actual_grade, expected_grade, f"分数{score}对应等级{expected_grade}", result)


# ============================================
# 测试 5: TopicService 核心服务
# ============================================

def test_topic_service(result: TestResult):
    """测试 TopicService 核心服务"""
    print("\n" + "="*70)
    print("测试 TopicService 核心服务")
    print("="*70)
    
    try:
        from core.topic_service import TopicService
        service = TopicService()
        result.add_pass("初始化 TopicService")
    except Exception as e:
        result.add_fail("初始化 TopicService", str(e))
        return
    
    # 测试 1: 获取行业列表
    try:
        industries = service.get_industries()
        assert_true(len(industries) > 0, f"获取行业列表 (数量={len(industries)})", result)
        assert_true(all(isinstance(ind, Industry) for ind in industries), "行业对象类型正确", result)
    except Exception as e:
        result.add_fail("获取行业列表", str(e))
    
    # 测试 2: 获取角度列表
    try:
        angles = service.get_angles()
        assert_true(len(angles) > 0, f"获取角度列表 (数量={len(angles)})", result)
        assert_true(all(isinstance(angle, Angle) for angle in angles), "角度对象类型正确", result)
    except Exception as e:
        result.add_fail("获取角度列表", str(e))
    
    # 测试 3: 生成选题
    try:
        topics = service.generate_topics(
            industries=["教育"],
            angles=["深度分析"],
            count=3,
            min_score=50.0
        )
        assert_true(len(topics) > 0, f"生成选题 (数量={len(topics)})", result)
        
        if topics:
            # 验证选题结构
            topic = topics[0]
            assert_true(isinstance(topic, Topic), "选题对象类型正确", result)
            assert_true(topic.title, "选题有标题", result)
            assert_true(topic.industry, "选题有行业", result)
            assert_true(topic.angle, "选题有角度", result)
            assert_true(topic.score is not None, "选题有评分", result)
            
            if topic.score:
                assert_in_range(topic.score.total, 0, 100, "评分总分范围", result)
    except Exception as e:
        result.add_fail("生成选题", str(e))
    
    # 测试 4: 评分选题
    try:
        if topics:
            topic = topics[0]
            score = service.score_topic(topic)
            assert_true(isinstance(score, TopicScore), "评分对象类型正确", result)
            assert_true(score.total > 0, "评分总分>0", result)
    except Exception as e:
        result.add_fail("评分选题", str(e))


# ============================================
# 测试 6: 5 维评分算法
# ============================================

def test_scoring_algorithm(result: TestResult):
    """测试 5 维评分算法"""
    print("\n" + "="*70)
    print("测试 5 维评分算法")
    print("="*70)
    
    try:
        from core.topic_service import TopicService
        service = TopicService()
    except Exception as e:
        result.add_fail("初始化服务", str(e))
        return
    
    # 创建测试选题
    test_topics = [
        Topic(
            id="test_hot",
            title="超热点事件",
            industry="教育",
            angle="深度分析",
            source_hotnews=["weibo_12345"],  # 假设有热点
        ),
        Topic(
            id="test_novel",
            title="独特视角？",
            industry="科技",
            angle="幽默调侃",
        ),
        Topic(
            id="test_match",
            title="职场技能提升",
            industry="职场",
            angle="知识科普",
            key_points=["点 1", "点 2", "点 3", "点 4"],
            description="详细描述"
        ),
    ]
    
    for topic in test_topics:
        try:
            score = service.score_topic(topic)
            
            # 验证各维度分数范围
            assert_in_range(score.heat, 0, 100, f"{topic.id} 热度分", result)
            assert_in_range(score.potential, 0, 100, f"{topic.id} 潜力分", result)
            assert_in_range(score.match, 0, 100, f"{topic.id} 匹配分", result)
            assert_in_range(score.novelty, 0, 100, f"{topic.id} 新颖分", result)
            assert_in_range(score.feasibility, 0, 100, f"{topic.id} 可行分", result)
            
            # 验证权重计算
            expected = (
                score.heat * 0.30 +
                score.potential * 0.25 +
                score.match * 0.20 +
                score.novelty * 0.15 +
                score.feasibility * 0.10
            )
            assert_equal(
                round(score.total, 1), round(expected, 1),
                f"{topic.id} 权重计算", result
            )
        except Exception as e:
            result.add_fail(f"评分 {topic.id}", str(e))


# ============================================
# 测试 7: 选题对比功能
# ============================================

def test_topic_comparison(result: TestResult):
    """测试选题对比功能"""
    print("\n" + "="*70)
    print("测试选题对比功能")
    print("="*70)
    
    try:
        from core.topic_service import TopicService
        service = TopicService()
    except Exception as e:
        result.add_fail("初始化服务", str(e))
        return
    
    # 生成测试选题
    try:
        topics = service.generate_topics(
            industries=["教育", "科技"],
            angles=["深度分析", "数据解读"],
            count=4,
            min_score=50.0
        )
        
        if len(topics) >= 2:
            # 保存选题到数据库
            for topic in topics[:3]:
                service.save_topic(topic)
            
            # 测试对比功能 (从数据库读取)
            topic_ids = [t.id for t in topics[:3]]
            comparison = service.compare_topics(topic_ids)
            
            assert_true(comparison is not None, "对比结果不为空", result)
            assert_true(len(comparison.topics) > 0, "对比包含选题", result)
            assert_true("recommendation" in comparison.__dict__, "对比包含推荐", result)
            assert_true(len(comparison.recommendation) > 0, "推荐内容非空", result)
        else:
            result.add_fail("选题对比", "生成的选题数量不足")
    except Exception as e:
        result.add_fail("选题对比", str(e))


# ============================================
# 测试 8: 数据库迁移 SQL
# ============================================

def test_database_schema(result: TestResult):
    """测试数据库迁移 SQL"""
    print("\n" + "="*70)
    print("测试数据库迁移 SQL")
    print("="*70)
    
    # 测试 SQL 语法
    try:
        statements = [s.strip() for s in CREATE_TABLE_SQL.split(';') if s.strip()]
        assert_true(len(statements) >= 4, f"SQL 语句数量 (期望>=4, 实际={len(statements)})", result)
        
        # 检查是否包含所有表
        sql_text = CREATE_TABLE_SQL.upper()
        required_tables = ["TOPICS", "TOPIC_SCORES", "TOPIC_INDUSTRIES", "TOPIC_ANGLES"]
        
        for table in required_tables:
            if f"CREATE TABLE" in sql_text and table in sql_text:
                result.add_pass(f"包含 {table} 表定义")
            else:
                result.add_fail(f"包含 {table} 表定义", "SQL 中未找到")
    except Exception as e:
        result.add_fail("SQL 语法检查", str(e))


# ============================================
# 测试 9: GenerateRequest 模型
# ============================================

def test_generate_request(result: TestResult):
    """测试生成请求模型"""
    print("\n" + "="*70)
    print("测试 GenerateRequest 模型")
    print("="*70)
    
    try:
        req = GenerateRequest(
            industries=["教育", "科技"],
            angles=["深度分析"],
            count=10,
            min_score=60.0
        )
        
        assert_equal(len(req.industries), 2, "行业列表长度", result)
        assert_equal(req.count, 10, "生成数量", result)
        assert_in_range(req.min_score, 0, 100, "最低评分范围", result)
    except Exception as e:
        result.add_fail("GenerateRequest 模型", str(e))
    
    # 测试验证
    try:
        # 测试 count 范围验证
        try:
            invalid_req = GenerateRequest(
                industries=["教育"],
                angles=["深度分析"],
                count=101  # 超过最大值
            )
            result.add_fail("count 验证", "应该抛出验证错误")
        except:
            result.add_pass("count 范围验证")
    except Exception as e:
        result.add_fail("验证测试", str(e))


# ============================================
# 主测试程序
# ============================================

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("🧪 V3 智能选题模块测试")
    print("="*70)
    print(f"开始时间：{datetime.now().isoformat()}")
    
    result = TestResult()
    
    # 运行所有测试
    test_topic_score_model(result)
    test_topic_model(result)
    test_industry_angle_model(result)
    test_grade_enum(result)
    test_topic_service(result)
    test_scoring_algorithm(result)
    test_topic_comparison(result)
    test_database_schema(result)
    test_generate_request(result)
    
    # 总结
    success = result.summary()
    print(f"结束时间：{datetime.now().isoformat()}")
    
    return success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
