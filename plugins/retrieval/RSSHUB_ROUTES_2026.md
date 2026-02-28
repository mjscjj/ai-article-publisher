# RSSHub 2026 路由更新

> **问题**: RSSHub 新版本改变了路由格式，旧路由返回 404/503

---

## 🔍 测试结果

| 旧路由 | 状态 | 新路由 (待验证) |
|--------|------|---------------|
| `/zhihu/hot.json` | ❌ NotFoundError | `/zhihu/hot-list` |
| `/weibo/hot.json` | ❌ NotFoundError | `/weibo/search-hot` |
| `/bilibili/ranking/0.json` | ❌ Invalid rid | `/bilibili/ranking/all` |
| `/smzdm/keyword/:kw` | ❌ 需要 Cookie | `/smzdm/ranking` |

---

## 📡 推荐方案：直连 API

由于 RSSHub 路由频繁变化且需要 Cookie 配置，建议**直接使用平台 API**：

### 方案优势
- ✅ 无需中间层，降低延迟
- ✅ 不依赖 RSSHub 维护
- ✅ 更灵活的数据处理

### 实现计划

| 平台 | 实现方式 | 优先级 |
|------|---------|--------|
| 知乎 | 直连知乎热榜 API | P0 |
| 微博 | 直连微博热搜 API | P0 |
| B 站 | 直连 B 站排行榜 API | P0 |
| 什么值得买 | 需要 Cookie，降级使用 | P1 |

---

## 🚀 下一步

1. **开发直连采集器** (今天)
   - `zhihu_direct.py` - 知乎热榜
   - `weibo_direct.py` - 微博热搜
   - `bilibili_direct.py` - B 站排行

2. **更新 Domestic Sniffer** (今天)
   - 集成直连采集器
   - 保留 RSSHub 作为备用

3. **测试验证** (明天)
   - 端到端测试
   - 性能基准

---

*RSSHub 保留作为备用方案，优先开发直连 API*
