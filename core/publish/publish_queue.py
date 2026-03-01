"""
发布队列管理模块
支持任务队列、失败重试、发布历史记录
"""
import json
import time
import sqlite3
import threading
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"      # 待处理
    PROCESSING = "processing"  # 处理中
    SUCCESS = "success"       # 成功
    FAILED = "failed"         # 失败
    RETRYING = "retrying"     # 重试中
    CANCELLED = "cancelled"   # 已取消


class Platform(Enum):
    """发布平台"""
    WECHAT = "wechat"
    ZHIHU = "zhihu"
    XIAOHONGSHU = "xiaohongshu"


@dataclass
class PublishTask:
    """发布任务"""
    id: str
    platform: str
    title: str
    content: str
    author: Optional[str] = None
    digest: Optional[str] = None
    thumb_image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    video_url: Optional[str] = None
    topics: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: str = TaskStatus.PENDING.value
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: str = ""
    updated_at: str = ""
    scheduled_at: Optional[str] = None
    published_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PublishTask":
        """从字典创建"""
        return cls(**data)


class PublishQueue:
    """发布队列管理器"""
    
    def __init__(self, db_path: str = "publish_queue.db"):
        """
        初始化发布队列
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.db_lock = threading.Lock()
        self._init_db()
        self._publishers = {}
        self._running = False
        self._worker_thread = None
    
    def _init_db(self):
        """初始化数据库"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT,
                    digest TEXT,
                    thumb_image_url TEXT,
                    image_urls TEXT,
                    video_url TEXT,
                    topics TEXT,
                    tags TEXT,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    error_message TEXT,
                    result TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    scheduled_at TEXT,
                    published_at TEXT
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform ON tasks(platform)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON tasks(created_at)')
            
            conn.commit()
            conn.close()
    
    def register_publisher(self, platform: str, publisher: Callable):
        """
        注册发布器
        
        Args:
            platform: 平台名称
            publisher: 发布器实例
        """
        self._publishers[platform] = publisher
        logger.info(f"注册发布器：{platform}")
    
    def add_task(self, task: PublishTask) -> str:
        """
        添加任务到队列
        
        Args:
            task: 发布任务
            
        Returns:
            任务 ID
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks (
                    id, platform, title, content, author, digest,
                    thumb_image_url, image_urls, video_url, topics, tags,
                    status, retry_count, max_retries, created_at, updated_at,
                    scheduled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.id, task.platform, task.title, task.content,
                task.author, task.digest, task.thumb_image_url,
                json.dumps(task.image_urls) if task.image_urls else None,
                task.video_url,
                json.dumps(task.topics) if task.topics else None,
                json.dumps(task.tags) if task.tags else None,
                task.status, task.retry_count, task.max_retries,
                task.created_at, task.updated_at, task.scheduled_at
            ))
            
            conn.commit()
            conn.close()
        
        logger.info(f"添加发布任务：{task.id}, platform={task.platform}, title={task.title}")
        return task.id
    
    def get_task(self, task_id: str) -> Optional[PublishTask]:
        """
        获取任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务或 None
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_task(row)
            return None
    
    def _row_to_task(self, row: tuple) -> PublishTask:
        """将数据库行转换为任务对象"""
        columns = [
            'id', 'platform', 'title', 'content', 'author', 'digest',
            'thumb_image_url', 'image_urls', 'video_url', 'topics', 'tags',
            'status', 'retry_count', 'max_retries', 'error_message', 'result',
            'created_at', 'updated_at', 'scheduled_at', 'published_at'
        ]
        
        data = dict(zip(columns, row))
        
        # 解析 JSON 字段
        for field in ['image_urls', 'topics', 'tags']:
            if data[field]:
                data[field] = json.loads(data[field])
        
        # 解析 result
        if data['result']:
            data['result'] = json.loads(data['result'])
        
        return PublishTask(**data)
    
    def get_pending_tasks(self, limit: int = 10) -> List[PublishTask]:
        """
        获取待处理任务（包括 pending 和 retrying 状态）
        
        Args:
            limit: 数量限制
            
        Returns:
            任务列表
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE status IN ('pending', 'retrying')
                AND (scheduled_at IS NULL OR scheduled_at <= ?)
                ORDER BY created_at ASC
                LIMIT ?
            ''', (now, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_task(row) for row in rows]
    
    def update_task_status(self, task_id: str, status: TaskStatus,
                          error_message: Optional[str] = None,
                          result: Optional[Dict[str, Any]] = None):
        """
        更新任务状态
        
        Args:
            task_id: 任务 ID
            status: 新状态
            error_message: 错误信息
            result: 发布结果
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updated_at = datetime.now().isoformat()
            
            updates = ["status = ?", "updated_at = ?"]
            params = [status.value, updated_at]
            
            if error_message is not None:
                updates.append("error_message = ?")
                params.append(error_message)
            
            if result is not None:
                updates.append("result = ?")
                params.append(json.dumps(result))
            
            if status == TaskStatus.SUCCESS:
                updates.append("published_at = ?")
                params.append(updated_at)
            
            params.append(task_id)
            
            cursor.execute(f'''
                UPDATE tasks SET {', '.join(updates)}
                WHERE id = ?
            ''', params)
            
            conn.commit()
            conn.close()
        
        logger.info(f"更新任务状态：{task_id}, status={status.value}")
    
    def increment_retry(self, task_id: str) -> int:
        """
        增加重试次数
        
        Args:
            task_id: 任务 ID
            
        Returns:
            当前重试次数
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks 
                SET retry_count = retry_count + 1,
                    status = 'retrying',
                    updated_at = ?
                WHERE id = ?
                RETURNING retry_count
            ''', (datetime.now().isoformat(), task_id))
            
            row = cursor.fetchone()
            conn.commit()
            conn.close()
            
            retry_count = row[0] if row else 0
            logger.info(f"任务重试：{task_id}, retry_count={retry_count}")
            return retry_count
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks 
                SET status = 'cancelled',
                    updated_at = ?
                WHERE id = ? AND status IN ('pending', 'retrying')
            ''', (datetime.now().isoformat(), task_id))
            
            affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if affected > 0:
                logger.info(f"取消任务：{task_id}")
                return True
            return False
    
    def get_history(self, platform: Optional[str] = None,
                   status: Optional[TaskStatus] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   limit: int = 100) -> List[PublishTask]:
        """
        获取发布历史
        
        Args:
            platform: 平台过滤
            status: 状态过滤
            start_date: 开始日期
            end_date: 结束日期
            limit: 数量限制
            
        Returns:
            任务列表
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM tasks WHERE 1=1"
            params = []
            
            if platform:
                query += " AND platform = ?"
                params.append(platform)
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if start_date:
                query += " AND created_at >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND created_at <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_task(row) for row in rows]
    
    def get_statistics(self, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取统计数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            统计数据
        """
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            base_query = "SELECT platform, status, COUNT(*) FROM tasks WHERE 1=1"
            params = []
            
            if start_date:
                base_query += " AND created_at >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                base_query += " AND created_at <= ?"
                params.append(end_date.isoformat())
            
            base_query += " GROUP BY platform, status"
            
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            conn.close()
            
            stats = {
                "total": 0,
                "by_platform": {},
                "by_status": {}
            }
            
            for platform, status, count in rows:
                stats["total"] += count
                
                if platform not in stats["by_platform"]:
                    stats["by_platform"][platform] = {}
                stats["by_platform"][platform][status] = count
                
                if status not in stats["by_status"]:
                    stats["by_status"][status] = 0
                stats["by_status"][status] += count
            
            return stats
    
    def _execute_task(self, task: PublishTask):
        """
        执行发布任务
        
        Args:
            task: 发布任务
        """
        publisher = self._publishers.get(task.platform)
        if not publisher:
            logger.error(f"未找到发布器：{task.platform}")
            self.update_task_status(
                task.id, TaskStatus.FAILED,
                error_message=f"未找到发布器：{task.platform}"
            )
            return
        
        try:
            logger.info(f"执行发布任务：{task.id}, platform={task.platform}")
            self.update_task_status(task.id, TaskStatus.PROCESSING)
            
            # 根据平台调用不同的发布方法
            if task.platform == Platform.WECHAT.value:
                result = publisher.publish_article(
                    title=task.title,
                    content=task.content,
                    author=task.author,
                    digest=task.digest,
                    thumb_image_url=task.thumb_image_url
                )
            elif task.platform == Platform.ZHIHU.value:
                result = publisher.publish_article(
                    title=task.title,
                    content=task.content,
                    topics=task.topics,
                    cover_image_url=task.thumb_image_url
                )
            elif task.platform == Platform.XIAOHONGSHU.value:
                result = publisher.publish_note(
                    title=task.title,
                    content=task.content,
                    image_urls=task.image_urls,
                    video_url=task.video_url,
                    topics=task.topics,
                    tags=task.tags
                )
            else:
                raise ValueError(f"不支持的平台：{task.platform}")
            
            # 处理结果
            if result.get("success"):
                self.update_task_status(
                    task.id, TaskStatus.SUCCESS,
                    result=result
                )
                logger.info(f"发布成功：{task.id}")
            else:
                raise Exception(result.get("error", "发布失败"))
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"发布失败：{task.id}, error={error_msg}")
            
            # 检查是否需要重试
            if task.retry_count < task.max_retries:
                retry_count = self.increment_retry(task.id)
                logger.info(f"任务将重试：{task.id}, retry={retry_count}/{task.max_retries}")
            else:
                self.update_task_status(
                    task.id, TaskStatus.FAILED,
                    error_message=error_msg
                )
    
    def process_queue(self):
        """处理队列中的任务"""
        pending_tasks = self.get_pending_tasks()
        
        for task in pending_tasks:
            self._execute_task(task)
    
    def start_worker(self, interval: int = 60):
        """
        启动后台工作线程
        
        Args:
            interval: 检查间隔（秒）
        """
        if self._running:
            logger.warning("工作线程已在运行")
            return
        
        self._running = True
        
        def worker():
            logger.info("发布队列工作线程启动")
            while self._running:
                try:
                    self.process_queue()
                except Exception as e:
                    logger.error(f"队列处理异常：{e}")
                
                time.sleep(interval)
        
        self._worker_thread = threading.Thread(target=worker, daemon=True)
        self._worker_thread.start()
    
    def stop_worker(self):
        """停止后台工作线程"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
            logger.info("发布队列工作线程停止")
    
    def clear_completed(self, days: int = 30):
        """
        清理已完成的历史记录
        
        Args:
            days: 保留天数
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM tasks 
                WHERE status IN ('success', 'cancelled', 'failed')
                AND created_at < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
        
        logger.info(f"清理历史记录：{deleted} 条")
        return deleted
