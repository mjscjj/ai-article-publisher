# V3 前端访问指南

> 创建时间：2026-03-02  
> 版本：v3.0.0

---

## 🌐 访问方式

### 方式一：直接访问 (当前可用)

直接在浏览器打开以下 URL：

| 页面 | URL | 说明 |
|------|-----|------|
| 🔥 热点中心 | `http://43.134.234.4:8000/frontend/v3_hotnews_center.html` | 实时热榜 |
| 🎯 智能选题 | `http://43.134.234.4:8000/frontend/v3_topic_intelligence.html` | 选题生成 |
| 📊 工作评价 | `http://43.134.234.4:8000/frontend/v3_evaluation.html` | DeepSeek V3 评价 |
| 🔍 工作 Review | `http://43.134.234.4:8000/frontend/v3_work_review.html` | 全面 Review |
| 📊 数据看板 | `http://43.134.234.4:8000/frontend/v3_data_dashboard.html` | 数据统计 |
| 👥 用户中心 | `http://43.134.234.4:8000/frontend/v3_user_center.html` | 用户管理 |

---

### 方式二：Nginx 统一入口 (推荐)

**步骤 1: 安装 Nginx**
```bash
# CentOS/OpenCloudOS
sudo yum install nginx -y

# Ubuntu/Debian
sudo apt install nginx -y
```

**步骤 2: 配置 Nginx**
```bash
sudo cp /root/.openclaw/workspace-writer/ai-article-publisher/deploy/nginx.conf /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl restart nginx
```

**步骤 3: 访问**
```
http://43.134.234.4/              # 首页
http://43.134.234.4/hotnews       # 热点中心
http://43.134.234.4/topics        # 智能选题
http://43.134.234.4/evaluation    # 工作评价
http://43.134.234.4/review        # 工作 Review
http://43.134.234.4/dashboard     # 数据看板
```

---

### 方式三：本地文件访问

```bash
# 直接用浏览器打开本地文件
file:///root/.openclaw/workspace-writer/ai-article-publisher/frontend/v3_hotnews_center.html
```

---

## 🔍 验证 API 连接

打开浏览器开发者工具 (F12)，检查 Network 标签：

```javascript
// 在浏览器控制台测试 API 连接
fetch('http://43.134.234.4:8000/api/v3/hotnews?limit=5')
  .then(r => r.json())
  .then(d => console.log('API 正常:', d))
  .catch(e => console.error('API 错误:', e))
```

---

## 🛠️ 故障排查

### 前端无法加载

```bash
# 1. 检查文件是否存在
ls -lh /root/.openclaw/workspace-writer/ai-article-publisher/frontend/*.html

# 2. 检查 API 服务
curl http://43.134.234.4:8000/health

# 3. 检查防火墙
firewall-cmd --list-ports
# 开放端口
firewall-cmd --add-port=8000-8008/tcp --permanent
firewall-cmd --reload
```

### API 无法连接

```bash
# 1. 检查服务状态
cd /root/.openclaw/workspace-writer/ai-article-publisher
./scripts/deploy_v3.sh status

# 2. 重启服务
./scripts/deploy_v3.sh restart

# 3. 查看日志
./scripts/deploy_v3.sh logs hotnews
```

---

## 📱 移动端适配

所有前端页面已适配移动端：
- ✅ 响应式设计
- ✅ 触摸友好
- ✅ 横竖屏自适应

---

## 🎨 前端特性

| 页面 | 技术栈 | 特性 |
|------|--------|------|
| 热点中心 | Vue3 + Tailwind | 实时刷新/筛选/订阅 |
| 智能选题 | Vue3 + Tailwind | 批量生成/5 维评分 |
| 工作评价 | Vue3 + Chart.js | 雷达图/DeepSeek V3 |
| 工作 Review | Vue3 + Chart.js | 全面评价/改进计划 |
| 数据看板 | Vue3 + ECharts | 多维度统计/趋势图 |
| 用户中心 | Vue3 + Tailwind | 登录/配置/权限 |

---

*所有前端页面均可直接访问，无需额外配置*
