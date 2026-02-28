#!/usr/bin/env python3
"""
V3 热点中心模块测试用例
测试范围:
- 数据模型 (HotNews, Subscription)
- 核心服务 (HotNewsService)
- API 路由 (FastAPI)

运行方式:
    python -m pytest tests/test_hotnews_v3.py -v
    或
    python tests/test_hotnews_v3.py
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import List

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 尝试导入 pytest
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    print("⚠️  pytest 未安装，使用内置测试运行器")

from models.hotnews import HotNews, Subscription, TrendData, PaginatedResponse, CREATE_TABLE_SQL
from core.hotnews_service import HotNewsService


# ============================================
# 数据模型测试
# ============================================

class TestHotNewsModel:
    """测试 HotNews 数据模型"""
    
    def test_create_hotnews_basic(self):
        """测试创建基础热点对象"""
        hotnews = HotNews(
            id="test_001",
            title="测试热点新闻",
            platform="微博",
            category="科技",
            heat_count=1500000
        )
        
        assert hotnews.id == "test_001"
        assert hotnews.title == "测试热点新闻"
        assert hotnews.platform == "微博"
        assert hotnews.category == "科技"
        assert hotnews.heat_count == 1500000
        print("✅ test_create_hotnews_basic 通过")
    
    def test_heat_level_auto_calculate(self):
        """测试热度等级自动计算"""
        # 100 万+
        hotnews1 = HotNews(id="t1", title="t1", heat_count=1500000)
        assert "100 万" in hotnews1.heat_level
        
        # 50 万+
        hotnews2 = HotNews(id="t2", title="t2", heat_count=600000)
        assert "50 万" in hotnews2.heat_level
        
        # 10 万+
        hotnews3 = HotNews(id="t3", title="t3", heat_count=200000)
        assert "10 万" in hotnews3.heat_level
        
        # 正常
        hotnews4 = HotNews(id="t4", title="t4", heat_count=5000)
        assert hotnews4.heat_level == "normal"
        
        print("✅ test_heat_level_auto_calculate 通过")
    
    def test_to_dict_and_json(self):
        """测试序列化和反序列化"""
        hotnews = HotNews(
            id="test_json",
            title="测试 JSON 序列化",
            platform="知乎",
            heat_count=100000
        )
        
        # 测试 to_dict
        data = hotnews.to_dict()
        assert isinstance(data, dict)
        assert data['id'] == "test_json"
        assert data['title'] == "测试 JSON 序列化"
        
        # 测试 to_json
        json_str = hotnews.to_json()
        assert isinstance(json_str, str)
        assert "测试 JSON 序列化" in json_str
        
        print("✅ test_to_dict_and_json 通过")
    
    def test_from_database_row(self):
        """测试从数据库行创建模型"""
        row = {
            'id': 'db_001',
            'title': '数据库测试',
            'content': '内容',
            'platform': 'B 站',
            'category': '科技',
            'heat_count': 500000,
            'heat_level': '🔥50 万+',
            'source_url': 'https://bilibili.com',
            'crawl_time': datetime.now(),
            'trend_data': [{"time": "2026-03-01", "heat": 1000}],  # 已经是列表
            'extra_data': None
        }
        
        hotnews = HotNews.from_database_row(row)
        
        assert hotnews.id == 'db_001'
        assert hotnews.title == '数据库测试'
        assert hotnews.platform == 'B 站'
        assert hotnews.heat_count == 500000
        assert hotnews.trend_data is not None
        
        print("✅ test_from_database_row 通过")


class TestSubscriptionModel:
    """测试 Subscription 数据模型"""
    
    def test_create_subscription(self):
        """测试创建订阅对象"""
        sub = Subscription(
            user_id="user_001",
            keyword="人工智能",
            platform="知乎",
            category="科技"
        )
        
        assert sub.user_id == "user_001"
        assert sub.keyword == "人工智能"
        assert sub.platform == "知乎"
        assert sub.category == "科技"
        assert sub.notify_enabled == True
        
        print("✅ test_create_subscription 通过")
    
    def test_subscription_optional_fields(self):
        """测试订阅可选字段"""
        sub = Subscription(
            user_id="user_002",
            keyword="教育"
            # platform 和 category 可选
        )
        
        assert sub.user_id == "user_002"
        assert sub.keyword == "教育"
        assert sub.platform is None
        assert sub.category is None
        
        print("✅ test_subscription_optional_fields 通过")


class TestPaginatedResponse:
    """测试分页响应模型"""
    
    def test_create_paginated_response(self):
        """测试创建分页响应"""
        items = [
            HotNews(id=f"t{i}", title=f"标题{i}", heat_count=1000*i)
            for i in range(1, 6)
        ]
        
        response = PaginatedResponse.create(
            items=items,
            total=58,
            page=2,
            page_size=5
        )
        
        assert response.data == items
        assert response.total == 58
        assert response.page == 2
        assert response.page_size == 5
        assert response.total_pages == 12  # ceil(58/5)
        
        print("✅ test_create_paginated_response 通过")


# ============================================
# 核心服务测试
# ============================================

class TestHotNewsService:
    """测试 HotNewsService 核心服务"""
    
    def test_get_hotlist_basic(self):
        """测试获取热点列表 (基础)"""
        service = HotNewsService()
        try:
        
            result = service.get_hotlist(page=1, page_size=10)
            
            assert isinstance(result, PaginatedResponse)
            assert result.page == 1
            assert result.page_size == 10
            assert result.total >= 0
            assert isinstance(result.data, list)
            
            print(f"✅ test_get_hotlist_basic 通过 (共 {result.total} 条)")
        finally:
            service.close()
    
    def test_get_hotlist_with_filters(self):
        """测试获取热点列表 (带筛选)"""
        service = HotNewsService()
        try:
        
            # 按平台筛选
            result = service.get_hotlist(platform="微博", page=1, page_size=5)
            assert isinstance(result, PaginatedResponse)
            
            # 按分类筛选
            result = service.get_hotlist(category="科技", page=1, page_size=5)
            assert isinstance(result, PaginatedResponse)
            
            # 按时间范围筛选
            result = service.get_hotlist(time_range="24h", page=1, page_size=5)
            assert isinstance(result, PaginatedResponse)
            
            print("✅ test_get_hotlist_with_filters 通过")
        finally:
            service.close()
    
    def test_search_basic(self):
        """测试搜索功能"""
        service = HotNewsService()
        try:
        
            results = service.search(query="AI", limit=10)
            
            assert isinstance(results, list)
            assert len(results) <= 10
            
            print(f"✅ test_search_basic 通过 (找到 {len(results)} 条)")
        finally:
            service.close()
    
    def test_get_statistics(self):
        """测试统计功能"""
        service = HotNewsService()
        try:
        
            stats = service.get_statistics(days=7)
            
            assert isinstance(stats, dict)
            assert 'total' in stats
            assert 'by_platform' in stats
            assert 'by_category' in stats
            
            print(f"✅ test_get_statistics 通过 (7 天热点：{stats['total']}条)")
        finally:
            service.close()
    
    def test_subscribe_and_unsubscribe(self):
        """测试订阅和取消订阅"""
        service = HotNewsService()
        try:
        
            user_id = "test_user_001"
            keyword = f"测试关键词_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 测试订阅
            subscription = service.subscribe(
                keyword=keyword,
                user_id=user_id,
                category="科技"
            )
            
            assert isinstance(subscription, Subscription)
            assert subscription.keyword == keyword
            assert subscription.user_id == user_id
            
            print(f"✅ 订阅成功：{keyword}")
            
            # 测试获取订阅列表
            subscriptions = service.get_subscriptions(user_id)
            assert isinstance(subscriptions, list)
            assert len(subscriptions) >= 1
            
            print(f"✅ 获取订阅列表成功 (共 {len(subscriptions)} 条)")
            
            # 测试取消订阅
            success = service.unsubscribe(user_id, keyword)
            assert success == True
            
            print(f"✅ 取消订阅成功：{keyword}")
        finally:
            service.close()
    
    def test_get_by_id(self):
        """测试根据 ID 获取热点"""
        service = HotNewsService()
        try:
        
            # 先获取一个热点
            result = service.get_hotlist(page=1, page_size=1)
            
            if result.data and len(result.data) > 0:
                hotnews_id = result.data[0].id
                hotnews = service.get_by_id(hotnews_id)
                
                assert hotnews is not None
                assert hotnews.id == hotnews_id
                
                print(f"✅ test_get_by_id 通过 (ID: {hotnews_id})")
            else:
                print("⚠️  无热点数据，跳过测试")
        finally:
            service.close()


# ============================================
# 集成测试
# ============================================

class TestIntegration:
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        print("\n🔄 测试完整工作流...")
        
        # 1. 创建服务
        service = HotNewsService()
        print("   ✅ 1. 服务初始化")
        
        # 2. 获取热点列表
        result = service.get_hotlist(page=1, page_size=5)
        print(f"   ✅ 2. 获取热点列表 ({result.total}条)")
        
        # 3. 搜索热点
        results = service.search(query="技术", limit=5)
        print(f"   ✅ 3. 搜索热点 ({len(results)}条)")
        
        # 4. 获取统计
        stats = service.get_statistics(days=7)
        print(f"   ✅ 4. 获取统计 (总数：{stats['total']})")
        
        # 5. 订阅
        keyword = f"集成测试_{datetime.now().strftime('%Y%m%d')}"
        subscription = service.subscribe(keyword=keyword, user_id="test_user")
        print(f"   ✅ 5. 订阅关键词 ({subscription.keyword})")
        
        # 6. 取消订阅
        service.unsubscribe("test_user", keyword)
        print(f"   ✅ 6. 取消订阅")
        
        # 7. 清理
        service.close()
        print("   ✅ 7. 服务关闭")
        
        print("\n✅ 完整工作流测试通过!")


# ============================================
# 测试运行器
# ============================================

def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 V3 热点中心模块测试")
    print("=" * 60)
    
    tests = [
        # 数据模型测试
        TestHotNewsModel(),
        TestSubscriptionModel(),
        TestPaginatedResponse(),
        # 核心服务测试
        TestHotNewsService(),
        # 集成测试
        TestIntegration()
    ]
    
    passed = 0
    failed = 0
    
    for test_obj in tests:
        print(f"\n{'='*60}")
        print(f"📋 运行测试类：{test_obj.__class__.__name__}")
        print('=' * 60)
        
        for method_name in dir(test_obj):
            if method_name.startswith('test_'):
                try:
                    method = getattr(test_obj, method_name)
                    method()
                    passed += 1
                except Exception as e:
                    print(f"❌ {method_name} 失败：{e}")
                    import traceback
                    traceback.print_exc()
                    failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果：{passed} 通过，{failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
