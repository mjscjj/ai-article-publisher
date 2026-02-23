# 心理学数据源测试结果

> 测试时间: 2026-02-21

---

## ✅ 可用的心理学数据源

### 1. 豆瓣心理学小组 ⭐⭐⭐⭐⭐

**RSS路径**: `http://localhost:1200/douban/group/psychology`

**今日内容示例**:
```
1. 拖延与大学生未来时间洞察力的关系
2. 音乐诱发情绪与神经机制
3. 游戏中的角色认同 — 你选小乔还是李白
4. 微博对剩男剩女的的态度
5. 单亲家庭应怎样改善？
6. 大学生的社交适应水平受什么影响？
```

**特点**:
- ✅ 无需 Puppeteer
- ✅ 心理学专业内容
- ✅ 持续更新

---

### 2. Hacker News (心理学研究) ⭐⭐⭐⭐

**RSS路径**: `http://localhost:1200/hackernews/best`

**关键词筛选**: psychology, brain, mind, mental, behavior, cognitive, neuro

**今日内容示例**:
```
1. We're no longer attracting top talent: the brain drain killing American science
```

**特点**:
- ✅ 无需 Puppeteer
- ⚠️ 需要关键词筛选
- ✅ 学术研究级别

---

### 3. V2EX (心理/成长话题) ⭐⭐⭐

**RSS路径**: `http://localhost:1200/v2ex/topics/hot`

**关键词筛选**: 心理, 情绪, 成长, 人生, 生活

**今日相关内容**:
```
1. 身体已是靠胰岛素维持的状态，爸爸还是酒不离身（健康心理）
2. 过年回家相亲记录（社交心理）
3. 随着 AI 的崛起，我发现一个非常困惑的问题（职业心理）
```

**特点**:
- ✅ 无需 Puppeteer
- ⚠️ 内容较少
- ⚠️ 需要手动筛选

---

## ⚠️ 需要配置的数据源

### 知乎心理学话题

| RSS路径 | 状态 |
|---------|------|
| `/zhihu/topic/19551647/hot` | ❌ 需 Puppeteer |
| `/zhihu/topic/19552039/hot` (心理健康) | ❌ 需 Puppeteer |
| `/zhihu/topic/19571698/hot` (青少年心理) | ❌ 需 Puppeteer |

### 微信公众号

| 公众号 | RSS路径 | 状态 |
|--------|---------|------|
| 简单心理 | `/wechat/mp/msgalbum/{biz}` | ❌ 需 Puppeteer |
| 壹心理 | `/wechat/mp/msgalbum/{biz}` | ❌ 需 Puppeteter |
| KnowYourself | `/wechat/mp/msgalbum/{biz}` | ❌ 需 Puppeteer |

### Semantic Scholar (学术论文)

**状态**: ⚠️ 限流中 (429 Too Many Requests)

**关键词**:
- psychology
- mental health
- adolescent development
- learning psychology
- cognitive science

---

## 📊 心理学内容分类

### 可采集的内容类型

| 类型 | 数据源 | 内容示例 |
|------|--------|----------|
| **心理学科普** | 豆瓣心理学小组 | 拖延与大学生未来时间洞察力 |
| **学术研究** | Hacker News | brain drain killing American science |
| **生活心理** | V2EX | 相亲记录、健康心理 |
| **情绪管理** | 待扩展 | 焦虑、抑郁、压力 |
| **青少年心理** | 待扩展 | 学业压力、成长烦恼 |
| **认知科学** | 待扩展 | 思维、学习、记忆 |

---

## 🔧 采集命令

```bash
# 豆瓣心理学小组
curl -s "http://localhost:1200/douban/group/psychology" | grep -oP '(?<=<title>)[^<]+(?=</title>)'

# Hacker News 心理学相关
curl -s "http://localhost:1200/hackernews/best" | grep -oP '(?<=<title>)[^<]+(?=</title>)' | grep -iE "psychology|brain|mind|mental"

# V2EX 心理/成长话题
curl -s "http://localhost:1200/v2ex/topics/hot" | grep -oP '(?<=<title>)[^<]+(?=</title>)' | grep -iE "心理|情绪|成长"
```

---

## 📝 扩展建议

### 短期（可快速实现）

1. **配置 Puppeteer** - 解锁知乎、微信等数据源
2. **增加豆瓣小组** - 心理咨询、自我成长等小组
3. **增加学术搜索** - 配置 Semantic Scholar API Key

### 中期（需要开发）

1. **专业心理学网站爬虫**
   - 中国心理学会官网
   - 北京师范大学心理学院
   - 简单心理文章

2. **心理健康平台**
   -壹心理文章
   - KnowYourself 内容

3. **教育心理文献**
   - ERIC 数据库
   - 中国知网心理学

---

## 🎯 当前能力总结

| 指标 | 数值 |
|------|------|
| 可用心理学数据源 | 3 个 |
| 每日内容量 | 5-15 条 |
| 内容质量 | 中等 |
| 更新频率 | 实时 |

**Puppeteer 配置**: ✅ 已配置 (browserless/chrome 容器)
**RSSHub 连接**: ✅ 已连接 Puppeteer 服务
**微博热搜**: ✅ 可用（已验证 50+ 条热点）
**36氪**: ✅ 可用
**知乎热榜**: ⚠️ 路由更新中
**抖音热点**: ⚠️ 需额外配置

---

*最后更新: 2026-02-21*