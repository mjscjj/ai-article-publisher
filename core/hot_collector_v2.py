#!/usr/bin/env python3
"""
【热点采集器 V2】Hot News Collector V2
基于新数据库架构重构的热点采集模块

复用已有能力:
1. DailyHotApi 采集器 (sources/dailyhot_collector.py)
2. RSSHub 采集器 (sources/extended_collectors_v2.py)
3. 视频采集器 (sources/video_collector.py)
4. 内容采集器 (sources/content_collector.py)
5. 垂直领域采集器 (sources/vertical_collector.py)

新增功能:
1. 数据库存储 (hot_database.py)
2. 智能去重 (基于关键词哈希)
3. 热度计算 (多维权重评分)
4. 自动分类 (基于来源和关键词)
5. 统计分析 (多维度报表)
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'sources'))

# 导入数据库
from core.hot_database import HotNewsDatabase

# 导入已有采集器
try:
    from sources.dailyhot_collector import collect_all_platforms as collect_dailyhot
    DAILYHOT_AVAILABLE = True
except ImportError:
    DAILYHOT_AVAILABLE = False
    print("⚠️  DailyHotApi 采集器不可用")

try:
    from sources.extended_collectors_v2 import collect_all_sources as collect_rsshub
    RSSHUB_AVAILABLE = True
except ImportError:
    RSSHUB_AVAILABLE = False
    print("⚠️  RSSHub 采集器不可用")

try:
    from sources.video_collector import collect_all_platforms as collect_videos
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False
    print("⚠️  视频采集器不可用")


class HotNewsCollectorV2:
    """热点采集器 V2"""
    
    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: 数据库路径 (可选)
        """
        self.db = HotNewsDatabase(db_path)
        self.stats = {
            'total_collected': 0,
            'total_stored': 0,
            'duplicates': 0,
            'errors': 0
        }
        
        # 初始化数据源
        self._init_sources()
    
    def _init_sources(self):
        """初始化数据源配置"""
        sources = [
            # DailyHotApi 来源
            {"name": "微博热搜", "platform": "微博", "category": "综合", "priority": 10, "credibility": 0.8},
            {"name": "知乎热榜", "platform": "知乎", "category": "综合", "priority": 9, "credibility": 0.85},
            {"name": "百度热榜", "platform": "百度", "category": "综合", "priority": 8, "credibility": 0.7},
            {"name": "抖音热点", "platform": "抖音", "category": "视频", "priority": 9, "credibility": 0.75},
            {"name": "B 站热门", "platform": "B 站", "category": "视频", "priority": 8, "credibility": 0.8},
            
            # RSSHub 来源
            {"name": "澎湃新闻", "platform": "澎湃新闻", "category": "新闻", "priority": 8, "credibility": 0.9},
            {"name": "36 氪", "platform": "36 氪", "category": "财经", "priority": 7, "credibility": 0.85},
            {"name": "虎嗅", "platform": "虎嗅", "category": "财经", "priority": 7, "credibility": 0.8},
            {"name": "IT 之家", "platform": "IT 之家", "category": "科技", "priority": 7, "credibility": 0.75},
            {"name": "少数派", "platform": "少数派", "category": "科技", "priority": 6, "credibility": 0.8},
        ]
        
        for source in sources:
            self.db.add_source(**source)
        
        print(f"[Collector] ✅ 初始化 {len(sources)} 个数据源")
    
    def collect_all(self, save_to_db: bool = True) -> Dict[str, Any]:
        """
        采集所有数据源
        
        Args:
            save_to_db: 是否保存到数据库
        
        Returns:
            采集结果统计
        """
        print(f"\n{'='*70}")
        print("📡 开始采集热点数据")
        print(f"{'='*70}\n")
        
        start_time = datetime.now()
        
        # 1. DailyHotApi 采集
        if DAILYHOT_AVAILABLE:
            print("Step 1: DailyHotApi 采集")
            dailyhot_result = self._collect_dailyhot()
            print(f"   ✅ 采集 {dailyhot_result['count']} 条\n")
        else:
            dailyhot_result = {"count": 0, "items": []}
        
        # 2. RSSHub 采集
        if RSSHUB_AVAILABLE:
            print("Step 2: RSSHub 采集")
            rsshub_result = self._collect_rsshub()
            print(f"   ✅ 采集 {rsshub_result['count']} 条\n")
        else:
            rsshub_result = {"count": 0, "items": []}
        
        # 3. 视频采集
        if VIDEO_AVAILABLE:
            print("Step 3: 视频采集")
            video_result = self._collect_videos()
            print(f"   ✅ 采集 {video_result['count']} 条\n")
        else:
            video_result = {"count": 0, "items": []}
        
        # 4. 合并结果
        all_items = (
            dailyhot_result.get('items', []) +
            rsshub_result.get('items', []) +
            video_result.get('items', [])
        )
        
        self.stats['total_collected'] = len(all_items)
        
        # 5. 保存到数据库
        if save_to_db:
            print("Step 4: 保存到数据库")
            store_result = self._save_to_database(all_items)
            print(f"   ✅ 存储 {store_result['stored']} 条，跳过 {store_result['skipped']} 条 (重复)\n")
        
        # 6. 生成报告
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        report = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'total_collected': self.stats['total_collected'],
            'total_stored': self.stats['total_stored'],
            'duplicates': self.stats['duplicates'],
            'errors': self.stats['errors'],
            'by_source': {
                'dailyhot': dailyhot_result.get('count', 0),
                'rsshub': rsshub_result.get('count', 0),
                'video': video_result.get('count', 0)
            }
        }
        
        print(f"{'='*70}")
        print("📊 采集完成")
        print(f"  总采集：{report['total_collected']} 条")
        print(f"  总存储：{report['total_stored']} 条")
        print(f"  重复跳过：{report['duplicates']} 条")
        print(f"  耗时：{duration:.2f}秒")
        print(f"{'='*70}\n")
        
        return report
    
    def _collect_dailyhot(self) -> Dict[str, Any]:
        """采集 DailyHotApi"""
        try:
            result = collect_dailyhot()
            items = result.get('items', [])
            
            # 标准化格式
            standardized = []
            for item in items:
                standardized.append({
                    'title': item.get('title', ''),
                    'content': item.get('desc', item.get('content', '')),
                    'url': item.get('url', ''),
                    'source_name': item.get('source_name', 'DailyHot'),
                    'category': self._auto_categorize(item.get('title', '')),
                    'tags': self._extract_tags(item.get('title', '')),
                    'keywords': self._extract_keywords(item.get('title', ''))
                })
            
            return {'count': len(standardized), 'items': standardized}
        except Exception as e:
            print(f"   ❌ DailyHotApi 采集失败：{e}")
            self.stats['errors'] += 1
            return {'count': 0, 'items': []}
    
    def _collect_rsshub(self) -> Dict[str, Any]:
        """采集 RSSHub"""
        try:
            result = collect_rsshub()
            items = result.get('items', [])
            
            # 标准化格式
            standardized = []
            for item in items:
                standardized.append({
                    'title': item.get('title', ''),
                    'content': item.get('description', item.get('content', '')),
                    'url': item.get('link', item.get('url', '')),
                    'source_name': item.get('source', 'RSSHub'),
                    'category': self._auto_categorize(item.get('title', '')),
                    'tags': self._extract_tags(item.get('title', '')),
                    'keywords': self._extract_keywords(item.get('title', ''))
                })
            
            return {'count': len(standardized), 'items': standardized}
        except Exception as e:
            print(f"   ❌ RSSHub 采集失败：{e}")
            self.stats['errors'] += 1
            return {'count': 0, 'items': []}
    
    def _collect_videos(self) -> Dict[str, Any]:
        """采集视频"""
        try:
            result = collect_videos()
            items = result.get('items', [])
            
            # 标准化格式
            standardized = []
            for item in items:
                standardized.append({
                    'title': item.get('title', ''),
                    'content': item.get('desc', ''),
                    'url': item.get('url', ''),
                    'source_name': item.get('platform', 'Video'),
                    'category': '视频',
                    'tags': self._extract_tags(item.get('title', '')),
                    'keywords': self._extract_keywords(item.get('title', '')),
                    'extra': {
                        'play_count': item.get('play_count'),
                        'author': item.get('author')
                    }
                })
            
            return {'count': len(standardized), 'items': standardized}
        except Exception as e:
            print(f"   ❌ 视频采集失败：{e}")
            self.stats['errors'] += 1
            return {'count': 0, 'items': []}
    
    def _save_to_database(self, items: List[Dict]) -> Dict[str, int]:
        """保存到数据库"""
        stored = 0
        skipped = 0
        
        for item in items:
            topic_id = self.db.add_hot_topic(**item)
            
            if topic_id > 0:
                stored += 1
            else:
                skipped += 1
        
        self.stats['total_stored'] = stored
        self.stats['duplicates'] = skipped
        
        return {'stored': stored, 'skipped': skipped}
    
    def _auto_categorize(self, title: str) -> str:
        """自动分类"""
        category_keywords = {
            '科技': ['AI', '人工智能', '科技', '互联网', '数码', '手机', '芯片'],
            '财经': ['财经', '股票', '基金', '投资', '理财', '经济', '金融'],
            '教育': ['教育', '学校', '考试', '培训', '学习', '教师', '学生'],
            '娱乐': ['娱乐', '明星', '电影', '电视剧', '综艺', '音乐'],
            '体育': ['体育', '比赛', '运动员', '球队', '奥运', '足球', '篮球'],
            '社会': ['社会', '民生', '政策', '政府', '法院', '公安']
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in title for kw in keywords):
                return category
        
        return '综合'
    
    def _extract_tags(self, title: str) -> List[str]:
        """提取标签"""
        tags = []
        
        # 热点类型标签
        if any(kw in title for kw in ['突发', '刚刚', '最新']):
            tags.append('突发')
        if any(kw in title for kw in ['重磅', '重要', '重磅发布']):
            tags.append('重磅')
        if any(kw in title for kw in ['曝光', '揭秘', '内幕']):
            tags.append('曝光')
        
        # 领域标签
        if 'AI' in title or '人工智能' in title:
            tags.append('AI')
        if '教育' in title:
            tags.append('教育')
        if '财经' in title or '股票' in title:
            tags.append('财经')
        
        return list(set(tags))
    
    def _extract_keywords(self, title: str) -> List[str]:
        """提取关键词"""
        import re
        
        # 简单分词 (2-4 字中文词)
        keywords = re.findall(r'[\u4e00-\u9fa5]{2,4}', title)
        
        # 过滤停用词
        stopwords = ['的', '了', '是', '在', '和', '与', '及', '等', '就', '都', '也', '还']
        keywords = [kw for kw in keywords if kw not in stopwords]
        
        # 保留前 10 个
        return keywords[:10]
    
    def get_hot_topics(self, limit: int = 20, **kwargs) -> List[Dict]:
        """获取热点列表 (代理到数据库)"""
        return self.db.get_hot_topics(limit=limit, **kwargs)
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取统计数据 (代理到数据库)"""
        return self.db.get_statistics(days=days)
    
    def cleanup(self, days_to_keep: int = 30):
        """清理旧数据"""
        return self.db.cleanup_old_data(days_to_keep)
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()


def test_collector_v2():
    """测试采集器 V2"""
    print("\n" + "="*70)
    print("📡 热点采集器 V2 测试")
    print("="*70 + "\n")
    
    collector = HotNewsCollectorV2()
    
    # 1. 采集所有数据
    report = collector.collect_all(save_to_db=True)
    
    # 2. 查询热点
    print("="*70)
    print("📋 最新热点 TOP10")
    print("="*70 + "\n")
    
    topics = collector.get_hot_topics(limit=10)
    for i, t in enumerate(topics, 1):
        print(f"{i}. [{t['heat_level']}] {t['title'][:50]}...")
        print(f"   来源：{t['source_name']} | 分类：{t.get('category', 'N/A')} | 热度：{t['heat_score']:.1f}\n")
    
    # 3. 统计
    print("="*70)
    print("📊 统计数据")
    print("="*70 + "\n")
    
    stats = collector.get_statistics(days=7)
    print(f"总热点数：{stats['overall']['total_count']}")
    print(f"平均热度：{stats['overall']['avg_heat']:.1f}")
    print(f"唯一热点：{stats['overall']['unique_count']}")
    
    print(f"\n按分类:")
    for cat in stats['by_category'][:5]:
        print(f"  - {cat['category']}: {cat['count']}条，平均热度{cat['avg_heat']:.1f}")
    
    print(f"\n热词 TOP10:")
    for kw in stats['hot_keywords'][:10]:
        print(f"  - {kw['keyword']}: {kw['count']}次")
    
    collector.close()
    
    print("\n" + "="*70)
    print("🎉 采集器 V2 测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_collector_v2()
