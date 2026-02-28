#!/usr/bin/env python3
"""
【深度信息检索】Deep Information Retriever
多源数据检索 + 智能聚合 + 事实验证

数据源:
1. RAG 知识库 (本地)
2. 热点数据源 (sources/)
3. 网络搜索 (enhanced_search.py)
4. 垂直领域采集器

功能:
1. 多源检索 - 并行搜索多个数据源
2. 智能去重 - 基于语义相似度
3. 可信度评分 - 评估信息可靠性
4. 事实提取 - 结构化提取关键信息
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class DeepRetriever:
    """深度信息检索器"""
    
    def __init__(self):
        # 数据源目录
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data'
        )
        
        # 热点数据缓存
        self.hot_data_cache = []
        
        # 加载本地数据
        self._load_local_data()
    
    def _load_local_data(self):
        """加载本地热点数据"""
        # 加载 by_source 目录下的数据
        by_source_dir = os.path.join(self.data_dir, 'by_source')
        if os.path.exists(by_source_dir):
            for filename in os.listdir(by_source_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(by_source_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                self.hot_data_cache.extend(data)
                    except:
                        pass
        
        print(f"[Retriever] ✅ 加载 {len(self.hot_data_cache)} 条本地数据")
    
    def retrieve(self, topic: str, 
                 top_k: int = 10,
                 sources: List[str] = None) -> List[Dict[str, Any]]:
        """
        多源检索
        
        Args:
            topic: 检索话题
            top_k: 返回数量
            sources: 指定数据源 (可选)
        
        Returns:
            检索结果列表，按相关性排序
        """
        results = []
        
        # 1. RAG 检索
        rag_results = self._search_rag(topic, top_k // 2)
        results.extend(rag_results)
        
        # 2. 本地热点检索
        local_results = self._search_local(topic, top_k)
        results.extend(local_results)
        
        # 3. 去重
        deduped = self._deduplicate(results)
        
        # 4. 可信度评分
        scored = self._score_credibility(deduped)
        
        # 5. 排序
        scored.sort(key=lambda x: (x.get('relevance', 0), x.get('credibility', 0)), reverse=True)
        
        return scored[:top_k]
    
    def _search_rag(self, topic: str, top_k: int) -> List[Dict]:
        """RAG 检索"""
        try:
            from core.rag_simple import SimpleRAG
            rag = SimpleRAG()
            results = rag.search(topic, top_k=top_k)
            
            # 标准化格式
            for r in results:
                r['source'] = 'RAG'
                r['source_type'] = 'knowledge_base'
            
            print(f"[Retriever] RAG 检索到 {len(results)} 条")
            return results
        except Exception as e:
            print(f"[Retriever] ⚠️ RAG 检索失败：{e}")
            return []
    
    def _search_local(self, topic: str, top_k: int) -> List[Dict]:
        """本地热点检索"""
        results = []
        topic_keywords = self._extract_keywords(topic)
        
        for item in self.hot_data_cache:
            # 计算相关性
            title = item.get('title', '')
            score = self._calculate_relevance(topic_keywords, title)
            
            if score > 0:
                results.append({
                    'title': title,
                    'content': item.get('content', item.get('snippet', '')),
                    'url': item.get('url', ''),
                    'source': item.get('source_name', 'Unknown'),
                    'source_type': 'hot_news',
                    'timestamp': item.get('crawl_time', ''),
                    'relevance': score
                })
        
        print(f"[Retriever] 本地检索到 {len(results)} 条")
        return results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        import re
        # 中文 2-4 字词 + 英文单词
        keywords = re.findall(r'[\u4e00-\u9fa5]{2,4}|\w+', text.lower())
        return keywords
    
    def _calculate_relevance(self, keywords: List[str], text: str) -> float:
        """计算相关性"""
        text_lower = text.lower()
        matched = sum(1 for kw in keywords if kw in text_lower)
        return matched / max(len(keywords), 1)
    
    def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """去重 (基于标题相似度)"""
        seen_hashes = set()
        deduped = []
        
        for r in results:
            # 计算标题哈希
            title = r.get('title', '')
            title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()
            
            if title_hash not in seen_hashes:
                seen_hashes.add(title_hash)
                deduped.append(r)
        
        print(f"[Retriever] 去重后 {len(deduped)} 条 (原{len(results)}条)")
        return deduped
    
    def _score_credibility(self, results: List[Dict]) -> List[Dict]:
        """可信度评分"""
        source_weights = {
            'RAG': 0.9,
            '官方媒体': 0.9,
            '知名媒体': 0.8,
            '行业媒体': 0.7,
            '社交媒体': 0.5,
            'Unknown': 0.5
        }
        
        for r in results:
            source = r.get('source', 'Unknown')
            
            # 基础可信度
            credibility = source_weights.get(source, 0.5)
            
            # 有时效性加分
            timestamp = r.get('timestamp', '')
            if timestamp:
                try:
                    crawl_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    days_old = (datetime.now() - crawl_time).days
                    if days_old <= 1:
                        credibility += 0.1
                    elif days_old <= 3:
                        credibility += 0.05
                except:
                    pass
            
            # 有 URL 加分
            if r.get('url'):
                credibility += 0.05
            
            r['credibility'] = min(1.0, credibility)
        
        return results
    
    def extract_facts(self, results: List[Dict]) -> List[str]:
        """
        从检索结果中提取事实
        
        Returns:
            事实列表
        """
        facts = []
        
        for r in results[:10]:  # 取前 10 条
            # 提取标题作为事实
            title = r.get('title', '')
            if title and len(title) > 10:
                facts.append(title)
            
            # 提取内容摘要
            content = r.get('content', '')
            if content and len(content) > 50:
                # 取第一句
                first_sentence = content.split('。')[0] + '。'
                if len(first_sentence) > 20:
                    facts.append(first_sentence)
        
        # 去重
        unique_facts = list(dict.fromkeys(facts))
        
        print(f"[Retriever] 提取 {len(unique_facts)} 条事实")
        return unique_facts
    
    def get_statistics(self, topic: str, results: List[Dict]) -> Dict[str, Any]:
        """
        生成检索统计
        
        Returns:
            统计信息
        """
        source_dist = Counter(r.get('source', 'Unknown') for r in results)
        
        # 可信度分布
        high_cred = sum(1 for r in results if r.get('credibility', 0) >= 0.8)
        med_cred = sum(1 for r in results if 0.5 <= r.get('credibility', 0) < 0.8)
        low_cred = sum(1 for r in results if r.get('credibility', 0) < 0.5)
        
        return {
            'topic': topic,
            'total_results': len(results),
            'source_distribution': dict(source_dist),
            'credibility': {
                'high': high_cred,
                'medium': med_cred,
                'low': low_cred
            },
            'avg_relevance': sum(r.get('relevance', 0) for r in results) / max(len(results), 1),
            'retrieval_time': datetime.now().isoformat()
        }


def test_deep_retriever():
    """测试"""
    print("\n" + "="*70)
    print("🔍 深度信息检索测试")
    print("="*70 + "\n")
    
    retriever = DeepRetriever()
    
    # 测试检索
    topic = "人工智能 教育"
    print(f"检索话题：{topic}\n")
    
    results = retriever.retrieve(topic, top_k=10)
    
    print(f"\n{'='*70}")
    print("📊 检索结果")
    print(f"{'='*70}\n")
    
    for i, r in enumerate(results[:5], 1):
        print(f"{i}. [{r.get('source', 'Unknown')}] {r.get('title', 'N/A')[:50]}...")
        print(f"   相关性：{r.get('relevance', 0):.2f} | 可信度：{r.get('credibility', 0):.2f}\n")
    
    # 提取事实
    print("="*70)
    print("📋 提取事实")
    print("="*70 + "\n")
    
    facts = retriever.extract_facts(results)
    for i, fact in enumerate(facts[:5], 1):
        print(f"{i}. {fact}\n")
    
    # 统计
    print("="*70)
    print("📈 检索统计")
    print("="*70 + "\n")
    
    stats = retriever.get_statistics(topic, results)
    print(f"总结果数：{stats['total_results']}")
    print(f"来源分布：{stats['source_distribution']}")
    print(f"可信度分布：高={stats['credibility']['high']}, 中={stats['credibility']['medium']}, 低={stats['credibility']['low']}")
    print(f"平均相关性：{stats['avg_relevance']:.2f}")
    
    print("\n" + "="*70)
    print("🎉 深度检索测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_deep_retriever()
