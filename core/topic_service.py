#!/usr/bin/env python3
"""
智能选题核心服务 - Topic Service
V3 智能选题模块核心业务逻辑

功能:
1. generate_topics() - 批量生成选题 (多行业 + 多角度)
2. score_topic() - 5 维智能评分
3. compare_topics() - 选题对比
4. get_industries() - 获取行业列表
5. get_angles() - 获取角度列表

技术实现:
- 复用 core/article_scorer.py 评分逻辑
- 复用 core/deep_retriever.py 检索能力
- 整合热点中心 API
"""

import os
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.topic import (
    Topic, TopicScore, Industry, Angle, 
    TopicComparison, GenerateRequest
)


class TopicService:
    """
    智能选题服务
    
    核心功能:
    1. 批量生成选题 - 支持多行业、多角度组合
    2. 5 维智能评分 - 热度/潜力/匹配/新颖/可行
    3. 选题对比分析 - 多维度对比推荐
    4. 行业/角度管理 - 配置管理
    """
    
    def __init__(self):
        """初始化服务"""
        # 数据库连接
        self.db = self._init_database()
        
        # 初始化评分器
        self.scorer = self._init_scorer()
        
        # 初始化检索器
        self.retriever = self._init_retriever()
        
        # 预置行业 (如果数据库为空)
        self.default_industries = [
            {"name": "教育", "code": "education", "description": "K12 教育、高等教育、职业教育等"},
            {"name": "科技", "code": "technology", "description": "互联网、人工智能、数码科技等"},
            {"name": "财经", "code": "finance", "description": "金融、投资、理财、经济等"},
            {"name": "娱乐", "code": "entertainment", "description": "影视、音乐、明星、综艺等"},
            {"name": "体育", "code": "sports", "description": "体育赛事、运动员、健身等"},
            {"name": "健康", "code": "health", "description": "医疗健康、养生、心理等"},
            {"name": "职场", "code": "career", "description": "求职、职场技能、职业发展等"},
            {"name": "生活", "code": "lifestyle", "description": "生活方式、旅游、美食等"},
        ]
        
        # 预置角度
        self.default_angles = [
            {"name": "深度分析", "code": "deep_analysis", "description": "事件背后的原因/逻辑/本质", "icon": "🔍"},
            {"name": "数据解读", "code": "data_interpretation", "description": "用数据说话，图表可视化", "icon": "📊"},
            {"name": "观点评论", "code": "opinion_comment", "description": "独特视角/争议性观点", "icon": "💡"},
            {"name": "知识科普", "code": "knowledge_pop", "description": "专业知识普及，易懂有趣", "icon": "🎓"},
            {"name": "幽默调侃", "code": "humor_tease", "description": "轻松有趣，梗文化", "icon": "😂"},
            {"name": "风险警示", "code": "risk_warning", "description": "提醒/避坑/注意事项", "icon": "⚠️"},
            {"name": "趋势预测", "code": "trend_forecast", "description": "未来走向/发展趋势", "icon": "🚀"},
            {"name": "人物故事", "code": "human_story", "description": "以人为核心的故事叙述", "icon": "👥"},
        ]
        
        print("[TopicService] ✅ 服务初始化完成")
    
    def _init_database(self):
        """初始化数据库连接"""
        try:
            from core.hot_database_mysql import HotNewsDatabaseMySQL
            db = HotNewsDatabaseMySQL()
            print("[TopicService] ✅ 数据库连接成功")
            return db
        except Exception as e:
            print(f"[TopicService] ⚠️ 数据库连接失败：{e}")
            return None
    
    def _init_scorer(self):
        """初始化评分器"""
        try:
            from core.article_scorer import ArticleScorer
            scorer = ArticleScorer()
            print("[TopicService] ✅ 评分器初始化完成")
            return scorer
        except Exception as e:
            print(f"[TopicService] ⚠️ 评分器初始化失败：{e}")
            return None
    
    def _init_retriever(self):
        """初始化检索器"""
        try:
            from core.deep_retriever import DeepRetriever
            retriever = DeepRetriever()
            print("[TopicService] ✅ 检索器初始化完成")
            return retriever
        except Exception as e:
            print(f"[TopicService] ⚠️ 检索器初始化失败：{e}")
            return None
    
    # ============================================
    # 核心功能：生成选题
    # ============================================
    
    def generate_topics(
        self,
        industries: List[str],
        angles: List[str],
        hotnews_ids: Optional[List[str]] = None,
        count: int = 20,
        min_score: float = 60.0
    ) -> List[Topic]:
        """
        批量生成选题
        
        Args:
            industries: 行业列表 (如 ["教育", "科技"])
            angles: 角度列表 (如 ["深度分析", "数据解读"])
            hotnews_ids: 基于热点 ID 列表 (可选)
            count: 生成数量
            min_score: 最低评分要求
        
        Returns:
            选题列表
        """
        print(f"[TopicService] 开始生成选题：{len(industries)}行业 x {len(angles)}角度 = {count}个")
        
        topics = []
        
        # 1. 获取热点数据 (如果有指定热点 ID)
        hotnews_data = []
        if hotnews_ids:
            hotnews_data = self._fetch_hotnews(hotnews_ids)
            print(f"[TopicService] 获取到 {len(hotnews_data)} 条热点数据")
        
        # 2. 如果没有指定热点，从热点中心获取最新热点
        if not hotnews_data:
            hotnews_data = self._get_latest_hotnews(count * 2)
            print(f"[TopicService] 获取最新热点 {len(hotnews_data)} 条")
        
        # 3. 如果仍然没有热点数据，创建虚拟热点用于生成选题
        if not hotnews_data:
            print(f"[TopicService] ⚠️ 无热点数据，使用通用话题生成")
            hotnews_data = self._create_dummy_hotnews(count)
        
        # 3. 生成选题组合
        topic_combinations = self._generate_combinations(
            industries, angles, hotnews_data, count
        )
        
        # 4. 为每个选题评分
        for combo in topic_combinations:
            topic = self._create_topic(combo)
            
            # 评分
            score = self.score_topic(topic)
            topic.score = score
            topic.score_total = score.total
            topic.grade = score.grade
            
            # 过滤低分选题
            if score.total >= min_score:
                topics.append(topic)
        
        # 5. 按评分排序
        topics.sort(key=lambda t: t.score_total or 0, reverse=True)
        
        print(f"[TopicService] ✅ 生成 {len(topics)} 个选题 (评分>={min_score})")
        return topics
    
    def _fetch_hotnews(self, hotnews_ids: List[str]) -> List[Dict]:
        """获取热点数据"""
        if not self.db:
            return []
        
        results = []
        for hot_id in hotnews_ids:
            try:
                rows = self.db._fetch_all(
                    "SELECT * FROM hotnews WHERE id = %s",
                    (hot_id,)
                )
                if rows:
                    results.append(rows[0])
            except Exception as e:
                print(f"[TopicService] ⚠️ 获取热点 {hot_id} 失败：{e}")
        
        return results
    
    def _get_latest_hotnews(self, count: int) -> List[Dict]:
        """获取最新热点"""
        if not self.db:
            return []
        
        try:
            # 先尝试从 hotnews 表获取
            rows = self.db._fetch_all(
                """SELECT * FROM hotnews 
                   ORDER BY crawl_time DESC 
                   LIMIT %s""",
                (count,)
            )
            
            if rows:
                return rows
            
            # 如果没有热点数据，从 hot_topics 表获取 (兼容旧表)
            rows = self.db._fetch_all(
                """SELECT id, title, content, url as source_url, category, 
                           heat_score as heat_count, crawl_time, 
                           CONCAT('🔥', heat_score, '+') as heat_level
                   FROM hot_topics 
                   ORDER BY crawl_time DESC 
                   LIMIT %s""",
                (count,)
            )
            
            # 转换为标准格式
            result = []
            for row in rows:
                result.append({
                    "id": str(row.get("id", "")),
                    "title": row.get("title", "热点话题"),
                    "content": row.get("content"),
                    "source_url": row.get("source_url"),
                    "category": row.get("category"),
                    "heat_count": int(row.get("heat_count", 0)) if row.get("heat_count") else 0,
                    "heat_level": row.get("heat_level", "normal"),
                    "crawl_time": row.get("crawl_time")
                })
            
            return result
        except Exception as e:
            print(f"[TopicService] ⚠️ 获取最新热点失败：{e}")
            return []
    
    def _generate_combinations(
        self,
        industries: List[str],
        angles: List[str],
        hotnews_data: List[Dict],
        count: int
    ) -> List[Dict]:
        """
        生成选题组合
        
        Returns:
            选题组合列表，每个包含：industry, angle, hotnews
        """
        combinations = []
        
        # 计算每个行业需要生成的数量
        per_industry = max(1, count // len(industries))
        
        for industry in industries:
            industry_topics = []
            
            for angle in angles:
                # 为每个角度分配热点
                angle_count = max(1, per_industry // len(angles))
                
                for i in range(angle_count):
                    if i < len(hotnews_data):
                        hotnews = hotnews_data[i]
                        combinations.append({
                            "industry": industry,
                            "angle": angle,
                            "hotnews": hotnews,
                            "index": len(combinations)
                        })
        
        # 如果组合数不足，循环使用热点
        while len(combinations) < count and hotnews_data:
            for industry in industries:
                for angle in angles:
                    if len(combinations) >= count:
                        break
                    hotnews = hotnews_data[len(combinations) % len(hotnews_data)]
                    combinations.append({
                        "industry": industry,
                        "angle": angle,
                        "hotnews": hotnews,
                        "index": len(combinations)
                    })
                if len(combinations) >= count:
                    break
        
        return combinations[:count]
    
    def _create_topic(self, combo: Dict) -> Topic:
        """
        创建选题对象
        
        Args:
            combo: 选题组合 (industry, angle, hotnews)
        
        Returns:
            Topic 对象
        """
        industry = combo["industry"]
        angle = combo["angle"]
        hotnews = combo.get("hotnews", {})
        
        # 生成选题 ID
        topic_id = f"topic_{uuid.uuid4().hex[:12]}"
        
        # 生成标题
        title = self._generate_title(industry, angle, hotnews)
        
        # 生成描述
        description = self._generate_description(industry, angle, hotnews)
        
        # 提取核心要点
        key_points = self._extract_key_points(industry, angle, hotnews)
        
        # 来源热点 ID
        source_hotnews = [hotnews.get("id")] if hotnews.get("id") else None
        
        return Topic(
            id=topic_id,
            title=title,
            industry=industry,
            angle=angle,
            source_hotnews=source_hotnews,
            description=description,
            key_points=key_points,
            status="draft"
        )
    
    def _generate_title(self, industry: str, angle: str, hotnews: Dict) -> str:
        """生成选题标题"""
        if not hotnews:
            return f"{industry}领域：{angle}视角的深度探讨"
        
        hot_title = hotnews.get("title", "热点事件")
        
        # 根据角度生成不同风格的标题
        angle_templates = {
            "深度分析": f"{hot_title}：{industry}背后的深度逻辑",
            "数据解读": f"数据解读{industry}：{hot_title[:20]}的关键指标",
            "观点评论": f"{hot_title}：一个{industry}从业者的独特视角",
            "知识科普": f"{industry}科普：从{hot_title[:15]}说起",
            "幽默调侃": f"{hot_title}？{industry}人看了都笑了",
            "风险警示": f"{industry}提醒：{hot_title[:20]}背后的风险",
            "趋势预测": f"从{hot_title[:15]}看{industry}未来趋势",
            "人物故事": f"{industry}人的故事：{hot_title[:20]}",
        }
        
        return angle_templates.get(angle, f"{industry}：{hot_title}")
    
    def _generate_description(self, industry: str, angle: str, hotnews: Dict) -> str:
        """生成选题描述"""
        if not hotnews:
            return f"从{angle}角度探讨{industry}领域的热点话题"
        
        return f"基于热点事件，从{angle}角度深入分析{industry}领域的相关议题"
    
    def _create_dummy_hotnews(self, count: int) -> List[Dict]:
        """创建虚拟热点数据 (当数据库为空时)"""
        dummy_topics = [
            {"title": "人工智能赋能教育创新", "category": "教育"},
            {"title": "科技创新驱动未来发展", "category": "科技"},
            {"title": "职场技能提升指南", "category": "职场"},
            {"title": "健康生活方式探讨", "category": "健康"},
            {"title": "财经市场趋势分析", "category": "财经"},
            {"title": "体育赛事精彩回顾", "category": "体育"},
            {"title": "娱乐产业新动态", "category": "娱乐"},
            {"title": "生活品质提升技巧", "category": "生活"},
        ]
        
        result = []
        for i in range(count):
            topic = dummy_topics[i % len(dummy_topics)]
            result.append({
                "id": f"dummy_{i}",
                "title": topic["title"],
                "content": f"关于{topic['category']}领域的热门话题讨论",
                "category": topic["category"],
                "heat_count": 50000 + i * 1000,
                "heat_level": "🔥5 万+",
                "crawl_time": datetime.now()
            })
        
        return result
    
    def _extract_key_points(self, industry: str, angle: str, hotnews: Dict) -> List[str]:
        """提取核心要点"""
        # 标准要点模板
        templates = {
            "深度分析": [
                f"{industry}领域现状分析",
                "事件背后的原因探究",
                "对行业的影响评估",
                "未来发展趋势预测"
            ],
            "数据解读": [
                "关键数据指标展示",
                "数据背后的趋势分析",
                "与历史数据对比",
                "数据驱动的建议"
            ],
            "观点评论": [
                "事件核心矛盾点",
                "不同观点对比",
                "个人独特见解",
                "对行业的启示"
            ],
            "知识科普": [
                "基础概念解释",
                "相关背景知识",
                "实际应用场景",
                "常见问题解答"
            ],
            "幽默调侃": [
                "事件槽点盘点",
                "行业梗文化解读",
                "轻松有趣的对比",
                "调侃中的思考"
            ],
            "风险警示": [
                "潜在风险识别",
                "常见误区分析",
                "避坑指南",
                "正确做法建议"
            ],
            "趋势预测": [
                "当前发展趋势",
                "影响因素分析",
                "未来走向预测",
                "应对策略建议"
            ],
            "人物故事": [
                "核心人物介绍",
                "关键事件回顾",
                "人物影响分析",
                "故事启示总结"
            ],
        }
        
        return templates.get(angle, [
            f"{industry}领域概述",
            "核心议题分析",
            "关键要点总结",
            "未来展望"
        ])
    
    # ============================================
    # 核心功能：智能评分
    # ============================================
    
    def score_topic(self, topic: Topic) -> TopicScore:
        """
        5 维智能评分
        
        评分维度:
        - 热度分 (30%): 基于平台热度
        - 潜力分 (25%): 趋势预测
        - 匹配分 (20%): 与账号定位匹配度
        - 新颖分 (15%): 独特性/差异化
        - 可行分 (10%): 素材充足度
        
        Args:
            topic: 选题对象
        
        Returns:
            TopicScore 评分对象
        """
        print(f"[TopicService] 评分选题：{topic.title[:30]}...")
        
        # 1. 热度分 (30%)
        heat_score = self._score_heat(topic)
        
        # 2. 潜力分 (25%)
        potential_score = self._score_potential(topic)
        
        # 3. 匹配分 (20%)
        match_score = self._score_match(topic)
        
        # 4. 新颖分 (15%)
        novelty_score = self._score_novelty(topic)
        
        # 5. 可行分 (10%)
        feasibility_score = self._score_feasibility(topic)
        
        # 创建评分对象
        score = TopicScore(
            topic_id=topic.id,
            heat=heat_score,
            potential=potential_score,
            match=match_score,
            novelty=novelty_score,
            feasibility=feasibility_score
        )
        
        # 计算总分和等级
        score.update_total()
        
        print(f"[TopicService] 评分完成：总分={score.total:.1f}, 等级={score.grade}")
        return score
    
    def _score_heat(self, topic: Topic) -> float:
        """
        热度分 (30%)
        
        基于来源热点的热度数据
        """
        if not topic.source_hotnews or not self.db:
            return 60.0  # 基础分
        
        try:
            # 获取热点热度
            hot_id = topic.source_hotnews[0]
            rows = self.db._fetch_all(
                "SELECT heat_count, heat_level FROM hotnews WHERE id = %s",
                (hot_id,)
            )
            
            if rows:
                heat_count = rows[0].get("heat_count", 0)
                
                # 根据热度数值评分
                if heat_count >= 1000000:
                    return 95.0  # 🔥100 万+
                elif heat_count >= 500000:
                    return 85.0  # 🔥50 万+
                elif heat_count >= 100000:
                    return 75.0  # 🔥10 万+
                elif heat_count >= 50000:
                    return 65.0  # 🔥5 万+
                else:
                    return 55.0
        except Exception as e:
            print(f"[TopicService] ⚠️ 热度评分失败：{e}")
        
        return 60.0
    
    def _score_potential(self, topic: Topic) -> float:
        """
        潜力分 (25%)
        
        趋势预测：基于话题时效性和讨论度
        """
        score = 65.0  # 基础分
        
        # 时间因素：新热点潜力更高
        if topic.created_at:
            hours_old = (datetime.now() - topic.created_at).total_seconds() / 3600
            if hours_old < 6:
                score += 20.0
            elif hours_old < 24:
                score += 10.0
            elif hours_old < 72:
                score += 5.0
        
        # 角度因素：某些角度潜力更高
        potential_angles = ["趋势预测", "深度分析", "数据解读"]
        if topic.angle in potential_angles:
            score += 10.0
        
        return min(100.0, score)
    
    def _score_match(self, topic: Topic) -> float:
        """
        匹配分 (20%)
        
        与账号定位匹配度
        """
        # 默认匹配分 (后续可根据账号配置调整)
        # 教育、科技类话题通常匹配度较高
        high_match_industries = ["教育", "科技", "职场"]
        
        if topic.industry in high_match_industries:
            return 85.0
        
        return 70.0
    
    def _score_novelty(self, topic: Topic) -> float:
        """
        新颖分 (15%)
        
        独特性/差异化
        """
        score = 60.0  # 基础分
        
        # 角度新颖性
        novel_angles = ["幽默调侃", "观点评论", "人物故事"]
        if topic.angle in novel_angles:
            score += 20.0
        
        # 标题独特性检测
        if "？" in topic.title or "！" in topic.title:
            score += 10.0  # 有问句或感叹句，更有吸引力
        
        return min(100.0, score)
    
    def _score_feasibility(self, topic: Topic) -> float:
        """
        可行分 (10%)
        
        素材充足度
        """
        score = 70.0  # 基础分
        
        # 有热点来源加分
        if topic.source_hotnews:
            score += 15.0
        
        # 有关键要点加分
        if topic.key_points and len(topic.key_points) >= 3:
            score += 10.0
        
        # 有描述加分
        if topic.description:
            score += 5.0
        
        return min(100.0, score)
    
    # ============================================
    # 核心功能：选题对比
    # ============================================
    
    def compare_topics(self, topic_ids: List[str]) -> TopicComparison:
        """
        选题对比分析
        
        Args:
            topic_ids: 选题 ID 列表
        
        Returns:
            TopicComparison 对比结果
        """
        print(f"[TopicService] 对比 {len(topic_ids)} 个选题")
        
        # 1. 获取选题详情
        topics = []
        for topic_id in topic_ids:
            topic = self.get_topic_by_id(topic_id)
            if topic:
                topics.append(topic)
        
        if not topics:
            raise ValueError("未找到任何选题")
        
        # 2. 对比分析
        comparison = self._analyze_comparison(topics)
        
        # 3. 生成推荐
        recommendation = self._generate_recommendation(topics, comparison)
        
        return TopicComparison(
            topics=topics,
            comparison=comparison,
            recommendation=recommendation
        )
    
    def _analyze_comparison(self, topics: List[Topic]) -> Dict[str, Any]:
        """分析对比数据"""
        if not topics:
            return {}
        
        # 计算各项指标
        scores = [t.score_total or 0 for t in topics]
        heat_scores = [t.score.heat if t.score else 0 for t in topics]
        potential_scores = [t.score.potential if t.score else 0 for t in topics]
        
        # 找出最佳
        best_total_idx = scores.index(max(scores))
        best_heat_idx = heat_scores.index(max(heat_scores))
        best_potential_idx = potential_scores.index(max(potential_scores))
        
        return {
            "count": len(topics),
            "avg_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "min_score": min(scores),
            "best_total": topics[best_total_idx].id,
            "best_heat": topics[best_heat_idx].id,
            "best_potential": topics[best_potential_idx].id,
            "industry_distribution": dict(Counter(t.industry for t in topics)),
            "angle_distribution": dict(Counter(t.angle for t in topics)),
        }
    
    def _generate_recommendation(
        self, 
        topics: List[Topic], 
        comparison: Dict[str, Any]
    ) -> str:
        """生成推荐建议"""
        if not topics:
            return "无选题可推荐"
        
        # 找到最佳选题
        best_topic = max(topics, key=lambda t: t.score_total or 0)
        
        reasons = []
        if best_topic.score:
            if best_topic.score.heat >= 80:
                reasons.append("热度高")
            if best_topic.score.potential >= 80:
                reasons.append("潜力大")
            if best_topic.score.match >= 80:
                reasons.append("匹配度好")
        
        reason_str = "、".join(reasons) if reasons else "综合评分最高"
        
        return f"推荐《{best_topic.title}》，{reason_str}，总分{best_topic.score_total:.1f}"
    
    # ============================================
    # 核心功能：获取行业/角度列表
    # ============================================
    
    def get_industries(self) -> List[Industry]:
        """获取行业列表"""
        if not self.db:
            # 返回预置行业
            return [
                Industry(
                    name=item["name"],
                    code=item["code"],
                    description=item.get("description")
                )
                for item in self.default_industries
            ]
        
        try:
            rows = self.db._fetch_all(
                "SELECT * FROM topic_industries WHERE enabled = TRUE ORDER BY id"
            )
            
            if rows:
                return [Industry.from_database_row(row) for row in rows]
        except Exception as e:
            print(f"[TopicService] ⚠️ 获取行业列表失败：{e}")
        
        # 返回预置行业
        return [
            Industry(
                name=item["name"],
                code=item["code"],
                description=item.get("description")
            )
            for item in self.default_industries
        ]
    
    def get_angles(self) -> List[Angle]:
        """获取角度列表"""
        if not self.db:
            # 返回预置角度
            return [
                Angle(
                    name=item["name"],
                    code=item["code"],
                    description=item.get("description"),
                    icon=item.get("icon")
                )
                for item in self.default_angles
            ]
        
        try:
            rows = self.db._fetch_all(
                "SELECT * FROM topic_angles WHERE enabled = TRUE ORDER BY id"
            )
            
            if rows:
                return [Angle.from_database_row(row) for row in rows]
        except Exception as e:
            print(f"[TopicService] ⚠️ 获取角度列表失败：{e}")
        
        # 返回预置角度
        return [
            Angle(
                name=item["name"],
                code=item["code"],
                description=item.get("description"),
                icon=item.get("icon")
            )
            for item in self.default_angles
        ]
    
    # ============================================
    # 辅助方法
    # ============================================
    
    def get_topic_by_id(self, topic_id: str) -> Optional[Topic]:
        """根据 ID 获取选题"""
        if not self.db:
            return None
        
        try:
            # 获取选题主表数据
            topic_rows = self.db._fetch_all(
                "SELECT * FROM topics WHERE id = %s",
                (topic_id,)
            )
            
            if not topic_rows:
                return None
            
            # 获取评分数据
            score_rows = self.db._fetch_all(
                "SELECT * FROM topic_scores WHERE topic_id = %s ORDER BY scored_at DESC LIMIT 1",
                (topic_id,)
            )
            
            score_row = score_rows[0] if score_rows else None
            
            return Topic.from_database_row(topic_rows[0], score_row)
        except Exception as e:
            print(f"[TopicService] ⚠️ 获取选题失败：{e}")
            return None
    
    def save_topic(self, topic: Topic) -> bool:
        """保存选题到数据库"""
        if not self.db:
            return False
        
        try:
            # 保存选题主表
            self.db._execute(
                """INSERT INTO topics 
                   (id, title, industry, angle, source_hotnews, description, 
                    key_points, score_total, grade, status, extra_data)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                   title=VALUES(title), industry=VALUES(industry), angle=VALUES(angle),
                   source_hotnews=VALUES(source_hotnews), description=VALUES(description),
                   key_points=VALUES(key_points), score_total=VALUES(score_total),
                   grade=VALUES(grade), status=VALUES(status), extra_data=VALUES(extra_data)""",
                (
                    topic.id, topic.title, topic.industry, topic.angle,
                    json.dumps(topic.source_hotnews) if topic.source_hotnews else None,
                    topic.description,
                    json.dumps(topic.key_points) if topic.key_points else None,
                    topic.score_total, topic.grade, topic.status,
                    json.dumps(topic.extra_data) if topic.extra_data else None
                )
            )
            
            # 保存评分 (注意：match 是 MySQL 保留字，需要加反引号)
            if topic.score:
                self.db._execute(
                    """INSERT INTO topic_scores 
                       (topic_id, heat, potential, `match`, novelty, feasibility, 
                        total, grade, details)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        topic.id, topic.score.heat, topic.score.potential,
                        topic.score.match, topic.score.novelty, topic.score.feasibility,
                        topic.score.total, topic.score.grade,
                        json.dumps(topic.score.details) if topic.score.details else None
                    )
                )
            
            print(f"[TopicService] ✅ 保存选题：{topic.id}")
            return True
        except Exception as e:
            print(f"[TopicService] ❌ 保存选题失败：{e}")
            return False
    
    def get_topics(
        self,
        status: Optional[str] = None,
        industry: Optional[str] = None,
        min_score: float = 0,
        page: int = 1,
        page_size: int = 20
    ) -> List[Topic]:
        """
        获取选题列表 (API 兼容方法)
        
        Args:
            status: 状态筛选
            industry: 行业筛选
            min_score: 最低分数
            page: 页码
            page_size: 每页数量
        
        Returns:
            选题列表
        """
        topics, _ = self.get_topic_list(
            status=status,
            industry=industry,
            min_score=min_score if min_score > 0 else None,
            page=page,
            page_size=page_size
        )
        return topics
    
    def get_topic_list(
        self,
        industry: Optional[str] = None,
        angle: Optional[str] = None,
        status: Optional[str] = None,
        min_score: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Topic], int]:
        """
        获取选题列表
        
        Returns:
            (选题列表，总数)
        """
        if not self.db:
            return [], 0
        
        try:
            # 构建查询条件
            conditions = ["1=1"]
            params = []
            
            if industry:
                conditions.append("industry = %s")
                params.append(industry)
            
            if angle:
                conditions.append("angle = %s")
                params.append(angle)
            
            if status:
                conditions.append("status = %s")
                params.append(status)
            
            if min_score is not None:
                conditions.append("score_total >= %s")
                params.append(min_score)
            
            where_clause = " AND ".join(conditions)
            
            # 查询总数
            count_sql = f"SELECT COUNT(*) as cnt FROM topics WHERE {where_clause}"
            count_result = self.db._fetch_one(count_sql, tuple(params))
            total = count_result["cnt"] if count_result else 0
            
            # 查询数据
            offset = (page - 1) * page_size
            data_sql = f"""
                SELECT t.*, s.total as score_total, s.grade, s.heat, s.potential, 
                       s.`match`, s.novelty, s.feasibility
                FROM topics t
                LEFT JOIN topic_scores s ON t.id = s.topic_id
                WHERE {where_clause}
                ORDER BY t.created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])
            rows = self.db._fetch_all(data_sql, tuple(params))
            
            # 转换为 Topic 对象
            topics = []
            for row in rows:
                score_data = {
                    "topic_id": row["id"],
                    "heat": float(row["heat"]) if row.get("heat") else 0,
                    "potential": float(row["potential"]) if row.get("potential") else 0,
                    "match": float(row["match"]) if row.get("match") else 0,
                    "novelty": float(row["novelty"]) if row.get("novelty") else 0,
                    "feasibility": float(row["feasibility"]) if row.get("feasibility") else 0,
                    "total": float(row["score_total"]) if row.get("score_total") else 0,
                    "grade": row.get("grade", "C")
                }
                score = TopicScore(**score_data)
                
                topic = Topic.from_database_row(row)
                topic.score = score
                topic.score_total = score.total
                topic.grade = score.grade
                
                topics.append(topic)
            
            return topics, total
        except Exception as e:
            print(f"[TopicService] ⚠️ 获取选题列表失败：{e}")
            return [], 0


def test_topic_service():
    """测试 TopicService"""
    print("\n" + "="*70)
    print("🎯 智能选题服务测试")
    print("="*70 + "\n")
    
    service = TopicService()
    
    # 测试 1: 获取行业列表
    print("\n" + "="*70)
    print("测试 1: 获取行业列表")
    print("="*70)
    industries = service.get_industries()
    print(f"行业数量：{len(industries)}")
    for ind in industries[:3]:
        print(f"  - {ind.name} ({ind.code})")
    
    # 测试 2: 获取角度列表
    print("\n" + "="*70)
    print("测试 2: 获取角度列表")
    print("="*70)
    angles = service.get_angles()
    print(f"角度数量：{len(angles)}")
    for angle in angles[:3]:
        print(f"  - {angle.name} ({angle.icon})")
    
    # 测试 3: 生成选题
    print("\n" + "="*70)
    print("测试 3: 生成选题")
    print("="*70)
    topics = service.generate_topics(
        industries=["教育", "科技"],
        angles=["深度分析", "数据解读"],
        count=5,
        min_score=60.0
    )
    print(f"生成选题数：{len(topics)}")
    for topic in topics[:3]:
        print(f"\n  标题：{topic.title}")
        print(f"  行业：{topic.industry} | 角度：{topic.angle}")
        if topic.score:
            print(f"  评分：{topic.score_total:.1f} ({topic.grade})")
            print(f"  维度：热度={topic.score.heat:.0f}, 潜力={topic.score.potential:.0f}, "
                  f"匹配={topic.score.match:.0f}, 新颖={topic.score.novelty:.0f}, "
                  f"可行={topic.score.feasibility:.0f}")
    
    # 测试 4: 评分选题
    print("\n" + "="*70)
    print("测试 4: 评分选题")
    print("="*70)
    if topics:
        topic = topics[0]
        score = service.score_topic(topic)
        print(f"选题：{topic.title[:30]}...")
        print(f"总分：{score.total:.1f} ({score.grade})")
        print(f"5 维评分:")
        print(f"  热度分 (30%): {score.heat:.1f}")
        print(f"  潜力分 (25%): {score.potential:.1f}")
        print(f"  匹配分 (20%): {score.match:.1f}")
        print(f"  新颖分 (15%): {score.novelty:.1f}")
        print(f"  可行分 (10%): {score.feasibility:.1f}")
    
    print("\n" + "="*70)
    print("🎉 测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_topic_service()


# 方法别名 (兼容旧调用)
def get_topics(self, limit: int = 50, offset: int = 0) -> List[Dict]:
    """获取选题列表 (get_topic_list 的别名)"""
    return self.get_topic_list(limit, offset)
