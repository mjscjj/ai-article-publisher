"""
知乎发布模块
支持文章发布和想法发布
"""
import requests
import time
import hashlib
import hmac
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ZhihuPublisher:
    """知乎发布器"""
    
    def __init__(self, access_token: str):
        """
        初始化知乎发布器
        
        Args:
            access_token: 知乎 OAuth2 access_token
        """
        self.access_token = access_token
        self.base_url = "https://api.zhihu.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, path: str, data: Optional[Dict] = None,
                 params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """发送 HTTP 请求"""
        url = f"{self.base_url}{path}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, params=params, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data, params=params, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, params=params, timeout=30)
            else:
                logger.error(f"不支持的 HTTP 方法：{method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"请求失败：{response.status_code}, {response.text}")
                return None
        except Exception as e:
            logger.error(f"请求异常：{e}")
            return None
    
    def create_article(self, title: str, content: str, 
                       topics: Optional[List[str]] = None,
                       cover_image: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        创建文章
        
        Args:
            title: 文章标题
            content: 文章内容（Markdown 格式）
            topics: 话题列表
            cover_image: 封面图片 URL
            
        Returns:
            文章信息或 None
        """
        # 1. 准备文章内容
        # 知乎 API 需要先将内容转换为 HTML 或使用 Markdown
        data = {
            "title": title,
            "content": content,
            "content_type": "markdown"  # 或 "html"
        }
        
        if topics:
            data["topics"] = topics
        
        # 2. 创建文章
        result = self._request("POST", "/articles", data=data)
        
        if result:
            logger.info(f"知乎文章创建成功：{result.get('id')}")
            return result
        else:
            logger.error("知乎文章创建失败")
            return None
    
    def upload_image(self, image_url: str) -> Optional[str]:
        """
        上传图片到知乎
        
        Args:
            image_url: 图片 URL
            
        Returns:
            图片 token 或 None
        """
        try:
            # 下载图片
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                logger.error(f"下载图片失败：{image_url}")
                return None
            
            image_data = response.content
            
            # 上传图片
            upload_url = f"{self.base_url}/upload"
            files = {"file": ("image.jpg", image_data, "image/jpeg")}
            
            upload_response = requests.post(upload_url, headers=self.headers, files=files, timeout=30)
            
            if upload_response.status_code == 200:
                result = upload_response.json()
                image_token = result.get("token")
                logger.info(f"图片上传成功：{image_token}")
                return image_token
            else:
                logger.error(f"图片上传失败：{upload_response.status_code}")
                return None
        except Exception as e:
            logger.error(f"上传图片异常：{e}")
            return None
    
    def publish_article(self, title: str, content: str,
                       topics: Optional[List[str]] = None,
                       cover_image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        发布文章（完整流程）
        
        Args:
            title: 文章标题
            content: 文章内容
            topics: 话题列表
            cover_image_url: 封面图片 URL
            
        Returns:
            发布结果
        """
        result = {
            "success": False,
            "article_id": None,
            "article_url": None,
            "error": None
        }
        
        # 1. 上传封面图片（如果有）
        cover_token = None
        if cover_image_url:
            logger.info(f"上传封面图片：{cover_image_url}")
            cover_token = self.upload_image(cover_image_url)
        
        # 2. 创建文章
        logger.info(f"创建知乎文章：{title}")
        article = self.create_article(
            title=title,
            content=content,
            topics=topics,
            cover_image=cover_token
        )
        
        if article:
            result["success"] = True
            result["article_id"] = article.get("id")
            result["article_url"] = article.get("url")
            logger.info(f"知乎文章发布成功：{title}, url={result['article_url']}")
        else:
            result["error"] = "文章创建失败"
            logger.error(f"知乎文章发布失败：{title}")
        
        return result
    
    def create_zhuanlan_article(self, title: str, content: str,
                                 description: Optional[str] = None,
                                 cover_image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        发布专栏文章
        
        Args:
            title: 文章标题
            content: 文章内容
            description: 文章描述
            cover_image_url: 封面图片 URL
            
        Returns:
            发布结果
        """
        # 知乎专栏 API 路径
        result = {
            "success": False,
            "article_id": None,
            "article_url": None,
            "error": None
        }
        
        data = {
            "title": title,
            "content": content,
            "description": description or title
        }
        
        # 上传封面
        if cover_image_url:
            cover_token = self.upload_image(cover_image_url)
            if cover_token:
                data["cover_image"] = cover_token
        
        # 发布到专栏（需要专栏 ID）
        # 注意：这里需要替换为实际的专栏 ID
        zhuanlan_id = "your_zhuanlan_id"
        path = f"/zhuanlan/{zhuanlan_id}/articles"
        
        article = self._request("POST", path, data=data)
        
        if article:
            result["success"] = True
            result["article_id"] = article.get("id")
            result["article_url"] = article.get("url")
            logger.info(f"知乎专栏文章发布成功：{title}")
        else:
            result["error"] = "专栏文章发布失败"
            logger.error(f"知乎专栏文章发布失败：{title}")
        
        return result
    
    def create_thought(self, content: str, 
                       images: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        发布想法（类似朋友圈）
        
        Args:
            content: 想法内容
            images: 图片 URL 列表
            
        Returns:
            想法信息或 None
        """
        data = {
            "content": content
        }
        
        # 上传图片
        if images:
            image_tokens = []
            for img_url in images:
                token = self.upload_image(img_url)
                if token:
                    image_tokens.append(token)
            
            if image_tokens:
                data["images"] = image_tokens
        
        result = self._request("POST", "/thoughts", data=data)
        
        if result:
            logger.info(f"知乎想法发布成功：{result.get('id')}")
            return result
        else:
            logger.error("知乎想法发布失败")
            return None
    
    def get_article_info(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        获取文章信息
        
        Args:
            article_id: 文章 ID
            
        Returns:
            文章信息或 None
        """
        path = f"/articles/{article_id}"
        return self._request("GET", path)
    
    def update_article(self, article_id: str, title: Optional[str] = None,
                      content: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        更新文章
        
        Args:
            article_id: 文章 ID
            title: 新标题
            content: 新内容
            
        Returns:
            更新结果或 None
        """
        data = {}
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        
        path = f"/articles/{article_id}"
        return self._request("PUT", path, data=data)
    
    def delete_article(self, article_id: str) -> bool:
        """
        删除文章
        
        Args:
            article_id: 文章 ID
            
        Returns:
            是否成功
        """
        path = f"/articles/{article_id}"
        result = self._request("DELETE", path)
        return result is not None
