#!/usr/bin/env python3
"""
【RAG 知识库】简易版 - 基于本地文件系统
不依赖 AnythingLLM API，使用本地 JSON 存储 + BM25 搜索

功能:
1. 文档存储 - JSON 格式本地存储
2. 全文搜索 - BM25 算法
3. 素材管理 - 分类管理
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import Counter
import math

class SimpleRAG:
    """简易 RAG 知识库"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'rag'
            )
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 文档存储文件
        self.docs_file = os.path.join(data_dir, "documents.json")
        self.index_file = os.path.join(data_dir, "index.json")
        
        # 加载文档
        self.documents = self._load_documents()
        self._build_index()
    
    def _load_documents(self) -> List[Dict]:
        """加载文档"""
        if os.path.exists(self.docs_file):
            try:
                with open(self.docs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_documents(self):
        """保存文档"""
        with open(self.docs_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def _build_index(self):
        """构建倒排索引"""
        self.index = {}
        for i, doc in enumerate(self.documents):
            # 简单分词 (中文按字符)
            text = doc.get('title', '') + ' ' + doc.get('content', '')[:500]
            words = re.findall(r'[\u4e00-\u9fa5]{2,4}|\w+', text.lower())
            
            for word in set(words):
                if word not in self.index:
                    self.index[word] = []
                self.index[word].append(i)
        
        # 保存索引
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False)
    
    def add_document(self, title: str, content: str, 
                    category: str = "article", 
                    tags: List[str] = None,
                    metadata: Dict = None) -> bool:
        """
        添加文档
        
        Args:
            title: 标题
            content: 内容
            category: 分类 (article/material/quote/data...)
            tags: 标签列表
            metadata: 元数据
        """
        doc = {
            "id": len(self.documents) + 1,
            "title": title,
            "content": content,
            "category": category,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "word_count": len(content)
        }
        
        self.documents.append(doc)
        self._save_documents()
        self._build_index()
        
        print(f"[RAG] ✅ 文档添加成功：{title[:30]}...")
        return True
    
    def add_article(self, title: str, content: str, 
                   topic: str = None, tags: List[str] = None) -> bool:
        """添加文章"""
        metadata = {"topic": topic} if topic else {}
        return self.add_document(title, content, "article", tags, metadata)
    
    def add_material(self, category: str, content: str, 
                    description: str = "") -> bool:
        """添加素材"""
        metadata = {"description": description}
        title = f"{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return self.add_document(title, content, "material", [], metadata)
    
    def search(self, query: str, top_k: int = 5, 
               category: str = None) -> List[Dict]:
        """
        搜索文档
        
        Args:
            query: 搜索词
            top_k: 返回数量
            category: 分类过滤
        """
        # 简单 BM25 实现
        query_words = re.findall(r'[\u4e00-\u9fa5]{2,4}|\w+', query.lower())
        
        scores = []
        for i, doc in enumerate(self.documents):
            # 分类过滤
            if category and doc.get('category') != category:
                continue
            
            # 计算相关性
            text = doc.get('title', '') + ' ' + doc.get('content', '')[:500]
            text_words = re.findall(r'[\u4e00-\u9fa5]{2,4}|\w+', text.lower())
            
            score = 0
            for word in query_words:
                if word in text_words:
                    # 标题匹配权重更高
                    if word in doc.get('title', '').lower():
                        score += 3
                    else:
                        score += 1
            
            if score > 0:
                scores.append((score, i))
        
        # 排序
        scores.sort(reverse=True)
        
        # 返回结果
        results = []
        for score, i in scores[:top_k]:
            doc = self.documents[i].copy()
            doc['score'] = score
            doc['snippet'] = doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
            results.append(doc)
        
        print(f"[RAG] ✅ 搜索到 {len(results)} 条结果")
        return results
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        问答式查询
        
        返回最相关的文档片段
        """
        results = self.search(question, top_k=3)
        
        if not results:
            return {
                "answer": "未找到相关信息",
                "sources": []
            }
        
        # 构建答案
        best_doc = results[0]
        answer = f"根据知识库，{best_doc['title']}:\n\n{best_doc['snippet']}"
        
        return {
            "answer": answer,
            "sources": [
                {
                    "title": r['title'],
                    "category": r['category'],
                    "score": r.get('score', 0)
                }
                for r in results
            ]
        }
    
    def get_materials(self, category: str = None, limit: int = 10) -> List[Dict]:
        """获取素材"""
        if category:
            return [
                doc for doc in self.documents 
                if doc.get('category') == 'material' and 
                   doc.get('metadata', {}).get('description', '').find(category) >= 0
            ][:limit]
        else:
            return [
                doc for doc in self.documents 
                if doc.get('category') == 'material'
            ][:limit]
    
    def stats(self) -> Dict[str, Any]:
        """统计信息"""
        by_category = Counter(doc.get('category', 'unknown') for doc in self.documents)
        
        return {
            "total_docs": len(self.documents),
            "by_category": dict(by_category),
            "total_words": sum(doc.get('word_count', 0) for doc in self.documents)
        }


# ========== 便捷函数 ==========

def get_rag() -> SimpleRAG:
    """获取 RAG 实例"""
    return SimpleRAG()


def test_rag():
    """测试"""
    print("\n" + "="*70)
    print("📚 简易 RAG 知识库测试")
    print("="*70 + "\n")
    
    rag = get_rag()
    
    # 1. 添加文章
    print("Step 1: 添加测试文章")
    rag.add_article(
        title="AI 写作技巧：如何写出爆款文章",
        content="""
好的切入角是成功的一半。数据支撑让观点更有说服力。金句提升文章传播力。

某篇关于 AI 教育的文章，通过"60% 高校已开设 AI 课程"这个数据点，
成功制造了紧迫感和焦虑感，最终获得 10w+ 阅读。

金句积累:
- "AI 不会取代你，但会用 AI 的人会"
- "在变革时代，认知是最大的护城河"
""",
        topic="写作技巧",
        tags=["AI", "写作", "爆款"]
    )
    
    # 2. 添加素材
    print("\nStep 2: 添加写作素材")
    rag.add_material(
        category="golden_sentence",
        content="AI 不会取代你，但会用 AI 的人会",
        description="适合用于 AI 相关文章结尾"
    )
    
    # 3. 搜索
    print("\nStep 3: 搜索测试")
    results = rag.search("AI 写作", top_k=3)
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['title']} (分数：{r.get('score', 0)})")
    
    # 4. 问答
    print("\nStep 4: 问答测试")
    result = rag.query("如何写出爆款文章？")
    print(f"  答案：{result['answer'][:100]}...")
    print(f"  来源：{len(result['sources'])} 个")
    
    # 5. 统计
    print("\nStep 5: 统计信息")
    stats = rag.stats()
    print(f"  总文档数：{stats['total_docs']}")
    print(f"  分类分布：{stats['by_category']}")
    print(f"  总字数：{stats['total_words']}")
    
    print("\n" + "="*70)
    print("🎉 RAG 测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_rag()
