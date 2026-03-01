"""
小红书发布模块
支持笔记发布（图文/视频）
"""
import requests
import time
import hashlib
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class XiaohongshuPublisher:
    """小红书发布器"""
    
    def __init__(self, access_token: str, user_id: str):
        """
        初始化小红书发布器
        
        Args:
            access_token: 小红书开放平台 access_token
            user_id: 用户 ID
        """
        self.access_token = access_token
        self.user_id = user_id
        self.base_url = "https://edith.xiaohongshu.com/api/sns/web/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Cookie": f"access_token={access_token}"
        }
    
    def _generate_sign(self, params: Dict) -> str:
        """
        生成签名（小红书需要签名验证）
        
        Args:
            params: 请求参数
            
        Returns:
            签名字符串
        """
        # 注意：实际签名算法需要根据小红书官方文档实现
        # 这里提供示例框架
        sorted_params = sorted(params.items())
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign = hashlib.md5(param_str.encode()).hexdigest()
        return sign
    
    def _request(self, method: str, path: str, data: Optional[Dict] = None,
                 params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """发送 HTTP 请求"""
        url = f"{self.base_url}{path}"
        
        # 添加签名
        if params:
            params["timestamp"] = int(time.time() * 1000)
            params["sign"] = self._generate_sign(params)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, params=params, timeout=30)
            else:
                logger.error(f"不支持的 HTTP 方法：{method}")
                return None
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") or result.get("code") == 0:
                    return result
                else:
                    logger.error(f"请求失败：{result}")
                    return None
            else:
                logger.error(f"请求失败：{response.status_code}, {response.text}")
                return None
        except Exception as e:
            logger.error(f"请求异常：{e}")
            return None
    
    def upload_image(self, image_url: str) -> Optional[str]:
        """
        上传图片
        
        Args:
            image_url: 图片 URL
            
        Returns:
            图片 ID 或 None
        """
        try:
            # 下载图片
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                logger.error(f"下载图片失败：{image_url}")
                return None
            
            image_data = response.content
            
            # 获取上传凭证
            upload_info = self._request("POST", "/media/upload_pre", data={
                "media_type": "image",
                "file_size": len(image_data),
                "file_name": "image.jpg"
            })
            
            if not upload_info:
                return None
            
            # 上传图片到 OSS
            upload_url = upload_info.get("upload_url")
            # 实际上传到 OSS 的逻辑...
            
            # 获取图片 ID
            image_id = upload_info.get("image_id")
            logger.info(f"图片上传成功：{image_id}")
            return image_id
            
        except Exception as e:
            logger.error(f"上传图片异常：{e}")
            return None
    
    def upload_video(self, video_url: str) -> Optional[str]:
        """
        上传视频
        
        Args:
            video_url: 视频 URL
            
        Returns:
            视频 ID 或 None
        """
        try:
            # 下载视频
            response = requests.get(video_url, timeout=30)
            if response.status_code != 200:
                logger.error(f"下载视频失败：{video_url}")
                return None
            
            video_data = response.content
            
            # 获取上传凭证
            upload_info = self._request("POST", "/media/upload_pre", data={
                "media_type": "video",
                "file_size": len(video_data),
                "file_name": "video.mp4"
            })
            
            if not upload_info:
                return None
            
            # 上传视频到 OSS
            # ...
            
            video_id = upload_info.get("video_id")
            logger.info(f"视频上传成功：{video_id}")
            return video_id
            
        except Exception as e:
            logger.error(f"上传视频异常：{e}")
            return None
    
    def publish_note(self, title: str, content: str,
                    image_urls: Optional[List[str]] = None,
                    video_url: Optional[str] = None,
                    topics: Optional[List[str]] = None,
                    tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        发布笔记
        
        Args:
            title: 标题
            content: 内容
            image_urls: 图片 URL 列表（最多 9 张）
            video_url: 视频 URL（与图片互斥）
            topics: 话题列表
            tags: 标签列表
            
        Returns:
            发布结果
        """
        result = {
            "success": False,
            "note_id": None,
            "note_url": None,
            "error": None
        }
        
        # 1. 上传媒体文件
        media_ids = []
        
        if video_url:
            # 视频笔记
            logger.info(f"上传视频：{video_url}")
            video_id = self.upload_video(video_url)
            if not video_id:
                result["error"] = "视频上传失败"
                return result
            media_ids.append(video_id)
            media_type = "video"
        elif image_urls:
            # 图文笔记
            logger.info(f"上传图片：{len(image_urls)} 张")
            for img_url in image_urls[:9]:  # 最多 9 张
                img_id = self.upload_image(img_url)
                if img_id:
                    media_ids.append(img_id)
            
            if not media_ids:
                result["error"] = "图片上传失败"
                return result
            media_type = "image"
        else:
            result["error"] = "必须提供图片或视频"
            return result
        
        # 2. 发布笔记
        data = {
            "title": title,
            "desc": content,
            "media_ids": media_ids,
            "media_type": media_type,
            "topics": topics or [],
            "tags": tags or []
        }
        
        logger.info(f"发布小红书笔记：{title}")
        publish_result = self._request("POST", "/note/publish", data=data)
        
        if publish_result:
            result["success"] = True
            result["note_id"] = publish_result.get("note_id")
            result["note_url"] = f"https://www.xiaohongshu.com/discovery/item/{result['note_id']}"
            logger.info(f"小红书笔记发布成功：{title}, id={result['note_id']}")
        else:
            result["error"] = "笔记发布失败"
            logger.error(f"小红书笔记发布失败：{title}")
        
        return result
    
    def update_note(self, note_id: str, title: Optional[str] = None,
                   content: Optional[str] = None,
                   image_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        更新笔记
        
        Args:
            note_id: 笔记 ID
            title: 新标题
            content: 新内容
            image_urls: 新图片列表
            
        Returns:
            更新结果
        """
        data = {
            "note_id": note_id
        }
        
        if title:
            data["title"] = title
        if content:
            data["desc"] = content
        
        # 如果需要更新图片，先上传新图片
        if image_urls:
            media_ids = []
            for img_url in image_urls[:9]:
                img_id = self.upload_image(img_url)
                if img_id:
                    media_ids.append(img_id)
            
            if media_ids:
                data["media_ids"] = media_ids
        
        result = self._request("POST", "/note/update", data=data)
        
        if result:
            logger.info(f"笔记更新成功：{note_id}")
            return {"success": True, "note_id": note_id}
        else:
            logger.error(f"笔记更新失败：{note_id}")
            return {"success": False, "error": "更新失败"}
    
    def delete_note(self, note_id: str) -> bool:
        """
        删除笔记
        
        Args:
            note_id: 笔记 ID
            
        Returns:
            是否成功
        """
        result = self._request("POST", "/note/delete", data={"note_id": note_id})
        return result is not None
    
    def get_note_info(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        获取笔记信息
        
        Args:
            note_id: 笔记 ID
            
        Returns:
            笔记信息或 None
        """
        return self._request("GET", f"/note/{note_id}")
    
    def get_user_notes(self, user_id: Optional[str] = None,
                      page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        获取用户笔记列表
        
        Args:
            user_id: 用户 ID（默认为当前用户）
            page: 页码
            page_size: 每页数量
            
        Returns:
            笔记列表
        """
        params = {
            "page": page,
            "page_size": page_size,
            "user_id": user_id or self.user_id
        }
        
        return self._request("GET", "/user/notes", params=params)
