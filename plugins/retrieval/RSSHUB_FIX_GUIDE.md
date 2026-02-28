# RSSHub 修复指南

> **时间**: 2026-02-26 22:45 UTC+8
> **状态**: 容器已重启，待配置 Cookie

---

## 🚀 已执行操作

```bash
# 1. 删除旧容器
docker stop rsshub && docker rm rsshub

# 2. 重新部署
docker run -d --name rsshub \
  -p 1200:1200 \
  -e TZ=Asia/Shanghai \
  -e NODE_ENV=production \
  --restart=always \
  diygod/rsshub:latest
```

---

## ⚠️ 需要配置的 Cookie

### 1. 什么值得买 (SMZDM)

**获取方法**:
1. 浏览器访问 https://www.smzdm.com/
2. 登录账号
3. F12 打开开发者工具 → Network 标签
4. 刷新页面，找到任意请求
5. 复制 `Cookie` 头全部内容

**配置命令**:
```bash
docker stop rsshub
docker rm rsshub

docker run -d --name rsshub \
  -p 1200:1200 \
  -e TZ=Asia/Shanghai \
  -e NODE_ENV=production \
  -e SMZDM_COOKIE="你的 Cookie 内容" \
  --restart=always \
  diygod/rsshub:latest
```

---

### 2. B 站 (Bilibili)

**获取方法**:
1. 浏览器访问 https://www.bilibili.com/
2. 登录账号 (有会员更好)
3. F12 → Network → 刷新
4. 复制 `Cookie` 头

**配置命令**:
```bash
docker run -d --name rsshub \
  -p 1200:1200 \
  -e TZ=Asia/Shanghai \
  -e BILIBILI_COOKIE="你的 Cookie 内容" \
  ...其他配置... \
  diygod/rsshub:latest
```

---

### 3. 微博 (Weibo)

**获取方法**:
1. 访问 https://weibo.com/
2. 登录后复制 Cookie

**配置**:
```bash
-e WEIBO_COOKIE="你的 Cookie 内容"
```

---

## 📋 推荐配置 (docker-compose)

创建 `docker-compose.yml`:

```yaml
version: '3'
services:
  rsshub:
    image: diygod/rsshub:latest
    container_name: rsshub
    ports:
      - "1200:1200"
    environment:
      - TZ=Asia/Shanghai
      - NODE_ENV=production
      - SMZDM_COOKIE=你的什么值得买 Cookie
      - BILIBILI_COOKIE=你的 B 站 Cookie
      - WEIBO_COOKIE=你的微博 Cookie
      - ZHIHU_COOKIES=你的知乎 Cookie
    restart: always
```

启动:
```bash
docker-compose up -d
```

---

## 🔍 测试路由

```bash
# B 站排行榜 (全区)
curl "http://localhost:1200/bilibili/ranking/0.json"

# 知乎热榜
curl "http://localhost:1200/zhihu/hot.json"

# 微博热搜
curl "http://localhost:1200/weibo/hot.json"

# 什么值得买排行榜
curl "http://localhost:1200/smzdm/ranking.json"
```

---

## 📡 可用路由列表

### B 站
| 路由 | 说明 | 需要 Cookie |
|------|------|-----------|
| `/bilibili/ranking/:rid` | 排行榜 (rid=0 全区) | 推荐 |
| `/bilibili/video/:bvid` | 单个视频 | 否 |
| `/bilibili/user/video/:uid` | UP 主视频 | 否 |

### 知乎
| 路由 | 说明 | 需要 Cookie |
|------|------|-----------|
| `/zhihu/hot` | 热榜 | 否 |
| `/zhihu/daily` | 日报 | 否 |
| `/zhihu/topic/:id` | 话题 | 否 |

### 微博
| 路由 | 说明 | 需要 Cookie |
|------|------|-----------|
| `/weibo/hot` | 热搜榜 | 否 |
| `/weibo/user/:uid` | 用户微博 | 否 |

### 什么值得买
| 路由 | 说明 | 需要 Cookie |
|------|------|-----------|
| `/smzdm/ranking` | 排行榜 | ✅ 必需 |
| `/smzdm/keyword/:kw` | 关键词搜索 | ✅ 必需 |

---

## 🐛 常见错误

### Error -352 (SSL 握手失败)
**原因**: 目标网站反爬或网络问题
**解决**: 配置 Cookie + 重启 RSSHub

### 503 Service Unavailable
**原因**: 路由不存在或缺少配置
**解决**: 检查路由格式 + 配置 Cookie

### ConfigNotFoundError
**原因**: 缺少必要的环境变量
**解决**: 添加对应 Cookie 环境变量

---

## 📊 当前状态

| 平台 | 路由 | 状态 |
|------|------|------|
| B 站 | `/bilibili/ranking/0` | ⏳ 待测试 |
| 知乎 | `/zhihu/hot` | ⏳ 待测试 |
| 微博 | `/weibo/hot` | ⏳ 待测试 |
| 什么值得买 | `/smzdm/ranking` | ⏳ 需要 Cookie |

---

*等待容器启动完成后测试...*
