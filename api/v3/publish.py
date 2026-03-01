"""
发布 API 接口
提供多平台发布功能的 RESTful API
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

from core.publish.wechat_publisher import WechatPublisher
from core.publish.zhihu_publisher import ZhihuPublisher
from core.publish.xiaohongshu_publisher import XiaohongshuPublisher
from core.publish.publish_queue import (
    PublishQueue, PublishTask, TaskStatus, Platform
)

logger = logging.getLogger(__name__)

# 路由器
router = APIRouter()

# 全局发布队列实例
_publish_queue: Optional[PublishQueue] = None
_publishers: Dict[str, Any] = {}


def get_publish_queue() -> PublishQueue:
    """获取发布队列实例"""
    global _publish_queue
    if _publish_queue is None:
        _publish_queue = PublishQueue()
        
        # 初始化发布器（从配置加载）
        # TODO: 从配置文件或环境变量加载凭据
        init_publishers(_publish_queue)
    
    return _publish_queue


def init_publishers(queue: PublishQueue):
    """初始化发布器"""
    # 微信公众号
    try:
        wechat_appid = "wx1c5d2d28dc97fc3f"
        wechat_secret = "16721c74fc595e4545b0a8745a51f41b"
        wechat_publisher = WechatPublisher(wechat_appid, wechat_secret)
        queue.register_publisher(Platform.WECHAT.value, wechat_publisher)
        _publishers[Platform.WECHAT.value] = wechat_publisher
    except Exception as e:
        logger.error(f"初始化微信公众号发布器失败：{e}")
    
    # 知乎
    try:
        zhihu_token = ""  # TODO: 从配置加载
        if zhihu_token:
            zhihu_publisher = ZhihuPublisher(zhihu_token)
            queue.register_publisher(Platform.ZHIHU.value, zhihu_publisher)
            _publishers[Platform.ZHIHU.value] = zhihu_publisher
    except Exception as e:
        logger.error(f"初始化知乎发布器失败：{e}")
    
    # 小红书
    try:
        xhs_token = ""  # TODO: 从配置加载
        xhs_user_id = ""  # TODO: 从配置加载
        if xhs_token and xhs_user_id:
            xhs_publisher = XiaohongshuPublisher(xhs_token, xhs_user_id)
            queue.register_publisher(Platform.XIAOHONGSHU.value, xhs_publisher)
            _publishers[Platform.XIAOHONGSHU.value] = xhs_publisher
    except Exception as e:
        logger.error(f"初始化小红书发布器失败：{e}")


# ============ 请求/响应模型 ============

class PublishRequest(BaseModel):
    """发布请求"""
    platform: str = Field(..., description="发布平台：wechat, zhihu, xiaohongshu")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    author: Optional[str] = Field(None, description="作者")
    digest: Optional[str] = Field(None, description="摘要")
    thumb_image_url: Optional[str] = Field(None, description="封面图片 URL")
    image_urls: Optional[List[str]] = Field(None, description="图片 URL 列表")
    video_url: Optional[str] = Field(None, description="视频 URL")
    topics: Optional[List[str]] = Field(None, description="话题列表")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    scheduled_at: Optional[str] = Field(None, description="定时发布时间")


class PublishResponse(BaseModel):
    """发布响应"""
    success: bool
    task_id: Optional[str] = None
    message: str
    result: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """任务详情响应"""
    task_id: str
    platform: str
    title: str
    status: str
    retry_count: int
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: str
    published_at: Optional[str] = None


class HistoryResponse(BaseModel):
    """历史记录响应"""
    tasks: List[TaskResponse]
    total: int


class StatisticsResponse(BaseModel):
    """统计信息响应"""
    total: int
    by_platform: Dict[str, Dict[str, int]]
    by_status: Dict[str, int]


# ============ API 接口 ============

@router.post("/submit", response_model=PublishResponse, summary="提交发布任务")
async def submit_publish_task(
    request: PublishRequest,
    background_tasks: BackgroundTasks,
    queue: PublishQueue = Depends(get_publish_queue)
):
    """
    提交发布任务到队列
    
    - **platform**: 发布平台 (wechat/zhihu/xiaohongshu)
    - **title**: 文章/笔记标题
    - **content**: 内容（支持 Markdown/HTML）
    - **thumb_image_url**: 封面图片 URL
    - **image_urls**: 图片列表（小红书用）
    - **video_url**: 视频 URL（小红书用）
    - **topics**: 话题标签
    - **scheduled_at**: 定时发布时间（ISO 格式）
    """
    # 验证平台
    try:
        platform = Platform(request.platform.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的平台：{request.platform}。支持：wechat, zhihu, xiaohongshu"
        )
    
    # 创建任务
    task = PublishTask(
        id=str(uuid.uuid4()),
        platform=platform.value,
        title=request.title,
        content=request.content,
        author=request.author,
        digest=request.digest,
        thumb_image_url=request.thumb_image_url,
        image_urls=request.image_urls,
        video_url=request.video_url,
        topics=request.topics,
        tags=request.tags,
        scheduled_at=request.scheduled_at
    )
    
    # 添加到队列
    task_id = queue.add_task(task)
    
    return PublishResponse(
        success=True,
        task_id=task_id,
        message="发布任务已提交",
        result={"platform": platform.value, "title": request.title}
    )


@router.post("/publish/{platform}", response_model=PublishResponse, summary="立即发布")
async def publish_now(
    platform: str,
    request: PublishRequest,
    queue: PublishQueue = Depends(get_publish_queue)
):
    """
    立即发布到指定平台（同步执行）
    
    适用于需要立即获取发布结果的场景
    """
    # 验证平台
    try:
        plat = Platform(platform.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的平台：{platform}"
        )
    
    # 获取发布器
    publisher = _publishers.get(plat.value)
    if not publisher:
        raise HTTPException(
            status_code=500,
            detail=f"发布器未初始化：{platform}"
        )
    
    # 执行发布
    try:
        if plat == Platform.WECHAT:
            result = publisher.publish_article(
                title=request.title,
                content=request.content,
                author=request.author,
                digest=request.digest,
                thumb_image_url=request.thumb_image_url
            )
        elif plat == Platform.ZHIHU:
            result = publisher.publish_article(
                title=request.title,
                content=request.content,
                topics=request.topics,
                cover_image_url=request.thumb_image_url
            )
        elif plat == Platform.XIAOHONGSHU:
            result = publisher.publish_note(
                title=request.title,
                content=request.content,
                image_urls=request.image_urls,
                video_url=request.video_url,
                topics=request.topics,
                tags=request.tags
            )
        else:
            raise ValueError(f"不支持的平台：{platform}")
        
        if result.get("success"):
            return PublishResponse(
                success=True,
                message="发布成功",
                result=result
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "发布失败")
            )
    
    except Exception as e:
        logger.error(f"发布失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}", response_model=TaskResponse, summary="查询任务状态")
async def get_task_status(
    task_id: str,
    queue: PublishQueue = Depends(get_publish_queue)
):
    """查询发布任务状态"""
    task = queue.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return TaskResponse(
        task_id=task.id,
        platform=task.platform,
        title=task.title,
        status=task.status,
        retry_count=task.retry_count,
        error_message=task.error_message,
        result=task.result,
        created_at=task.created_at,
        published_at=task.published_at
    )


@router.post("/task/{task_id}/cancel", response_model=PublishResponse, summary="取消任务")
async def cancel_task(
    task_id: str,
    queue: PublishQueue = Depends(get_publish_queue)
):
    """取消待发布的任务"""
    task = queue.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status not in [TaskStatus.PENDING.value, TaskStatus.RETRYING.value]:
        raise HTTPException(
            status_code=400,
            detail=f"无法取消任务，当前状态：{task.status}"
        )
    
    success = queue.cancel_task(task_id)
    
    if success:
        return PublishResponse(
            success=True,
            message="任务已取消"
        )
    else:
        raise HTTPException(status_code=500, detail="取消失败")


@router.get("/history", response_model=HistoryResponse, summary="查询发布历史")
async def get_publish_history(
    platform: Optional[str] = Query(None, description="平台过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    limit: int = Query(100, ge=1, le=500, description="数量限制"),
    queue: PublishQueue = Depends(get_publish_queue)
):
    """查询发布历史记录"""
    # 解析状态
    task_status = None
    if status:
        try:
            task_status = TaskStatus(status.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的状态：{status}"
            )
    
    # 查询历史
    tasks = queue.get_history(
        platform=platform,
        status=task_status,
        limit=limit
    )
    
    return HistoryResponse(
        tasks=[
            TaskResponse(
                task_id=task.id,
                platform=task.platform,
                title=task.title,
                status=task.status,
                retry_count=task.retry_count,
                error_message=task.error_message,
                result=task.result,
                created_at=task.created_at,
                published_at=task.published_at
            )
            for task in tasks
        ],
        total=len(tasks)
    )


@router.get("/statistics", response_model=StatisticsResponse, summary="统计信息")
async def get_statistics(
    queue: PublishQueue = Depends(get_publish_queue)
):
    """获取发布统计信息"""
    stats = queue.get_statistics()
    return StatisticsResponse(**stats)


@router.post("/queue/process", response_model=PublishResponse, summary="手动处理队列")
async def process_queue(
    queue: PublishQueue = Depends(get_publish_queue)
):
    """手动触发队列处理"""
    try:
        queue.process_queue()
        return PublishResponse(
            success=True,
            message="队列处理完成"
        )
    except Exception as e:
        logger.error(f"队列处理失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue/start", response_model=PublishResponse, summary="启动后台处理")
async def start_queue_worker(
    interval: int = Query(60, ge=10, description="检查间隔（秒）"),
    queue: PublishQueue = Depends(get_publish_queue)
):
    """启动后台队列处理线程"""
    try:
        queue.start_worker(interval=interval)
        return PublishResponse(
            success=True,
            message=f"队列工作线程已启动，检查间隔：{interval}秒"
        )
    except Exception as e:
        logger.error(f"启动工作线程失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue/stop", response_model=PublishResponse, summary="停止后台处理")
async def stop_queue_worker(
    queue: PublishQueue = Depends(get_publish_queue)
):
    """停止后台队列处理线程"""
    try:
        queue.stop_worker()
        return PublishResponse(
            success=True,
            message="队列工作线程已停止"
        )
    except Exception as e:
        logger.error(f"停止工作线程失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/cleanup", response_model=PublishResponse, summary="清理历史记录")
async def cleanup_history(
    days: int = Query(30, ge=1, description="保留天数"),
    queue: PublishQueue = Depends(get_publish_queue)
):
    """清理指定天数之前的已完成历史记录"""
    try:
        deleted = queue.clear_completed(days=days)
        return PublishResponse(
            success=True,
            message=f"已清理 {deleted} 条历史记录"
        )
    except Exception as e:
        logger.error(f"清理历史记录失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platforms", response_model=Dict[str, bool], summary="可用平台列表")
async def get_available_platforms():
    """获取可用的发布平台列表"""
    return {
        Platform.WECHAT.value: Platform.WECHAT.value in _publishers,
        Platform.ZHIHU.value: Platform.ZHIHU.value in _publishers,
        Platform.XIAOHONGSHU.value: Platform.XIAOHONGSHU.value in _publishers
    }


# ============================================
# 健康检查
# ============================================

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "Publish Service",
        "version": "3.0.0"
    }
