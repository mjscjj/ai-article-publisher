#!/usr/bin/env python3
"""
【RAG 知识库客户端】AnythingLLM Client
对接本机 AI Base (AnythingLLM) 实现 RAG 功能

功能:
1. 文档上传 - 将文章/素材上传到知识库
2. 智能检索 - 基于语义搜索相关文档
3. 问答增强 - 结合知识库生成回答
4. 素材管理 - 分类管理写作素材

配置:
- AI Base URL: http://43.134.234.4:3001
- API Key: sk-WaUmgZsMxgeHOpp8SJxK1rmVQxiwfiDJ
"""

import json
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

class AnythingLLMClient:
    """AnythingLLM RAG 客户端"""
    
    def __init__(self, 
                 base_url: str = "http://43.134.234.4:3001",
                 api_key: str = None,
                 workspace_id: str = None):
        self.base_url = base_url
        self.api_key = api_key or "sk-WaUmgZsMxgeHOpp8SJxK1rmVQxiwfiDJ"
        # 使用默认工作空间 ID (从 AnythingLLM 获取)
        self.workspace_id = workspace_id or "0"  # 默认工作空间
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 本地缓存目录
        self.cache_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'rag_cache'
        )
        os.makedirs(self.cache_dir, exist_ok=True)
    
    # ========== 工作空间管理 ==========
    
    def get_workspace(self, workspace_id: str = None) -> Optional[Dict]:
        """获取工作空间信息"""
        wid = workspace_id or self.workspace_id
        url = f"{self.base_url}/api/v1/workspace/{wid}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            print(f"[RAG] 获取工作空间失败：{e}")
            return None
    
    def list_workspaces(self) -> List[Dict]:
        """获取所有工作空间列表"""
        url = f"{self.base_url}/api/v1/workspaces"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("workspaces", [])
            return []
        except Exception as e:
            print(f"[RAG] 获取工作空间列表失败：{e}")
            return []
    
    def create_workspace(self, name: str = None) -> Optional[Dict]:
        """创建工作空间"""
        if not name:
            name = f"workspace_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        url = f"{self.base_url}/api/v1/workspace"
        payload = {"name": name}
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=10)
            if resp.status_code in [200, 201]:
                result = resp.json()
                self.workspace_id = str(result.get("id", self.workspace_id))
                print(f"[RAG] ✅ 工作空间创建成功：{name} (ID: {self.workspace_id})")
                return result
            print(f"[RAG] ⚠️ 工作空间创建失败：{resp.text}")
            return None
        except Exception as e:
            print(f"[RAG] 创建工作空间失败：{e}")
            return None
    
    # ========== 文档管理 ==========
    
    def upload_document(self, content: str, filename: str = None, 
                       metadata: Dict = None) -> bool:
        """
        上传文档到知识库
        
        Args:
            content: 文档内容 (Markdown 或纯文本)
            filename: 文件名 (可选)
            metadata: 元数据 (可选)
        """
        if not filename:
            filename = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # 保存到本地缓存
        cache_path = os.path.join(self.cache_dir, filename)
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 调用 AnythingLLM API 上传
        url = f"{self.base_url}/api/v1/workspace/{self.workspace_id}/documents"
        
        payload = {
            "documents": [
                {
                    "name": filename,
                    "content": content,
                    "metadata": metadata or {}
                }
            ]
        }
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if resp.status_code in [200, 201]:
                print(f"[RAG] ✅ 文档上传成功：{filename}")
                return True
            print(f"[RAG] ⚠️ 文档上传失败：{resp.text}")
            return False
        except Exception as e:
            print(f"[RAG] 上传文档失败：{e}")
            return False
    
    def upload_article(self, title: str, content: str, 
                      topic: str = None, tags: List[str] = None) -> bool:
        """
        上传文章到知识库
        
        Args:
            title: 文章标题
            content: 文章内容
            topic: 话题分类
            tags: 标签列表
        """
        metadata = {
            "type": "article",
            "title": title,
            "topic": topic or "",
            "tags": tags or [],
            "created_at": datetime.now().isoformat()
        }
        
        filename = f"article_{title[:20].replace(' ', '_')}.md"
        full_content = f"# {title}\n\n{content}"
        
        return self.upload_document(full_content, filename, metadata)
    
    def list_documents(self) -> List[Dict]:
        """获取文档列表"""
        url = f"{self.base_url}/api/v1/workspace/{self.workspace_id}/documents"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("documents", [])
            return []
        except Exception as e:
            print(f"[RAG] 获取文档列表失败：{e}")
            return []
    
    def delete_document(self, doc_name: str) -> bool:
        """删除文档"""
        url = f"{self.base_url}/api/v1/workspace/{self.workspace_id}/documents/{doc_name}"
        try:
            resp = requests.delete(url, headers=self.headers, timeout=10)
            if resp.status_code in [200, 204]:
                print(f"[RAG] ✅ 文档删除成功：{doc_name}")
                return True
            return False
        except Exception as e:
            print(f"[RAG] 删除文档失败：{e}")
            return False
    
    # ========== 智能检索 ==========
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        语义搜索相关文档
        
        Args:
            query: 搜索 query
            top_k: 返回结果数量
        """
        # 使用聊天接口的 search 模式
        url = f"{self.base_url}/api/v1/workspace/{self.workspace_id}/chat"
        payload = {
            "message": query,
            "mode": "search",
            "top_k": top_k
        }
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                sources = result.get("sources", [])
                if sources:
                    print(f"[RAG] ✅ 搜索到 {len(sources)} 条结果")
                    return sources
                print(f"[RAG] ⚠️ 无搜索结果")
                return []
            print(f"[RAG] ⚠️ 搜索失败：{resp.text[:200]}")
            return []
        except Exception as e:
            print(f"[RAG] 搜索失败：{e}")
            return []
    
    def query(self, question: str, 
              include_sources: bool = True) -> Dict[str, Any]:
        """
        基于知识库问答
        
        Args:
            question: 问题
            include_sources: 是否返回来源
        """
        url = f"{self.base_url}/api/v1/workspace/{self.workspace_id}/chat"
        payload = {
            "message": question,
            "mode": "chat"  # 使用 chat 模式
        }
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                return {
                    "answer": result.get("response", ""),
                    "sources": result.get("sources", []) if include_sources else []
                }
            print(f"[RAG] ⚠️ 问答失败：{resp.text[:200]}")
            return {"answer": "", "sources": []}
        except Exception as e:
            print(f"[RAG] 问答失败：{e}")
            return {"answer": "", "sources": []}
    
    # ========== 素材管理 ==========
    
    def save_writing_material(self, category: str, content: str, 
                             description: str = "") -> bool:
        """
        保存写作素材
        
        Args:
            category: 分类 (case_study, quote, data, template...)
            content: 素材内容
            description: 描述
        """
        metadata = {
            "type": "material",
            "category": category,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        filename = f"material_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        return self.upload_document(content, filename, metadata)
    
    def get_materials(self, category: str = None, limit: int = 10) -> List[Dict]:
        """获取写作素材"""
        # 简单实现：搜索特定分类
        if category:
            query = f"category:{category}"
        else:
            query = "type:material"
        
        return self.search(query, limit)
    
    # ========== 批量操作 ==========
    
    def batch_upload_articles(self, articles: List[Dict]) -> Dict[str, int]:
        """
        批量上传文章
        
        Args:
            articles: 文章列表 [{"title": "...", "content": "...", "topic": "..."}]
        
        Returns:
            {"success": 成功数，"failed": 失败数}
        """
        stats = {"success": 0, "failed": 0}
        
        for i, article in enumerate(articles):
            success = self.upload_article(
                title=article.get("title", f"Article_{i}"),
                content=article.get("content", ""),
                topic=article.get("topic"),
                tags=article.get("tags", [])
            )
            
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1
            
            # 避免频率限制
            if (i + 1) % 10 == 0:
                print(f"[RAG] 已上传 {i+1}/{len(articles)} 篇...")
        
        return stats


# ========== 便捷函数 ==========

def get_rag_client() -> AnythingLLMClient:
    """获取 RAG 客户端实例"""
    return AnythingLLMClient()


def test_rag_client():
    """测试 RAG 客户端"""
    print("\n" + "="*70)
    print("🤖 RAG 知识库客户端测试")
    print("="*70 + "\n")
    
    client = get_rag_client()
    
    # 1. 获取工作空间列表
    print("Step 1: 获取工作空间列表")
    workspaces = client.list_workspaces()
    if workspaces:
        print(f"✅ 发现 {len(workspaces)} 个工作空间:")
        for ws in workspaces[:5]:
            print(f"   - {ws.get('name', 'N/A')} (ID: {ws.get('id', 'N/A')})")
        # 使用第一个工作空间
        client.workspace_id = str(workspaces[0].get('id', '0'))
        print(f"   使用工作空间：{client.workspace_id}")
    else:
        print("⚠️ 无工作空间，创建默认工作空间...")
        client.create_workspace("ai-article-publisher")
    
    # 2. 上传测试文档
    print("\nStep 2: 上传测试文档")
    test_content = """
# AI 写作技巧：如何写出爆款文章

## 核心观点
1. 好的切入角是成功的一半
2. 数据支撑让观点更有说服力
3. 金句提升文章传播力

## 实战案例
某篇关于 AI 教育的文章，通过"60% 高校已开设 AI 课程"这个数据点，
成功制造了紧迫感和焦虑感，最终获得 10w+ 阅读。

## 金句积累
- "AI 不会取代你，但会用 AI 的人会"
- "在变革时代，认知是最大的护城河"
"""
    
    success = client.upload_document(
        content=test_content,
        filename="test_writing_tips.md",
        metadata={"type": "test", "tags": ["写作技巧", "爆款"]}
    )
    print(f"上传结果：{'✅ 成功' if success else '❌ 失败'}")
    
    # 3. 搜索测试
    print("\nStep 3: 搜索测试")
    results = client.search("AI 写作技巧", top_k=3)
    if results:
        print(f"✅ 搜索到 {len(results)} 条结果")
        for i, r in enumerate(results[:2], 1):
            print(f"  {i}. {r.get('title', 'N/A')[:50]}...")
    
    # 4. 问答测试
    print("\nStep 4: 问答测试")
    result = client.query("如何写出爆款文章？")
    if result["answer"]:
        print(f"✅ 回答：{result['answer'][:100]}...")
        if result["sources"]:
            print(f"   来源：{len(result['sources'])} 个")
    
    # 5. 保存素材
    print("\nStep 5: 保存写作素材")
    success = client.save_writing_material(
        category="golden_sentence",
        content="AI 不会取代你，但会用 AI 的人会",
        description="适合用于 AI 相关文章结尾"
    )
    print(f"素材保存：{'✅ 成功' if success else '❌ 失败'}")
    
    # 6. 获取素材
    print("\nStep 6: 获取金句素材")
    materials = client.get_materials("golden_sentence", limit=5)
    print(f"获取到 {len(materials)} 条金句素材")
    
    print("\n" + "="*70)
    print("🎉 RAG 客户端测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_rag_client()
