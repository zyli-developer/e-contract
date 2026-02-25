# 后端 — Token 与安全机制

## 一、双 Token 体系

系统使用双 Token 机制（Access Token + Refresh Token），用于所有 API 认证：

```
┌─────────────────────────────────────────────────────────────┐
│                        Token 架构                            │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  Access      │  Access Token                                │
│  Token       │  用于所有业务 API 认证（含签署操作）              │
│              │  Header: Authorization: Bearer {token}         │
│              │                                              │
├──────────────┼──────────────────────────────────────────────┤
│              │                                              │
│  Refresh     │  Refresh Token                               │
│  Token       │  用于刷新 Access Token                        │
│              │  仅用于 /refresh-token 接口                    │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

### 1.1 Member Access Token

| 属性 | 说明 |
|------|------|
| 获取方式 | 登录成功后返回 |
| 传递方式 | `Authorization: Bearer {token}` |
| 有效期 | 由后端 JWT 配置控制 |
| 刷新方式 | 使用 Refresh Token 调用刷新接口 |
| 适用范围 | 所有需要认证的业务 API |

### 1.2 Member Refresh Token

| 属性 | 说明 |
|------|------|
| 获取方式 | 登录成功后与 Access Token 一同返回 |
| 存储位置 | 前端 localStorage（`refreshToken` 键） |
| 有效期 | 通常长于 Access Token（建议 30 天） |
| 用途 | 唯一用途是换取新的 Access Token |

---

## 二、Token 刷新机制

### 2.1 Access Token 刷新流程

```
前端请求 → 后端返回 401 / 1012005005 / 1012005006
     │
     ├── 前端检查：是否正在刷新中？
     │     │
     │     ├── [是] 将当前请求加入等待队列，等待刷新完成
     │     │
     │     └── [否] 设置 isRefreshing = true
     │               │
     │               ├── POST /api/v1/member/auth/refresh-token
     │               │     Body: { refreshToken: "stored_refresh_token" }
     │               │
     │               ├── [成功] 更新存储的 token 和 refreshToken
     │               │         → 重放等待队列中的所有请求
     │               │         → 重试当前请求
     │               │
     │               └── [失败] 清除所有 Token 和用户数据
     │                         → 重定向到登录页
     │
     └── 设置 isRefreshing = false
```

### 2.2 后端刷新接口要求

```
POST /api/v1/member/auth/refresh-token
```

**后端需要实现：**

1. 验证 refreshToken 有效性（未过期、未被撤销）
2. 生成新的 accessToken 和 refreshToken
3. **废弃旧的 refreshToken**（一次性使用，防重放攻击）
4. 返回新的 Token 对

**Response:**
```json
{
  "code": 0,
  "data": {
    "accessToken": "new_access_token",
    "refreshToken": "new_refresh_token"
  }
}
```

### 2.3 并发刷新保护

前端已实现并发保护（同一时刻只发一次刷新请求），但后端也应确保：

- refreshToken 只能使用一次（乐观锁 or 标记已使用）
- 并发使用同一 refreshToken 时只有一个成功
- 成功的刷新请求废弃旧 refreshToken

---

## 三、Seal Core H5 集成安全

### 3.1 H5 页面认证

签署/创建/预览等核心操作在独立的 Seal Core H5 服务中完成，通过 WebView 嵌入小程序。

**URL 构造：**
```
{SEAL_CORE_H5_URL}/h5/{path}?token={accessToken}&platform=mobile&taskId={id}&...
```

**路径映射：**

| mode | H5 路径 | 功能 |
|------|---------|------|
| `create` | `/h5/sign/create` | 模板创建合同 |
| `create-file` | `/h5/sign/create-file` | 文件上传创建 |
| `create-image` | `/h5/sign/create-image` | 图片上传创建 |
| `sign` | `/h5/sign/document` | 签署合同 |
| `view` | `/h5/preview/contract` | 查看合同 |
| `form` | `/h5/sign/form` | 填写表单 |
| `seal-create` | `/h5/seal/create` | 创建印章 |
| `template-preview` | `/h5/template/preview` | 预览模板 |

### 3.2 Seal Core 后端要求

Seal Core H5 服务是独立部署的服务，需要：

1. **验证 URL 中的 Access Token** — 解析 Token 获取用户身份和权限
2. **与主后端共享 Token 签名密钥** — 确保 Token 可跨服务验证

### 3.3 WebView 通信

H5 页面通过 postMessage 向小程序发送消息：

| 消息类型 | 说明 |
|---------|------|
| `signComplete` | 签署完成 |
| `signCancel` | 用户取消签署 |
| `signError` | 签署出错 |
| `ready` | H5 页面加载完成 |
| `close` | 请求关闭 WebView |

---

## 四、认证错误处理

### 4.1 错误码与处理策略

| 错误码 | 含义 | 前端处理 | 后端要求 |
|--------|------|---------|---------|
| `401` | 未认证 | 刷新 Token | 标准 HTTP 401 |
| `1012005005` | Token 无效 | 刷新 Token | 自定义业务码 |
| `1012005006` | Token 过期 | 刷新 Token | 自定义业务码 |
| `403` | 许可证/授权错误 | 弹窗提示 | 返回联系信息 |

### 4.2 403 许可证错误响应格式

```json
{
  "code": 403,
  "msg": "授权已过期",
  "data": {
    "statusDesc": "您的授权已过期，请联系管理员续期",
    "contact": {
      "email": "support@example.com",
      "wechat": "WeChat_ID"
    },
    "tip": "请联系客服获取授权"
  }
}
```

### 4.3 登录重定向防重复

前端实现了防重复跳转机制：
- 使用 `isRedirectingToLogin` 标志位
- 5 秒内不重复跳转
- 后端无需额外处理，但应确保 401 响应一致

---

## 五、请求认证分类

### 5.1 无需认证的接口

| 接口 | 说明 |
|------|------|
| `POST /member/auth/login` | 密码登录 |
| `POST /member/auth/sms-login` | 短信登录 |
| `POST /member/auth/send-sms-code` | 发送验证码 |
| `POST /member/auth/refresh-token` | 刷新 Token |
| `POST /member/auth/social-login` | 社交登录 |
| `POST /member/auth/weixin-mini-app-login` | 微信手机号登录 |
| `GET /member/auth/social-auth-redirect` | OAuth 重定向 |
| `POST /member/auth/create-weixin-jsapi-signature` | JSSDK 签名 |
| `POST /seal/verification/verify` | 合同验真 |
| `GET /seal/verification/get` | 验真详情 |
| `GET /seal/verification/remaining` | 验真配额 |
| `GET /share/summary` | 分享摘要 |

### 5.2 需要 Access Token 的接口

所有业务 API 默认需要 `Authorization: Bearer {token}`，包括：
- 用户信息管理
- 企业管理
- 合同签署任务管理
- 印章管理（CRUD、模板）
- 配额与支付
- KYC 认证
- Seal Core H5 页面 URL 中的 token 参数

---

## 六、后端安全实现建议

### 6.1 Token 生成

- 使用 JWT（JSON Web Token）或类似机制
- Access Token 建议有效期 2 小时
- Refresh Token 建议有效期 30 天

### 6.2 Token 存储

- Access Token：无状态（JWT 自校验）或 Redis 缓存
- Refresh Token：数据库持久化（支持撤销）

### 6.3 安全措施

| 措施 | 说明 |
|------|------|
| HTTPS | 所有接口强制 HTTPS（生产环境） |
| Refresh Token 一次性 | 使用后立即废弃，防重放 |
| 并发控制 | 同一 refreshToken 只允许一次刷新成功 |
| 密钥安全 | 微信 AppSecret、JWT 签名密钥不可泄露 |
