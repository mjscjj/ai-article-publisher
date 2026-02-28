#!/bin/bash
# 热点展示系统启动脚本

echo "======================================"
echo "🔥 热点展示系统启动"
echo "======================================"

# 检查 Python 依赖
echo ""
echo "Step 1: 检查 Python 依赖..."

if ! python3 -c "import pymysql" 2>/dev/null; then
    echo "⚠️  安装 pymysql..."
    pip3 install pymysql
fi

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  安装 FastAPI..."
    pip3 install fastapi uvicorn
fi

echo "✅ Python 依赖检查完成"

# 启动 API 服务
echo ""
echo "Step 2: 启动 API 服务..."
echo "    地址：http://43.134.234.4:8080"
echo "    文档：http://43.134.234.4:8080/docs"

cd /root/.openclaw/workspace-writer/ai-article-publisher

# 后台启动 API
nohup python3 -m uvicorn api.hot_news_api:app \
    --host 0.0.0.0 \
    --port 8080 \
    --reload \
    > /tmp/hot_news_api.log 2>&1 &

API_PID=$!
echo "✅ API 服务已启动 (PID: $API_PID)"

# 等待 API 启动
sleep 3

# 检查 API 状态
if curl -s http://localhost:8080/ > /dev/null; then
    echo "✅ API 服务运行正常"
else
    echo "⚠️  API 服务可能启动失败，请查看日志：/tmp/hot_news_api.log"
fi

# 显示前端地址
echo ""
echo "======================================"
echo "📺 前端访问地址"
echo "======================================"
echo "    文件：/root/.openclaw/workspace-writer/ai-article-publisher/frontend/hot-news-dashboard.html"
echo ""
echo "    方式 1: 直接用浏览器打开文件"
echo "    方式 2: 使用 Python 简单 HTTP 服务器:"
echo "            cd frontend && python3 -m http.server 3000"
echo "            然后访问：http://43.134.234.4:3000/hot-news-dashboard.html"
echo ""

# 显示 API 测试命令
echo "======================================"
echo "🧪 API 测试命令"
echo "======================================"
echo ""
echo "# 获取热点列表"
echo "curl http://43.134.234.4:8080/api/topics"
echo ""
echo "# 获取统计数据"
echo "curl http://43.134.234.4:8080/api/statistics"
echo ""
echo "# 获取数据源"
echo "curl http://43.134.234.4:8080/api/sources"
echo ""
echo "# 获取热门关键词"
echo "curl http://43.134.234.4:8080/api/keywords"
echo ""

echo "======================================"
echo "✅ 启动完成"
echo "======================================"
echo ""
echo "日志文件：/tmp/hot_news_api.log"
echo "停止服务：kill $API_PID"
echo ""
