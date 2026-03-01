"""
微信公众号发布模块
支持草稿箱管理和群发功能
"""
import hashlib
import time
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WechatPublisher:
    """微信公众号发布器"""
    
    def __init__(self, appid: str, appsecret: str):
        """
        初始化微信公众号发布器
        
        Args:
            appid: 公众号 AppID
            appsecret: 公众号 AppSecret
        """
        self.appid = appid
        self.appsecret = appsecret
        self.access_token = None
        self.token_expires_at = 0
        self.base_url = "https://api.weixin.qq.com/cgi-bin"
    
    def _get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        url = f"{self.base_url}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.appsecret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                self.token_expires_at = time.time() + result.get("expires_in", 7200) - 300
                logger.info("微信公众号 access_token 获取成功")
                return self.access_token
            else:
                logger.error(f"获取 access_token 失败：{result}")
                return None
        except Exception as e:
            logger.error(f"获取 access_token 异常：{e}")
            return None
    
    def _upload_temporary_material(self, media_type: str, media_data: bytes) -> Optional[str]:
        """
        上传临时素材
        
        Args:
            media_type: 素材类型 (image, voice, video, thumb)
            media_data: 素材二进制数据
            
        Returns:
            media_id 或 None
        """
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        url = f"{self.base_url}/media/upload"
        params = {
            "access_token": access_token,
            "type": media_type
        }
        
        files = {"media": media_data}
        
        try:
            response = requests.post(url, params=params, files=files, timeout=30)
            result = response.json()
            
            if "media_id" in result:
                logger.info(f"临时素材上传成功：{result['media_id']}")
                return result["media_id"]
            else:
                logger.error(f"上传临时素材失败：{result}")
                return None
        except Exception as e:
            logger.error(f"上传临时素材异常：{e}")
            return None
    
    def _upload_permanent_material(self, media_type: str, media_data: bytes, 
                                    title: Optional[str] = None, 
                                    introduction: Optional[str] = None) -> Optional[str]:
        """
        上传永久素材
        
        Args:
            media_type: 素材类型
            media_data: 素材数据
            title: 标题（视频素材需要）
            introduction: 描述（视频素材需要）
            
        Returns:
            media_id 或 None
        """
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        url = f"{self.base_url}/material/add_material"
        params = {"access_token": access_token}
        
        if media_type == "video":
            # 视频需要先上传描述信息
            desc = {
                "title": title or "视频标题",
                "introduction": introduction or "视频描述"
            }
            files = {
                "description": (None, str(desc), "application/json"),
                "media": media_data
            }
        else:
            files = {"media": media_data}
        
        params["type"] = media_type
        
        try:
            response = requests.post(url, params=params, files=files, timeout=30)
            result = response.json()
            
            if "media_id" in result:
                logger.info(f"永久素材上传成功：{result['media_id']}")
                return result["media_id"]
            else:
                logger.error(f"上传永久素材失败：{result}")
                return None
        except Exception as e:
            logger.error(f"上传永久素材异常：{e}")
            return None
    
    def _upload_image_url(self, image_url: str) -> Optional[str]:
        """
        从 URL 上传图片
        
        Args:
            image_url: 图片 URL
            
        Returns:
            media_id 或 None
        """
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                return self._upload_permanent_material("image", response.content)
            else:
                logger.error(f"下载图片失败：{image_url}")
                return None
        except Exception as e:
            logger.error(f"下载图片异常：{e}")
            return None
    
    def create_draft(self, title: str, content: str, author: Optional[str] = None,
                     digest: Optional[str] = None, thumb_media_id: Optional[str] = None,
                     show_cover_pic: int = 1) -> Optional[str]:
        """
        创建草稿
        
        Args:
            title: 文章标题
            content: 文章内容（HTML 格式）
            author: 作者
            digest: 摘要
            thumb_media_id: 封面图片 media_id
            show_cover_pic: 是否显示封面 (0/1)
            
        Returns:
            media_id 或 None
        """
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        url = f"{self.base_url}/draft/add"
        params = {"access_token": access_token}
        
        articles = [{
            "title": title,
            "author": author or "",
            "digest": digest or "",
            "content": content,
            "content_source_url": "",
            "thumb_media_id": thumb_media_id or "",
            "show_cover_pic": show_cover_pic,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }]
        
        data = {
            "articles": articles
        }
        
        try:
            response = requests.post(url, params=params, json=data, timeout=30)
            result = response.json()
            
            if "media_id" in result:
                logger.info(f"草稿创建成功：{result['media_id']}")
                return result["media_id"]
            else:
                logger.error(f"创建草稿失败：{result}")
                return None
        except Exception as e:
            logger.error(f"创建草稿异常：{e}")
            return None
    
    def publish(self, media_id: str, send_to_all: bool = True, 
                tag_id: Optional[int] = None,
                client_msg_id: Optional[str] = None) -> Dict[str, Any]:
        """
        群发消息
        
        Args:
            media_id: 草稿 media_id
            send_to_all: 是否发送给所有用户
            tag_id: 标签 ID（按标签群发时使用）
            client_msg_id: 消息 ID（用于去重）
            
        Returns:
            发布结果 {"errcode": 0, "errmsg": "ok", "msg_id": "xxx"}
        """
        access_token = self._get_access_token()
        if not access_token:
            return {"errcode": -1, "errmsg": "获取 access_token 失败"}
        
        url = f"{self.base_url}/message/mass/sendall" if send_to_all else f"{self.base_url}/message/mass/send"
        params = {"access_token": access_token}
        
        if send_to_all:
            data = {
                "filter": {
                    "is_to_all": True
                },
                "mpnews": {
                    "media_ids": [media_id]
                },
                "msgtype": "mpnews",
                "send_ignore_reprint": 0
            }
        else:
            data = {
                "to_user": [],
                "mpnews": {
                    "media_ids": [media_id]
                },
                "msgtype": "mpnews",
                "send_ignore_reprint": 0
            }
        
        if client_msg_id:
            data["client_msg_id"] = client_msg_id
        
        try:
            response = requests.post(url, params=params, json=data, timeout=30)
            result = response.json()
            
            if result.get("errcode") == 0:
                logger.info(f"消息群发成功：msg_id={result.get('msg_id')}")
            else:
                logger.error(f"消息群发失败：{result}")
            
            return result
        except Exception as e:
            logger.error(f"消息群发异常：{e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    def publish_article(self, title: str, content: str, author: Optional[str] = None,
                       digest: Optional[str] = None, thumb_image_url: Optional[str] = None,
                       send_to_all: bool = True) -> Dict[str, Any]:
        """
        发布文章（完整流程：上传封面→创建草稿→群发）
        
        Args:
            title: 文章标题
            content: 文章内容
            author: 作者
            digest: 摘要
            thumb_image_url: 封面图片 URL
            send_to_all: 是否群发给所有用户
            
        Returns:
            发布结果
        """
        result = {
            "success": False,
            "media_id": None,
            "msg_id": None,
            "error": None
        }
        
        # 1. 上传封面图片
        thumb_media_id = None
        if thumb_image_url:
            logger.info(f"上传封面图片：{thumb_image_url}")
            thumb_media_id = self._upload_image_url(thumb_image_url)
            if not thumb_media_id:
                result["error"] = "封面图片上传失败"
                return result
        
        # 2. 创建草稿
        logger.info(f"创建草稿：{title}")
        media_id = self.create_draft(
            title=title,
            content=content,
            author=author,
            digest=digest,
            thumb_media_id=thumb_media_id
        )
        
        if not media_id:
            result["error"] = "草稿创建失败"
            return result
        
        result["media_id"] = media_id
        
        # 3. 群发消息
        logger.info(f"群发消息：{media_id}")
        publish_result = self.publish(media_id, send_to_all=send_to_all)
        
        if publish_result.get("errcode") == 0:
            result["success"] = True
            result["msg_id"] = publish_result.get("msg_id")
            logger.info(f"文章发布成功：{title}, msg_id={result['msg_id']}")
        else:
            result["error"] = publish_result.get("errmsg", "发布失败")
            logger.error(f"文章发布失败：{title}, {result['error']}")
        
        return result
    
    def get_draft_list(self, offset: int = 0, count: int = 20) -> Dict[str, Any]:
        """
        获取草稿列表
        
        Args:
            offset: 偏移量
            count: 数量（最多 20）
            
        Returns:
            草稿列表
        """
        access_token = self._get_access_token()
        if not access_token:
            return {"errcode": -1, "errmsg": "获取 access_token 失败"}
        
        url = f"{self.base_url}/draft/batchget"
        params = {"access_token": access_token}
        
        data = {
            "offset": offset,
            "count": min(count, 20)
        }
        
        try:
            response = requests.post(url, params=params, json=data, timeout=30)
            result = response.json()
            return result
        except Exception as e:
            logger.error(f"获取草稿列表异常：{e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    def delete_draft(self, media_id: str) -> Dict[str, Any]:
        """
        删除草稿
        
        Args:
            media_id: 草稿 media_id
            
        Returns:
            删除结果
        """
        access_token = self._get_access_token()
        if not access_token:
            return {"errcode": -1, "errmsg": "获取 access_token 失败"}
        
        url = f"{self.base_url}/draft/delete"
        params = {
            "access_token": access_token,
            "media_id": media_id
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            result = response.json()
            return result
        except Exception as e:
            logger.error(f"删除草稿异常：{e}")
            return {"errcode": -1, "errmsg": str(e)}
