#!/usr/bin/env python3
"""
【话题发现引擎】Topic Discovery Engine
基于多源热点数据，智能发现值得写作的选题

功能:
1. 热点聚类 (TF-IDF + 语义相似度)
2. 选题评分 (热度 + 时效 + 竞争度 + 写作价值)
3. 选题推荐 (TOP N 排序)
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import Counter

class TopicDiscoveryEngine:
    """话题发现引擎"""
    
    def __init__(self, data_dir: str = None):
        if data_dir:
            self.data_dir = data_dir
        else:
            # 正确解析：plugins/topic_discovery/../../data = plugins/../data = data
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.data_dir = os.path.join(base_dir, 'data')
        self.hot_topics = []
    
    def load_hot_data(self, source_files: List[str] = None) -> List[Dict]:
        """
        加载热点数据
        
        默认加载:
        - data/by_source/*.json
        - data/hot_topics.json
        """
        if source_files is None:
            source_files = [
                os.path.join(self.data_dir, 'hot_topics.json'),
            ]
        
        all_items = []
        for file_path in source_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_items.extend(data)
                        elif isinstance(data, dict) and 'items' in data:
                            all_items.extend(data['items'])
                except Exception as e:
                    print(f"[TopicDiscovery] 加载 {file_path} 失败：{e}")
        
        self.hot_topics = all_items
        return all_items
    
    def cluster_topics(self, items: List[Dict], max_clusters: int = 20) -> List[Dict]:
        """
        简单聚类：基于关键词重叠度
        
        返回聚类后的话题组
        """
        if not items:
            return []
        
        # 提取关键词 (简单分词)
        def extract_keywords(item: Dict) -> List[str]:
            title = item.get('title', '')
            # 简单按中文字符分割 (每 2-4 字为一个词)
            import re
            # 提取 2-4 字的连续中文字符作为关键词
            chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', title)
            return chinese_words
        
        # 计算关键词频率
        all_keywords = []
        for item in items:
            keywords = extract_keywords(item)
            all_keywords.extend(keywords)
            item['_keywords'] = keywords
        
        keyword_freq = Counter(all_keywords)
        top_keywords = set([k for k, v in keyword_freq.most_common(50)])
        
        # 基于关键词聚类
        clusters = {}
        for item in items:
            # 找到最匹配的关键词
            matched = [k for k in item['_keywords'] if k in top_keywords]
            if matched:
                cluster_key = matched[0]
                if cluster_key not in clusters:
                    clusters[cluster_key] = []
                clusters[cluster_key].append(item)
        
        # 转换为聚类结果
        result = []
        for keyword, cluster_items in clusters.items():
            if len(cluster_items) >= 2:  # 至少 2 条才成簇
                # 计算簇的热度 (累加)
                total_heat = sum([
                    item.get('heat', 10) or 10 
                    for item in cluster_items
                ])
                
                result.append({
                    'cluster_keyword': keyword,
                    'items': cluster_items,
                    'count': len(cluster_items),
                    'total_heat': total_heat,
                    'latest_time': max([
                        item.get('timestamp', 0) or 0
                        for item in cluster_items
                    ], default=0),
                })
        
        # 按热度排序
        result.sort(key=lambda x: x['total_heat'], reverse=True)
        return result[:max_clusters]
    
    def score_topic(self, cluster: Dict) -> Dict[str, Any]:
        """
        选题评分
        
        维度:
        - 热度分 (30%): 聚类总热度
        - 时效分 (25%): 时间新鲜度
        - 丰富度 (25%): 聚类条目数
        - 写作价值 (20%): 关键词质量
        """
        # 热度分 (0-100)
        heat_score = min(100, cluster['total_heat'] / 10)
        
        # 时效分 (0-100)
        now = datetime.now().timestamp()
        hours_ago = (now - cluster['latest_time']) / 3600
        if hours_ago < 2:
            time_score = 100
        elif hours_ago < 6:
            time_score = 80
        elif hours_ago < 24:
            time_score = 60
        elif hours_ago < 72:
            time_score = 40
        else:
            time_score = 20
        
        # 丰富度分 (0-100)
        richness_score = min(100, cluster['count'] * 10)
        
        # 写作价值 (基于关键词长度和多样性)
        keyword = cluster['cluster_keyword']
        if 3 <= len(keyword) <= 6:
            value_score = 80
        else:
            value_score = 60
        
        # 加权总分
        total_score = (
            heat_score * 0.30 +
            time_score * 0.25 +
            richness_score * 0.25 +
            value_score * 0.20
        )
        
        return {
            'cluster': cluster,
            'scores': {
                'heat': round(heat_score, 1),
                'time': round(time_score, 1),
                'richness': round(richness_score, 1),
                'value': round(value_score, 1),
                'total': round(total_score, 1),
            },
            'recommendation': self._get_recommendation(total_score),
        }
    
    def _get_recommendation(self, score: float) -> str:
        if score >= 80:
            return "🔥 强烈推荐 - 立即写作"
        elif score >= 60:
            return "✅ 推荐 - 值得考虑"
        elif score >= 40:
            return "⚠️ 一般 - 可作为备选"
        else:
            return "❌ 不推荐 - 热度不足"
    
    def discover_topics(self, max_topics: int = 10, source_files: List[str] = None) -> List[Dict]:
        """
        发现并推荐选题
        
        返回评分后的 TOP N 选题
        """
        # 加载数据
        if source_files is None:
            # 默认尝试多个可能的文件
            source_files = [
                os.path.join(self.data_dir, 'ai_topics.json'),
                os.path.join(self.data_dir, 'hot_topics.json'),
            ]
        items = self.load_hot_data(source_files)
        if not items:
            print("[TopicDiscovery] ⚠️ 无热点数据")
            return []
        
        # 聚类
        clusters = self.cluster_topics(items)
        print(f"[TopicDiscovery] ✅ 聚类完成：{len(clusters)} 个话题簇")
        
        # 评分
        scored = [self.score_topic(c) for c in clusters]
        scored.sort(key=lambda x: x['scores']['total'], reverse=True)
        
        # 返回 TOP N
        return scored[:max_topics]


if __name__ == "__main__":
    engine = TopicDiscoveryEngine()
    topics = engine.discover_topics(5)
    
    print("\n" + "="*60)
    print("📊 今日推荐选题 TOP 5")
    print("="*60)
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{i}. {topic['cluster']['cluster_keyword']}")
        print(f"   总分：{topic['scores']['total']} | {topic['recommendation']}")
        print(f"   热度:{topic['scores']['heat']} 时效:{topic['scores']['time']} "
              f"丰富:{topic['scores']['richness']} 价值:{topic['scores']['value']}")
        print(f"   条目数：{topic['cluster']['count']} | "
              f"总热度：{topic['cluster']['total_heat']}")
