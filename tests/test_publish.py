"""
发布模块测试
"""
import pytest
import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from core.publish.wechat_publisher import WechatPublisher
from core.publish.zhihu_publisher import ZhihuPublisher
from core.publish.xiaohongshu_publisher import XiaohongshuPublisher
from core.publish.publish_queue import (
    PublishQueue, PublishTask, TaskStatus, Platform
)


# ============ 微信公众号发布器测试 ============

class TestWechatPublisher:
    """微信公众号发布器测试"""
    
    @pytest.fixture
    def publisher(self):
        """创建测试用发布器"""
        return WechatPublisher(
            appid="test_appid",
            appsecret="test_secret"
        )
    
    @patch('core.publish.wechat_publisher.requests.get')
    def test_get_access_token_success(self, mock_get, publisher):
        """测试获取 access_token 成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 7200
        }
        mock_get.return_value = mock_response
        
        token = publisher._get_access_token()
        
        assert token == "test_token"
        assert publisher.access_token == "test_token"
    
    @patch('core.publish.wechat_publisher.requests.get')
    def test_get_access_token_failure(self, mock_get, publisher):
        """测试获取 access_token 失败"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "errcode": 40013,
            "errmsg": "invalid appid"
        }
        mock_get.return_value = mock_response
        
        token = publisher._get_access_token()
        
        assert token is None
    
    @patch('core.publish.wechat_publisher.requests.post')
    @patch('core.publish.wechat_publisher.WechatPublisher._get_access_token')
    def test_create_draft_success(self, mock_token, mock_post, publisher):
        """测试创建草稿成功"""
        mock_token.return_value = "test_token"
        
        mock_response = Mock()
        mock_response.json.return_value = {"media_id": "test_media_id"}
        mock_post.return_value = mock_response
        
        media_id = publisher.create_draft(
            title="测试标题",
            content="<p>测试内容</p>"
        )
        
        assert media_id == "test_media_id"
        mock_post.assert_called_once()
    
    @patch('core.publish.wechat_publisher.requests.post')
    @patch('core.publish.wechat_publisher.WechatPublisher._get_access_token')
    def test_publish_article_success(self, mock_token, mock_post, publisher):
        """测试发布文章成功"""
        mock_token.return_value = "test_token"
        
        # 模拟草稿创建和群发
        mock_response = Mock()
        mock_response.json.side_effect = [
            {"media_id": "draft_media_id"},  # 创建草稿
            {"errcode": 0, "errmsg": "ok", "msg_id": "123456"}  # 群发
        ]
        mock_post.return_value = mock_response
        
        result = publisher.publish_article(
            title="测试文章",
            content="<p>测试内容</p>"
        )
        
        assert result["success"] is True
        assert result["msg_id"] == "123456"


# ============ 知乎发布器测试 ============

class TestZhihuPublisher:
    """知乎发布器测试"""
    
    @pytest.fixture
    def publisher(self):
        """创建测试用发布器"""
        return ZhihuPublisher(access_token="test_token")
    
    @patch('core.publish.zhihu_publisher.requests.post')
    def test_create_article_success(self, mock_post, publisher):
        """测试创建文章成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "article_123",
            "url": "https://zhuanlan.zhihu.com/p/123"
        }
        mock_post.return_value = mock_response
        
        result = publisher.create_article(
            title="测试文章",
            content="# 测试内容"
        )
        
        assert result is not None
        assert result["id"] == "article_123"
    
    @patch('core.publish.zhihu_publisher.requests.get')
    @patch('core.publish.zhihu_publisher.requests.post')
    def test_publish_article_with_image(self, mock_post, mock_get, publisher):
        """测试发布带图片的文章"""
        # 模拟图片下载
        mock_image = Mock()
        mock_image.status_code = 200
        mock_image.content = b"fake_image_data"
        mock_get.return_value = mock_image
        
        # 模拟图片上传
        mock_upload = Mock()
        mock_upload.status_code = 200
        mock_upload.json.return_value = {"token": "image_token"}
        
        # 模拟文章创建
        mock_article = Mock()
        mock_article.status_code = 200
        mock_article.json.return_value = {
            "id": "article_456",
            "url": "https://zhuanlan.zhihu.com/p/456"
        }
        
        mock_post.side_effect = [mock_upload, mock_article]
        
        result = publisher.publish_article(
            title="带图文章",
            content="内容",
            cover_image_url="http://example.com/image.jpg"
        )
        
        assert result["success"] is True
        assert result["article_id"] == "article_456"


# ============ 小红书发布器测试 ============

class TestXiaohongshuPublisher:
    """小红书发布器测试"""
    
    @pytest.fixture
    def publisher(self):
        """创建测试用发布器"""
        return XiaohongshuPublisher(
            access_token="test_token",
            user_id="user_123"
        )
    
    def test_generate_sign(self, publisher):
        """测试签名生成"""
        params = {"a": "1", "b": "2"}
        sign = publisher._generate_sign(params)
        
        assert isinstance(sign, str)
        assert len(sign) == 32  # MD5 长度
    
    @patch('core.publish.xiaohongshu_publisher.requests.get')
    @patch('core.publish.xiaohongshu_publisher.XiaohongshuPublisher._request')
    def test_publish_note_success(self, mock_request, mock_get, publisher):
        """测试发布笔记成功"""
        # 模拟图片下载
        mock_image = Mock()
        mock_image.status_code = 200
        mock_image.content = b"fake_image"
        mock_get.return_value = mock_image
        
        # 模拟上传和发布
        mock_request.return_value = {
            "success": True,
            "note_id": "note_789"
        }
        
        result = publisher.publish_note(
            title="测试笔记",
            content="测试内容",
            image_urls=["http://example.com/img.jpg"]
        )
        
        assert result["success"] is True
        assert result["note_id"] == "note_789"


# ============ 发布队列测试 ============

class TestPublishQueue:
    """发布队列测试"""
    
    @pytest.fixture
    def queue(self, tmp_path):
        """创建测试用队列"""
        db_path = tmp_path / "test_queue.db"
        return PublishQueue(db_path=str(db_path))
    
    def test_add_task(self, queue):
        """测试添加任务"""
        task = PublishTask(
            id=str(uuid.uuid4()),
            platform="wechat",
            title="测试任务",
            content="测试内容"
        )
        
        task_id = queue.add_task(task)
        
        assert task_id == task.id
        
        # 验证任务可查询
        retrieved = queue.get_task(task_id)
        assert retrieved is not None
        assert retrieved.title == "测试任务"
    
    def test_get_pending_tasks(self, queue):
        """测试获取待处理任务"""
        # 添加多个任务
        for i in range(5):
            task = PublishTask(
                id=str(uuid.uuid4()),
                platform="wechat",
                title=f"任务{i}",
                content="内容"
            )
            queue.add_task(task)
        
        pending = queue.get_pending_tasks(limit=3)
        
        assert len(pending) == 3
        assert all(t.status == TaskStatus.PENDING.value for t in pending)
    
    def test_update_task_status(self, queue):
        """测试更新任务状态"""
        task = PublishTask(
            id=str(uuid.uuid4()),
            platform="wechat",
            title="测试",
            content="内容"
        )
        queue.add_task(task)
        
        # 更新状态
        queue.update_task_status(
            task.id,
            TaskStatus.SUCCESS,
            result={"msg_id": "123"}
        )
        
        updated = queue.get_task(task.id)
        assert updated.status == TaskStatus.SUCCESS.value
        assert updated.result["msg_id"] == "123"
    
    def test_increment_retry(self, queue):
        """测试重试计数"""
        task = PublishTask(
            id=str(uuid.uuid4()),
            platform="wechat",
            title="测试",
            content="内容",
            max_retries=3
        )
        queue.add_task(task)
        
        # 多次重试
        for i in range(3):
            count = queue.increment_retry(task.id)
            assert count == i + 1
        
        # 验证状态
        updated = queue.get_task(task.id)
        assert updated.retry_count == 3
        assert updated.status == TaskStatus.RETRYING.value
    
    def test_cancel_task(self, queue):
        """测试取消任务"""
        task = PublishTask(
            id=str(uuid.uuid4()),
            platform="wechat",
            title="测试",
            content="内容"
        )
        queue.add_task(task)
        
        # 取消任务
        success = queue.cancel_task(task.id)
        assert success is True
        
        # 验证状态
        updated = queue.get_task(task.id)
        assert updated.status == TaskStatus.CANCELLED.value
        
        # 已处理的任务不能取消
        queue.update_task_status(task.id, TaskStatus.SUCCESS)
        success = queue.cancel_task(task.id)
        assert success is False
    
    def test_get_history(self, queue):
        """测试获取历史记录"""
        # 添加多个任务
        for i in range(10):
            task = PublishTask(
                id=str(uuid.uuid4()),
                platform="wechat" if i % 2 == 0 else "zhihu",
                title=f"任务{i}",
                content="内容"
            )
            queue.add_task(task)
            queue.update_task_status(task.id, TaskStatus.SUCCESS)
        
        # 查询所有历史
        history = queue.get_history(limit=100)
        assert len(history) == 10
        
        # 按平台过滤
        wechat_history = queue.get_history(platform="wechat", limit=100)
        assert len(wechat_history) == 5
        
        # 按状态过滤
        success_history = queue.get_history(status=TaskStatus.SUCCESS, limit=100)
        assert len(success_history) == 10
    
    def test_get_statistics(self, queue):
        """测试获取统计数据"""
        # 添加不同平台和状态的任务
        platforms = ["wechat", "zhihu", "xiaohongshu"]
        statuses = [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.PENDING]
        
        for platform in platforms:
            for status in statuses:
                task = PublishTask(
                    id=str(uuid.uuid4()),
                    platform=platform,
                    title="测试",
                    content="内容",
                    status=status.value
                )
                queue.add_task(task)
        
        stats = queue.get_statistics()
        
        assert stats["total"] == 9
        assert len(stats["by_platform"]) == 3
        assert len(stats["by_status"]) == 3
    
    @patch('core.publish.publish_queue.WechatPublisher')
    def test_process_queue_success(self, mock_publisher_class, queue, tmp_path):
        """测试队列处理成功"""
        # 创建 Mock 发布器
        mock_publisher = Mock()
        mock_publisher.publish_article.return_value = {
            "success": True,
            "msg_id": "123"
        }
        queue.register_publisher("wechat", mock_publisher)
        
        # 添加任务
        task = PublishTask(
            id=str(uuid.uuid4()),
            platform="wechat",
            title="测试",
            content="内容"
        )
        queue.add_task(task)
        
        # 处理队列
        queue.process_queue()
        
        # 验证任务状态
        updated = queue.get_task(task.id)
        assert updated.status == TaskStatus.SUCCESS.value
        mock_publisher.publish_article.assert_called_once()
    
    @patch('core.publish.publish_queue.WechatPublisher')
    def test_process_queue_with_retry(self, mock_publisher_class, queue, tmp_path):
        """测试队列处理失败重试"""
        # 创建 Mock 发布器（总是失败）
        mock_publisher = Mock()
        mock_publisher.publish_article.side_effect = Exception("发布失败")
        queue.register_publisher("wechat", mock_publisher)
        
        # 添加任务（最多重试 2 次）
        task = PublishTask(
            id=str(uuid.uuid4()),
            platform="wechat",
            title="测试",
            content="内容",
            max_retries=2
        )
        queue.add_task(task)
        
        # 第一次处理
        queue.process_queue()
        updated = queue.get_task(task.id)
        assert updated.status == TaskStatus.RETRYING.value
        assert updated.retry_count == 1
        
        # 第二次处理
        queue.process_queue()
        updated = queue.get_task(task.id)
        assert updated.status == TaskStatus.RETRYING.value
        assert updated.retry_count == 2
        
        # 第三次处理（超过最大重试次数）
        queue.process_queue()
        updated = queue.get_task(task.id)
        assert updated.status == TaskStatus.FAILED.value
        assert updated.retry_count == 2
    
    def test_clear_completed(self, queue):
        """测试清理已完成记录"""
        # 添加已完成任务
        for i in range(5):
            task = PublishTask(
                id=str(uuid.uuid4()),
                platform="wechat",
                title=f"任务{i}",
                content="内容"
            )
            queue.add_task(task)
            queue.update_task_status(task.id, TaskStatus.SUCCESS)
        
        # 添加待处理任务
        pending_task = PublishTask(
            id=str(uuid.uuid4()),
            platform="wechat",
            title="待处理",
            content="内容"
        )
        queue.add_task(pending_task)
        
        # 清理（应该只清理已完成的）
        deleted = queue.clear_completed(days=0)
        
        assert deleted == 5
        
        # 验证待处理任务还在
        pending = queue.get_task(pending_task.id)
        assert pending is not None


# ============ 集成测试 ============

class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def setup_queue(self, tmp_path):
        """设置测试环境"""
        db_path = tmp_path / "test_queue.db"
        queue = PublishQueue(db_path=str(db_path))
        
        # 注册 Mock 发布器
        for platform in ["wechat", "zhihu", "xiaohongshu"]:
            mock_publisher = Mock()
            mock_publisher.publish_article.return_value = {
                "success": True,
                "id": f"{platform}_123"
            }
            queue.register_publisher(platform, mock_publisher)
        
        return queue
    
    def test_full_publish_workflow(self, setup_queue):
        """测试完整发布流程"""
        queue = setup_queue
        
        # 1. 提交发布任务
        task = PublishTask(
            id=str(uuid.uuid4()),
            platform="wechat",
            title="集成测试文章",
            content="这是测试内容",
            author="测试作者"
        )
        task_id = queue.add_task(task)
        
        # 2. 处理队列
        queue.process_queue()
        
        # 3. 验证结果
        result_task = queue.get_task(task_id)
        assert result_task.status == TaskStatus.SUCCESS.value
        assert result_task.result is not None
    
    def test_multi_platform_publish(self, setup_queue):
        """测试多平台发布"""
        queue = setup_queue
        
        # 提交多个平台任务
        task_ids = []
        for platform in ["wechat", "zhihu", "xiaohongshu"]:
            task = PublishTask(
                id=str(uuid.uuid4()),
                platform=platform,
                title=f"{platform}测试",
                content="内容"
            )
            task_ids.append(queue.add_task(task))
        
        # 处理所有任务
        queue.process_queue()
        
        # 验证所有任务成功
        for task_id in task_ids:
            task = queue.get_task(task_id)
            assert task.status == TaskStatus.SUCCESS.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
