# OpenClaw 配置微信公众号 API Key 教程

> 整理时间: 2026-02-22

---

## 📋 教程汇总

### 1. 官方文档

| 文档 | 链接 |
|------|------|
| OpenClaw 配置指南 | https://docs.openclaw.ai/gateway/configuration |
| wemp-operator Skill | https://github.com/IanShaw027/wemp-operator |
| 微信公众号开发文档 | https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html |
| 微信公众平台 | https://mp.weixin.qq.com |

### 2. 社区资源

| 资源 | 链接 |
|------|------|
| OpenClaw Discord | https://discord.gg/clawd |
| OpenClaw GitHub | https://github.com/openclaw/openclaw |
| wemp-operator Issues | https://github.com/IanShaw027/wemp-operator/issues |

---

## 🚀 完整配置教程

### 步骤 1: 获取微信公众号 AppID 和 AppSecret

1. **登录微信公众平台**
   ```
   https://mp.weixin.qq.com
   ```

2. **进入开发者配置**
   ```
   左侧菜单 → 开发 → 基本配置
   ```

3. **复制 AppID 和 AppSecret**
   - AppID: 类似 `wx1234567890abcdef`
   - AppSecret: 类似 `1234567890abcdefghijklmnopqrstuv`

4. **设置 IP 白名单** ⚠️ 重要
   ```
   开发 → 基本配置 → IP白名单 → 添加你的服务器 IP
   ```

   **如何查看服务器 IP**:
   ```bash
   # 在服务器上执行
   curl ifconfig.me
   # 或
   curl ip.sb
   ```

5. **设置服务器配置** (可选)
   ```
   开发 → 基本配置 → 服务器配置
   - URL: 你的服务器地址
   - Token: 自定义令牌
   - EncodingAESKey: 随机生成
   ```

---

### 步骤 2: 安装 wemp-operator Skill

```bash
# 方式 1: 通过 ClawHub 安装 (推荐)
openclaw skill install IanShaw027/wemp-operator

# 方式 2: 手动安装
git clone https://github.com/IanShaw027/wemp-operator.git \
  ~/.openclaw/workspace/skills/wemp-operator
```

---

### 步骤 3: 配置 OpenClaw

**方式 1: 使用配置向导**
```bash
openclaw configure
# 按提示输入 AppID 和 AppSecret
```

**方式 2: 直接编辑配置文件**
```bash
# 编辑配置文件
nano ~/.openclaw/openclaw.json

# 或使用 VS Code
code ~/.openclaw/openclaw.json
```

**添加以下配置**:
```json5
{
  "channels": {
    "wemp": {
      "enabled": true,
      "appId": "wx1234567890abcdef",      // 替换为你的 AppID
      "appSecret": "your-app-secret-here"  // 替换为你的 AppSecret
    }
  }
}
```

**方式 3: 使用 CLI 命令**
```bash
openclaw config set channels.wemp.enabled true
openclaw config set channels.wemp.appId "wx1234567890abcdef"
openclaw config set channels.wemp.appSecret "your-app-secret-here"
```

---

### 步骤 4: 验证配置

```bash
# 检查配置是否正确
openclaw doctor

# 测试 API 连接
cd ~/.openclaw/workspace/skills/wemp-operator
node scripts/setup.mjs
```

---

### 步骤 5: 使用 Skill

**自然语言交互**:
```
帮我采集今天的 AI 热点
生成公众号日报
检查公众号新评论
```

**命令行调用**:
```bash
# 采集热点
node ~/.openclaw/workspace/skills/wemp-operator/scripts/content/smart-collect.mjs \
  --query "AI热点" \
  --sources "hackernews,v2ex,36kr"

# 生成日报
node ~/.openclaw/workspace/skills/wemp-operator/scripts/analytics/daily-report.mjs
```

---

## 🔧 高级配置

### 配置多个公众号

```json5
{
  "channels": {
    "wemp": {
      "enabled": true,
      "accounts": {
        "main": {
          "appId": "wx_main_account_id",
          "appSecret": "main_secret"
        },
        "tech": {
          "appId": "wx_tech_account_id",
          "appSecret": "tech_secret"
        }
      }
    }
  }
}
```

### 配置访问权限

```json5
{
  "channels": {
    "wemp": {
      "enabled": true,
      "appId": "your-app-id",
      "appSecret": "your-app-secret",
      "allowFrom": ["owner_user_openid"],  // 允许的用户
      "dmPolicy": "pairing"                 // DM 访问策略
    }
  }
}
```

---

## ⚠️ 常见问题

### 1. IP 白名单未设置

**错误**: `ip not in whitelist`

**解决**:
```bash
# 查看服务器 IP
curl ifconfig.me

# 在微信公众平台添加该 IP 到白名单
```

### 2. AppSecret 错误

**错误**: `invalid appsecret`

**解决**:
- 检查 AppSecret 是否正确复制（无空格）
- 重置 AppSecret 并更新配置

### 3. Access Token 过期

**错误**: `access_token expired`

**解决**:
```bash
# wemp-operator 会自动刷新 token
# 如果失败，重启 Gateway
openclaw gateway restart
```

### 4. 配置文件格式错误

**错误**: `Config validation failed`

**解决**:
```bash
# 检查配置格式
openclaw doctor

# 修复配置
openclaw doctor --fix
```

---

## 📚 相关 Skills

| Skill | 功能 | 安装 |
|-------|------|------|
| **wemp-operator** | 公众号运营 (70 API) | `openclaw skill install IanShaw027/wemp-operator` |
| **wechat-article-skill** | 文章创作 + 发布 | 已安装在 workspace/skills/ |
| **wemp** | 基础公众号集成 | 已安装 |

---

## 🔗 参考链接

1. **OpenClaw 官方文档**
   - 配置指南: https://docs.openclaw.ai/gateway/configuration
   - Channel 配置: https://docs.openclaw.ai/channels
   - 故障排除: https://docs.openclaw.ai/help/troubleshooting

2. **微信公众号开发**
   - 开发文档: https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html
   - 接口权限: https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Explanation_of_interface_privileges.html
   - 错误码文档: https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Global_Return_Code.html

3. **社区支持**
   - OpenClaw Discord: https://discord.gg/clawd
   - GitHub Issues: https://github.com/openclaw/openclaw/issues

---

## 💡 小贴士

1. **安全建议**
   - 不要在代码中硬编码 AppSecret
   - 定期更换 AppSecret
   - 使用 IP 白名单限制访问

2. **调试技巧**
   ```bash
   # 查看详细日志
   openclaw gateway --verbose
   
   # 测试 API 连接
   curl "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=YOUR_APPID&secret=YOUR_SECRET"
   ```

3. **配置热重载**
   - OpenClaw 会自动检测配置文件变化
   - 修改后无需重启 Gateway

---

*教程整理: 2026-02-22*