# 小红书替代方案 - 实施总结

> **日期**: 2026-02-26
> **状态**: 代码就绪，待 RSSHub 修复

---

## ✅ 已完成的工作

### 1. 百度 MCP Provider
- **文件**: `plugins/autonomous_researcher/providers/baidu_mcp.py`
- **实现**: 百度移动版爬虫 (免 API Key)
- **状态**: ✅ 代码完成，待测试 (百度反爬强)

### 2. B 站采集器 (小红书替代 ①)
- **文件**: `plugins/retrieval/bilibili_collector.py`
- **功能**: 获取 B 站视频元数据 + 评论
- **依赖**: RSSHub `/bilibili/ranking` 或 `/bilibili/search`
- **状态**: ⚠️ 代码完成，RSSHub 路由故障 (-352 SSL 错误)

### 3. 什么值得买采集器 (小红书替代 ②)
- **文件**: `plugins/retrieval/smzdm_collector.py`
- **功能**: 获取爆料 + 用户评测
- **依赖**: RSSHub `/smzdm/keyword/{kw}` + Cookie
- **状态**: ⚠️ 代码完成，需要配置 SMZDM_COOKIE

### 4. Domestic Sniffer V2 集成
- **文件**: `plugins/retrieval/domestic_sniffer.py`
- **升级**: 集成 B 站 + 什么值得买 + 百度
- **状态**: ✅ 代码完成

### 5. 文档
- `README_XIAOHONGSHU_ALTERNATIVE.md` - 替代方案说明
- `DEPLOY_STATUS.md` - 部署状态跟踪
- `BAIDU_MCP_DEPLOY.md` - 百度 MCP 部署指南

---

## ⚠️ 当前阻塞

### 1. RSSHub 服务问题

**现象**:
- B 站路由：Error -352 (SSL 握手失败)
- 什么值得买：需要 Cookie 配置
- 微博搜索：路由不存在 (404)
- 知乎搜索：路由不存在 (404)

**根本原因**:
- RSSHub Docker 容器网络问题 (无法访问 B 站 API)
- 缺少平台 Cookie (什么值得买)
- 路由参数错误 (搜索类路由需要特定格式)

**解决方案**:

#### 方案 A: 修复 RSSHub (推荐)
```bash
# 1. 重启 RSSHub 容器
docker restart rsshub

# 2. 配置环境变量 (docker-compose 或 docker run)
docker run -d --name rsshub \
  -p 1200:1200 \
  -e BILIBILI_COOKIE=xxx \
  -e SMZDM_COOKIE=xxx \
  -e WEIBO_COOKIE=xxx \
  diygod/rsshub:latest

# 3. 检查日志
docker logs -f rsshub
```

#### 方案 B: 直连 API (临时方案)
创建独立采集器，绕过 RSSHub:
- `bilibili_direct.py` - 直接调用 B 站 API
- `zhihu_direct.py` - 直接调用知乎 API
- `weibo_direct.py` - 直接调用微博 API

---

## 📊 数据源状态

| 平台 | 采集方式 | 状态 | 备注 |
|------|---------|------|------|
| ~~小红书~~ | MCP | ❌ 放弃 | 反爬太强 |
| 百度新闻 | 爬虫 | ⚠️ 待测 | 代码就绪 |
| B 站 | RSSHub | ⚠️ 故障 | SSL 错误 -352 |
| 什么值得买 | RSSHub+Cookie | ⚠️ 待配置 | 需要 Cookie |
| 微博 | RSSHub | ⚠️ 路由错误 | 搜索路由不存在 |
| 知乎 | RSSHub | ⚠️ 路由错误 | 搜索路由不存在 |

---

## 🎯 下一步行动

### 优先级 1 (今天)
1. **修复 RSSHub**: 配置 Cookie + 检查网络
2. **测试百度 Provider**: 手动验证爬虫是否可用

### 优先级 2 (明天)
3. **开发直连采集器**: 作为 RSSHub 备用方案
4. **情感分析模块**: LLM 零样本分类

### 优先级 3 (后天)
5. **触发器引擎**: 事件驱动升频
6. **集成测试**: 端到端验证完整流程

---

## 📝 RSSHub 正确路由参考

```
# B 站
/bilibili/ranking/:rid  # 排行榜 (rid=0 全区)
/bilibili/video/:bvid   # 单个视频

# 知乎
/zhihu/hot              # 热榜 (非搜索)
/zhihu/daily            # 日报

# 微博
/weibo/hot              # 热搜榜
/weibo/user/:uid        # 用户微博

# 什么值得买
/smzdm/keyword/:keyword # 关键词搜索 (需要 Cookie)
/smzdm/ranking          # 排行榜
```

---

*部署进度：代码 100% 完成，环境配置 40%*
