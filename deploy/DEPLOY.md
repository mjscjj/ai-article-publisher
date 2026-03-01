# V3 服务部署指南

> 创建时间：2026-03-02  
> 版本：v3.0.0  
> 状态：可部署

---

## 📋 部署方式

### 方式一：快速部署脚本 (推荐)

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher

# 1. 启动所有服务
./scripts/deploy_v3.sh start

# 2. 检查状态
./scripts/deploy_v3.sh status

# 3. 查看日志
./scripts/deploy_v3.sh logs hotnews

# 4. 停止服务
./scripts/deploy_v3.sh stop
```

### 方式二：Docker Compose 部署

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher/deploy

# 1. 启动所有服务
docker-compose up -d

# 2. 查看状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### 方式三：手动部署

```bash
cd /root/.openclaw/workspace-writer/ai-article-publisher

# 安装依赖
pip install -r requirements.txt

# 启动各个服务
nohup python3 -m uvicorn api.v3.hotnews:app --host 0.0.0.0 --port 8000 > logs/hotnews.log 2>&1 &
nohup python3 -m uvicorn api.v3.topics:app --host 0.0.0.0 --port 8000 > logs/topics.log 2>&1 &
nohup python3 -m uvicorn api.v3.evaluation:app --host 0.0.0.0 --port 8001 > logs/evaluation.log 2>&1 &
nohup python3 -m uvicorn api.v3.review_api:app --host 0.0.0.0 --port 8002 > logs/review.log 2>&1 &
nohup python3 -m uvicorn api.v3.coordinator_api:app --host 0.0.0.0 --port 8003 > logs/coordinator.log 2>&1 &
nohup python3 -m uvicorn api.v3.publish:app --host 0.0.0.0 --port 8004 > logs/publish.log 2>&1 &
nohup python3 -m uvicorn api.v3.analytics:app --host 0.0.0.0 --port 8005 > logs/analytics.log 2>&1 &
nohup python3 -m uvicorn api.v3.workflow:app --host 0.0.0.0 --port 8006 > logs/workflow.log 2>&1 &
nohup python3 -m uvicorn api.v3.auth:app --host 0.0.0.0 --port 8007 > logs/auth.log 2>&1 &
```

---

## 🌐 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| **热点中心** | 8000 | 热点数据 API |
| **智能选题** | 8001 | 选题生成 API |
| **工作评价** | 8002 | DeepSeek V3 评价 |
| **工作 Review** | 8003 | Review 系统 |
| **项目协调者** | 8004 | 协调者 API |
| **自动发布** | 8005 | 多平台发布 |
| **数据看板** | 8006 | 统计分析 |
| **工作流引擎** | 8007 | 工作流管理 |
| **用户认证** | 8008 | 认证授权 |
| **Nginx Gateway** | 80 | 统一入口 |
| **MySQL** | 3306 | 数据库 |
| **Redis** | 6379 | 缓存 |
| **AnythingLLM** | 3001 | AI Base |

---

## 🧪 健康检查

```bash
# 检查所有服务
curl http://43.134.234.4:8000/health
curl http://43.134.234.4:8001/health
curl http://43.134.234.4:8002/health
curl http://43.134.234.4:8003/health
curl http://43.134.234.4:8004/health
curl http://43.134.234.4:8005/health
curl http://43.134.234.4:8006/health
curl http://43.134.234.4:8007/health
curl http://43.134.234.4:8008/health

# 通过 Gateway 访问
curl http://43.134.234.4/api/v3/hotnews/health
```

---

## 📊 前端访问

**直接访问**:
- 热点中心：`http://43.134.234.4:8000/frontend/v3_hotnews_center.html`
- 智能选题：`http://43.134.234.4:8000/frontend/v3_topic_intelligence.html`
- 工作评价：`http://43.134.234.4:8000/frontend/v3_evaluation.html`
- 工作 Review: `http://43.134.234.4:8000/frontend/v3_work_review.html`
- 数据看板：`http://43.134.234.4:8000/frontend/v3_data_dashboard.html`
- 用户中心：`http://43.134.234.4:8000/frontend/v3_user_center.html`

**通过 Nginx**:
- 统一入口：`http://43.134.234.4/`

---

## 🔧 配置管理

### 数据库配置

```bash
export DB_HOST="43.134.234.4"
export DB_PORT="3306"
export DB_NAME="youmind"
export DB_USER="youmind"
export DB_PASSWORD="YouMind2026"
```

### AI Base 配置

```bash
export AI_BASE_URL="http://43.134.234.4:3001"
export AI_BASE_API_KEY="sk-WaUmgZsMxgeHOpp8SJxK1rmVQxiwfiDJ"
export AI_WORKSPACE="common"
```

### JWT 配置

```bash
export JWT_SECRET_KEY="your-secret-key-change-in-production"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRATION_HOURS="24"
```

---

## 📝 运维命令

### 日志管理

```bash
# 查看所有日志
tail -f logs/*.log

# 查看特定服务日志
tail -f logs/hotnews.log

# 清理旧日志
find logs/ -name "*.log" -mtime +7 -delete
```

### 进程管理

```bash
# 查看运行进程
ps aux | grep uvicorn

# 批量停止
pkill -f "uvicorn api.v3"

# 查看端口占用
netstat -tuln | grep 800
```

### 数据库管理

```bash
# 连接数据库
mysql -h 43.134.234.4 -u youmind -pYouMind2026 youmind

# 备份数据库
mysqldump -h 43.134.234.4 -u youmind -pYouMind2026 youmind > backup.sql

# 恢复数据库
mysql -h 43.134.234.4 -u youmind -pYouMind2026 youmind < backup.sql
```

---

## 🚨 故障排查

### 服务无法启动

```bash
# 检查端口占用
netstat -tuln | grep 8000

# 检查依赖
pip list | grep -E "fastapi|uvicorn|pymysql"

# 查看错误日志
tail -100 logs/hotnews.log
```

### 数据库连接失败

```bash
# 测试连接
mysql -h 43.134.234.4 -u youmind -pYouMind2026 -e "SELECT 1"

# 检查 MySQL 状态
systemctl status mysql

# 检查防火墙
ufw status | grep 3306
```

### API 响应慢

```bash
# 检查 CPU/内存
top -bn1 | head -20

# 检查慢查询
mysql -h 43.134.234.4 -u youmind -pYouMind2026 -e "SHOW PROCESSLIST"

# 检查 Redis
redis-cli -h 43.134.234.4 ping
```

---

## 📈 监控告警

### Prometheus + Grafana (可选)

```bash
# 安装 Prometheus
docker run -d -p 9090:9090 prom/prometheus

# 安装 Grafana
docker run -d -p 3000:3000 grafana/grafana
```

### 自定义监控脚本

```bash
#!/bin/bash
# monitor.sh - 服务监控

SERVICES=("hotnews" "topics" "evaluation" "review" "coordinator" "publish" "analytics" "workflow" "auth")

for service in "${SERVICES[@]}"; do
    pid_file="pids/${service}.pid"
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if ! kill -0 "$pid" 2>/dev/null; then
            echo "❌ $service 已停止，正在重启..."
            ./scripts/deploy_v3.sh restart
        fi
    fi
done
```

---

## ✅ 部署检查清单

- [ ] 安装 Python 依赖
- [ ] 配置数据库连接
- [ ] 配置 AI Base 连接
- [ ] 运行数据库迁移
- [ ] 启动所有服务
- [ ] 验证健康检查
- [ ] 测试 API 端点
- [ ] 测试前端页面
- [ ] 配置 Nginx (可选)
- [ ] 设置监控告警
- [ ] 备份配置

---

*部署完成后，所有 V3 服务将可通过 http://43.134.234.4 访问*
