#!/usr/bin/env python3
"""
热点中心核心服务 - HotNews Service
V3 热点中心模块核心业务逻辑

提供以下功能:
- get_hotlist(): 获取热点列表 (支持多维度筛选)
- get_trend(): 获取热度趋势
- subscribe(): 订阅热点
- search(): 搜索热点

数据库：MySQL (youmind 数据库)
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("⚠️  pymysql 未安装，请运行：pip install pymysql")

from models.hotnews import HotNews, Subscription, TrendData, PaginatedResponse


class HotNewsService:
    """
    热点中心核心服务类
    
    提供热点数据的查询、筛选、订阅、搜索等功能
    """
    
    # 数据库配置
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', '43.134.234.4'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME', 'youmind'),
        'user': os.getenv('DB_USER', 'youmind'),
        'password': os.getenv('DB_PASSWORD', 'YouMind2026'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    def __init__(self):
        """初始化服务，建立数据库连接"""
        if not MYSQL_AVAILABLE:
            raise ImportError("pymysql 未安装，无法初始化 HotNewsService")
        
        self.conn = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            self.conn = pymysql.connect(**self.DB_CONFIG)
            print(f"[HotNewsService] ✅ 数据库连接成功")
        except Exception as e:
            print(f"[HotNewsService] ❌ 数据库连接失败：{e}")
            raise
    
    def _execute(self, query: str, params: tuple = None) -> List[Dict]:
        """
        执行 SQL 查询
        
        Args:
            query: SQL 查询语句
            params: 查询参数
        
        Returns:
            查询结果列表
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Exception as e:
            print(f"[HotNewsService] ❌ SQL 错误：{e}")
            raise
        finally:
            cursor.close()
    
    def _execute_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """执行 SQL 查询并返回单条结果"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def _execute_write(self, query: str, params: tuple = None) -> int:
        """
        执行写操作 (INSERT/UPDATE/DELETE)
        
        Returns:
            受影响的行数
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            print(f"[HotNewsService] ❌ 写操作失败：{e}")
            raise
        finally:
            cursor.close()
    
    # ============================================
    # 核心功能：获取热点列表
    # ============================================
    
    def get_hotlist(
        self,
        platform: Optional[str] = None,
        category: Optional[str] = None,
        time_range: str = "24h",
        min_heat: int = 0,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> PaginatedResponse:
        """
        获取热点列表 (支持多维度筛选)
        
        Args:
            platform: 平台筛选 (微博/知乎/B 站等)
            category: 分类筛选 (科技/教育/财经等)
            time_range: 时间范围 (1h/6h/24h/7d)
            min_heat: 最低热度值
            keyword: 关键词搜索
            page: 页码 (从 1 开始)
            page_size: 每页数量
        
        Returns:
            PaginatedResponse: 分页响应对象
        """
        # 时间范围转换
        time_map = {
            "1h": 1,
            "6h": 6,
            "24h": 24,
            "7d": 24 * 7
        }
        hours = time_map.get(time_range, 24)
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        # 构建查询条件
        conditions = ["crawl_time >= %s", "heat_count >= %s"]
        params = [time_threshold, min_heat]
        
        if platform:
            conditions.append("platform = %s")
            params.append(platform)
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        if keyword:
            conditions.append("(title LIKE %s OR content LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        where_clause = " AND ".join(conditions)
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM hotnews WHERE {where_clause}"
        count_result = self._execute_one(count_sql, params)
        total = count_result['total'] if count_result else 0
        
        # 查询数据
        offset = (page - 1) * page_size
        query = f"""
            SELECT * FROM hotnews 
            WHERE {where_clause}
            ORDER BY heat_count DESC, crawl_time DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])
        
        rows = self._execute(query, params)
        items = [HotNews.from_database_row(row) for row in rows]
        
        return PaginatedResponse.create(items, total, page, page_size)
    
    # ============================================
    # 核心功能：获取热度趋势
    # ============================================
    
    def get_trend(self, item_id: str, hours: int = 24) -> Optional[TrendData]:
        """
        获取热点的热度趋势
        
        Args:
            item_id: 热点 ID
            hours: 时间范围 (小时)
        
        Returns:
            TrendData: 趋势数据，如果不存在返回 None
        """
        # 查询热点
        query = "SELECT * FROM hotnews WHERE id = %s"
        row = self._execute_one(query, (item_id,))
        
        if not row:
            return None
        
        # 如果有存储的趋势数据，直接返回
        if row.get('trend_data'):
            trend_data = row['trend_data']
            if isinstance(trend_data, str):
                trend_data = json.loads(trend_data)
            return TrendData(item_id=item_id, trend=trend_data)
        
        # 如果没有存储趋势数据，返回当前热度作为单点趋势
        crawl_time = row.get('crawl_time', datetime.now())
        heat_count = row.get('heat_count', 0)
        
        return TrendData(
            item_id=item_id,
            trend=[{
                "time": crawl_time.isoformat() if isinstance(crawl_time, datetime) else str(crawl_time),
                "heat": heat_count
            }]
        )
    
    # ============================================
    # 核心功能：订阅热点
    # ============================================
    
    def subscribe(
        self,
        keyword: str,
        user_id: str,
        platform: Optional[str] = None,
        category: Optional[str] = None,
        notify_enabled: bool = True
    ) -> Subscription:
        """
        订阅热点
        
        Args:
            keyword: 订阅关键词
            user_id: 用户 ID
            platform: 订阅平台 (可选)
            category: 订阅分类 (可选)
            notify_enabled: 是否启用通知
        
        Returns:
            Subscription: 创建的订阅对象
        """
        query = """
            INSERT INTO hotnews_subscriptions 
            (user_id, keyword, platform, category, notify_enabled, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
        
        self._execute_write(query, (user_id, keyword, platform, category, notify_enabled))
        
        # 查询刚插入的记录
        subscription = self.get_subscription_by_keyword(user_id, keyword)
        
        if not subscription:
            raise Exception("订阅创建成功但无法查询到记录")
        
        return subscription
    
    def get_subscription_by_keyword(self, user_id: str, keyword: str) -> Optional[Subscription]:
        """根据关键词查询订阅"""
        query = """
            SELECT * FROM hotnews_subscriptions 
            WHERE user_id = %s AND keyword = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        row = self._execute_one(query, (user_id, keyword))
        
        if not row:
            return None
        
        return Subscription.from_database_row(row)
    
    def get_subscriptions(self, user_id: str) -> List[Subscription]:
        """
        获取用户的所有订阅
        
        Args:
            user_id: 用户 ID
        
        Returns:
            订阅列表
        """
        query = """
            SELECT * FROM hotnews_subscriptions 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        rows = self._execute(query, (user_id,))
        return [Subscription.from_database_row(row) for row in rows]
    
    def unsubscribe(self, user_id: str, keyword: str) -> bool:
        """
        取消订阅
        
        Args:
            user_id: 用户 ID
            keyword: 订阅关键词
        
        Returns:
            是否成功取消
        """
        query = """
            DELETE FROM hotnews_subscriptions 
            WHERE user_id = %s AND keyword = %s
        """
        rows_affected = self._execute_write(query, (user_id, keyword))
        return rows_affected > 0
    
    # ============================================
    # 核心功能：搜索热点
    # ============================================
    
    def search(
        self,
        query: str,
        platform: Optional[str] = None,
        category: Optional[str] = None,
        time_range: str = "24h",
        limit: int = 50
    ) -> List[HotNews]:
        """
        搜索热点 (全文检索)
        
        Args:
            query: 搜索关键词
            platform: 平台筛选
            category: 分类筛选
            time_range: 时间范围
            limit: 返回数量限制
        
        Returns:
            热点列表
        """
        # 时间范围转换
        time_map = {"1h": 1, "6h": 6, "24h": 24, "7d": 24 * 7}
        hours = time_map.get(time_range, 24)
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        # 构建查询条件
        conditions = ["crawl_time >= %s", "(title LIKE %s OR content LIKE %s)"]
        params = [time_threshold, f"%{query}%", f"%{query}%"]
        
        if platform:
            conditions.append("platform = %s")
            params.append(platform)
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        where_clause = " AND ".join(conditions)
        
        sql = f"""
            SELECT * FROM hotnews 
            WHERE {where_clause}
            ORDER BY heat_count DESC
            LIMIT %s
        """
        params.append(limit)
        
        rows = self._execute(sql, tuple(params))
        return [HotNews.from_database_row(row) for row in rows]
    
    # ============================================
    # 辅助功能：获取单个热点详情
    # ============================================
    
    def get_by_id(self, item_id: str) -> Optional[HotNews]:
        """
        根据 ID 获取热点详情
        
        Args:
            item_id: 热点 ID
        
        Returns:
            HotNews 对象，不存在返回 None
        """
        query = "SELECT * FROM hotnews WHERE id = %s"
        row = self._execute_one(query, (item_id,))
        
        if not row:
            return None
        
        return HotNews.from_database_row(row)
    
    # ============================================
    # 辅助功能：获取统计信息
    # ============================================
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            days: 统计天数
        
        Returns:
            统计数据字典
        """
        time_threshold = datetime.now() - timedelta(days=days)
        
        # 总数统计
        count_query = """
            SELECT COUNT(*) as total, AVG(heat_count) as avg_heat, MAX(heat_count) as max_heat
            FROM hotnews
            WHERE crawl_time >= %s
        """
        count_result = self._execute_one(count_query, (time_threshold,))
        
        # 平台分布
        platform_query = """
            SELECT platform, COUNT(*) as count
            FROM hotnews
            WHERE crawl_time >= %s
            GROUP BY platform
            ORDER BY count DESC
        """
        platform_result = self._execute(platform_query, (time_threshold,))
        
        # 分类分布
        category_query = """
            SELECT category, COUNT(*) as count
            FROM hotnews
            WHERE crawl_time >= %s
            GROUP BY category
            ORDER BY count DESC
        """
        category_result = self._execute(category_query, (time_threshold,))
        
        return {
            "total": count_result['total'] if count_result else 0,
            "avg_heat": float(count_result['avg_heat']) if count_result and count_result['avg_heat'] else 0,
            "max_heat": count_result['max_heat'] if count_result else 0,
            "by_platform": platform_result,
            "by_category": category_result,
            "period_days": days
        }
    
    # ============================================
    # 资源清理
    # ============================================
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("[HotNewsService] ✅ 数据库连接已关闭")
    
    def __del__(self):
        """析构函数，确保资源释放"""
        self.close()


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    # 简单测试
    print("🔍 测试 HotNewsService...")
    
    try:
        service = HotNewsService()
        
        # 测试获取热点列表
        print("\n📋 测试 get_hotlist()...")
        result = service.get_hotlist(page=1, page_size=5)
        print(f"✅ 获取到 {result.total} 条热点，当前页 {result.page}/{result.total_pages}")
        
        # 测试搜索
        print("\n🔍 测试 search()...")
        results = service.search("AI", limit=5)
        print(f"✅ 搜索到 {len(results)} 条结果")
        
        # 测试统计
        print("\n📊 测试 get_statistics()...")
        stats = service.get_statistics(days=7)
        print(f"✅ 7 天内热点总数：{stats['total']}")
        
        service.close()
        print("\n✅ 所有测试通过!")
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
