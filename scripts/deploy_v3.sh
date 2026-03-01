#!/bin/bash
# V3 服务部署脚本
# 部署所有 V3 模块的 API 服务

set -e

echo "=========================================="
echo "🚀 V3 服务部署脚本"
echo "=========================================="

PROJECT_ROOT="/root/.openclaw/workspace-writer/ai-article-publisher"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# 创建目录
mkdir -p $LOG_DIR $PID_DIR

# 服务配置
declare -A SERVICES=(
    ["hotnews"]="api.v3.hotnews:8000"
    ["topics"]="api.v3.topics:8001"
    ["evaluation"]="api.v3.evaluation:8002"
    ["review"]="api.v3.review_api:8003"
    ["coordinator"]="api.v3.coordinator_api:8004"
    ["publish"]="api.v3.publish:8005"
    ["analytics"]="api.v3.analytics:8006"
    ["workflow"]="api.v3.workflow:8007"
    ["auth"]="api.v3.auth:8008"
)

# 停止所有服务
stop_all() {
    echo "🛑 停止所有服务..."
    for pid_file in $PID_DIR/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid"
                echo "  ✅ 停止服务 (PID: $pid)"
            fi
            rm "$pid_file"
        fi
    done
    echo "✅ 所有服务已停止"
}

# 启动单个服务
start_service() {
    local name=$1
    local module=$2
    local port=$3
    
    echo "🚀 启动 $name (端口：$port)..."
    
    cd $PROJECT_ROOT
    
    # 添加项目路径到 PYTHONPATH (包括父目录以访问 core.workflow)
    export PYTHONPATH="$PROJECT_ROOT:/root/.openclaw/workspace-writer:$PYTHONPATH"
    
    nohup python3 -m uvicorn $module:app \
        --host 0.0.0.0 \
        --port $port \
        > $LOG_DIR/${name}.log 2>&1 &
    
    echo $! > $PID_DIR/${name}.pid
    echo "  ✅ $name 已启动 (PID: $!)"
}

# 启动所有服务
start_all() {
    echo "🚀 启动所有服务..."
    
    for name in "${!SERVICES[@]}"; do
        config="${SERVICES[$name]}"
        module="${config%%:*}"
        port="${config##*:}"
        start_service "$name" "$module" "$port"
    done
    
    echo "=========================================="
    echo "✅ 所有服务已启动"
    echo "=========================================="
}

# 检查服务状态
check_status() {
    echo "📊 服务状态检查"
    echo "=========================================="
    
    for name in "${!SERVICES[@]}"; do
        config="${SERVICES[$name]}"
        port="${config##*:}"
        pid_file="$PID_DIR/${name}.pid"
        
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                # 检查端口
                if netstat -tuln 2>/dev/null | grep -q ":$port "; then
                    echo "✅ $name (端口:$port, PID:$pid) - 运行中"
                else
                    echo "⚠️  $name (端口:$port, PID:$pid) - 端口未监听"
                fi
            else
                echo "❌ $name (端口:$port) - 进程已停止"
            fi
        else
            echo "❌ $name (端口:$port) - 未启动"
        fi
    done
    
    echo "=========================================="
}

# 查看日志
view_logs() {
    local name=$1
    if [ -z "$name" ]; then
        echo "可用服务：${!SERVICES[@]}"
        read -p "输入服务名：" name
    fi
    
    if [ -f "$LOG_DIR/${name}.log" ]; then
        tail -f $LOG_DIR/${name}.log
    else
        echo "❌ 日志文件不存在"
    fi
}

# 主菜单
case "${1:-start}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs "$2"
        ;;
    *)
        echo "用法：$0 {start|stop|restart|status|logs [service_name]}"
        exit 1
        ;;
esac
