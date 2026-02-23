#!/usr/bin/env python3
"""
API 服务器 - 为前后端提供 RESTful 接口
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# 添加项目路径
sys.path.insert(0, '/root/.openclaw/workspace-writer/ai-article-publisher')

# 导入项目模块
from sources.unified_collector import main as collect_hotspots
from data_store import get_store
import topic_selector
import reviewer

# 配置
PORT = 8899
HOST = '0.0.0.0'

class APIHandler(BaseHTTPRequestHandler):
    """API 请求处理器"""
    
    def _send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        
    def _get_params(self):
        """获取 URL 参数"""
        parsed = urlparse(self.path)
        return parse_qs(parsed.query)
        
    def do_GET(self):
        """处理 GET 请求"""
        path = urlparse(self.path).path
        
        # 健康检查
        if path == '/health':
            self._send_json({'status': 'ok', 'service': 'ai-article-publisher-api'})
            return
            
        # 获取热点
        if path == '/api/hotspots':
            store = get_store()
            params = self._get_params()
            limit = int(params.get('limit', [50])[0])
            source = params.get('source', [None])[0]
            
            if source:
                hotspots = store.get_hotspots(limit=limit, source=source)
            else:
                hotspots = store.get_hotspots(limit=limit)
                
            self._send_json({
                'code': 0,
                'data': hotspots,
                'total': len(hotspots)
            })
            return
            
        # 获取选题
        if path == '/api/topics':
            store = get_store()
            hotspots = store.get_hotspots(limit=50)
            params = self._get_params()
            keywords = params.get('keywords', ['AI', '技术'])[0].split(',')
            top_n = int(params.get('top_n', [5])[0])
            
            topics = topic_selector.select_topics(hotspots, keywords=keywords, top_n=top_n)
            self._send_json({
                'code': 0,
                'data': topics
            })
            return
            
        # 获取文章列表
        if path == '/api/articles':
            store = get_store()
            params = self._get_params()
            status = params.get('status', [None])[0]
            limit = int(params.get('limit', [20])[0])
            
            articles = store.get_articles(status=status, limit=limit)
            self._send_json({
                'code': 0,
                'data': articles,
                'total': len(articles)
            })
            return
            
        # 获取单篇文章
        if path.startswith('/api/article/'):
            article_id = int(path.split('/')[-1])
            store = get_store()
            article = store.get_article(article_id)
            
            if article:
                self._send_json({
                    'code': 0,
                    'data': article
                })
            else:
                self._send_json({
                    'code': 404,
                    'message': 'Article not found'
                }, 404)
            return
            
        # 获取配置
        if path == '/api/config':
            store = get_store()
            config = store.get_config('pipeline_config')
            self._send_json({
                'code': 0,
                'data': config or {}
            })
            return
            
        # 获取任务状态
        if path == '/api/tasks':
            store = get_store()
            params = self._get_params()
            task_type = params.get('type', [None])[0]
            
            tasks = store.get_pending_tasks(task_type=task_type)
            self._send_json({
                'code': 0,
                'data': tasks
            })
            return
            
        # 默认 404
        self._send_json({
            'code': 404,
            'message': 'Not found'
        }, 404)
        
    def do_POST(self):
        """处理 POST 请求"""
        path = urlparse(self.path).path
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
            
        # 采集热点
        if path == '/api/collect':
            store = get_store()
            # 运行采集
            from sources.unified_collector import main as collect_main
            collect_main()
            
            self._send_json({
                'code': 0,
                'message': 'Collection completed'
            })
            return
            
        # 生成文章
        if path == '/api/generate':
            store = get_store()
            topic_id = data.get('topic_id')
            style = data.get('style', '技术干货')
            
            # 获取选题
            topics = store.get_hotspots(limit=10)
            topic = topics[topic_id - 1] if topic_id and topic_id <= len(topics) else topics[0]
            
            # 生成文章内容 (Mock 实现)
            content = f"# {topic['title']}\n\n这是根据热点「{topic['title']}」生成的测试文章内容。\n\n## 正文\n\n{topic.get('description', '')}"
            
            # 保存文章
            article_id = store.save_article(
                title=topic['title'],
                content=content,
                topic_id=topic.get('id'),
                status='draft'
            )
            
            self._send_json({
                'code': 0,
                'data': {
                    'article_id': article_id,
                    'title': topic['title'],
                    'content': content
                }
            })
            return
            
        # 审查文章
        if path == '/api/review':
            store = get_store()
            article_id = data.get('article_id')
            
            article = store.get_article(article_id)
            if not article:
                self._send_json({'code': 404, 'message': 'Article not found'}, 404)
                return
                
            # 审查
            review_result = reviewer.review_article(article['content'])
            
            # 更新文章
            store.update_article(
                article_id,
                review_result=json.dumps(review_result),
                quality_score=review_result['quality']['score']
            )
            
            self._send_json({
                'code': 0,
                'data': review_result
            })
            return
            
        # 发布文章
        if path == '/api/publish':
            store = get_store()
            article_id = data.get('article_id')
            
            article = store.get_article(article_id)
            if not article:
                self._send_json({'code': 404, 'message': 'Article not found'}, 404)
                return
                
            # 更新状态
            store.update_article(article_id, status='published')
            
            self._send_json({
                'code': 0,
                'message': 'Article published successfully'
            })
            return
            
        # 保存配置
        if path == '/api/config':
            store = get_store()
            key = data.get('key')
            value = data.get('value')
            
            if key and value:
                store.save_config(key, value)
                self._send_json({
                    'code': 0,
                    'message': 'Config saved'
                })
            else:
                self._send_json({
                    'code': 400,
                    'message': 'Invalid config data'
                }, 400)
            return
            
        # 默认 404
        self._send_json({
            'code': 404,
            'message': 'Not found'
        }, 404)
        
    def log_message(self, format, *args):
        """日志"""
        print(f"[API] {args[0]}")


def start_server():
    """启动 API 服务器"""
    server = HTTPServer((HOST, PORT), APIHandler)
    print(f"\n🚀 API 服务器已启动: http://{HOST}:{PORT}")
    print(f"📋 可用接口:")
    print(f"  GET  /api/hotspots - 获取热点列表")
    print(f"  GET  /api/topics - 获取选题")
    print(f"  GET  /api/articles - 获取文章列表")
    print(f"  GET  /api/article/{id} - 获取单篇文章")
    print(f"  POST /api/collect - 采集热点")
    print(f"  POST /api/generate - 生成文章")
    print(f"  POST /api/review - 审查文章")
    print(f"  POST /api/publish - 发布文章")
    print(f"  GET  /health - 健康检查")
    print("="*60 + "\n")
    
    server.serve_forever()


if __name__ == '__main__':
    start_server()
