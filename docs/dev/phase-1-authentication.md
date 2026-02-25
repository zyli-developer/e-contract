# Phase 1：用户认证

**目标**：实现微信小程序登录、短信验证码登录、双 Token 体系、基础用户信息管理。

**前置依赖**：Phase 0

## 后端任务

| # | 任务 | 说明 |
|---|------|------|
| 1.1 | 微信小程序登录 | `POST /member/auth/social-login`（type=34），对接微信 `code2Session` 获取 openid，返回 Access + Refresh Token |
| 1.2 | 短信验证码登录 | `POST /member/auth/sms-login`（登录即注册），`POST /member/auth/send-sms-code`（scene=1 登录） |
| 1.3 | 密码登录 | `POST /member/auth/login`，bcrypt 验证 |
| 1.4 | Token 刷新 | `POST /member/auth/refresh-token`，Refresh Token 单次使用、乐观锁防重放 |
| 1.5 | JWT 中间件 | 解析 `Authorization: Bearer {token}` header，注入 current_user；公开接口白名单 |
| 1.6 | 用户信息 | `GET /member/user/get`、`PUT /member/user/update`、`PUT /member/user/update-password` |
| 1.7 | 登出 | `POST /member/auth/logout`，销毁 Token |

**Pydantic Schemas**：`LoginReq`, `SmsLoginReq`, `SocialLoginReq`, `RefreshTokenReq`, `AuthTokenResp`, `UserInfoResp`, `UpdatePasswordReq`

**数据表**：`member`, `member_social_user`, `member_token`

## 前端任务

| # | 任务 | 说明 |
|---|------|------|
| 1.8 | useAuthStore | Zustand store：token/refreshToken/userId/userInfo 持久化到 Storage |
| 1.9 | Auth API 层 | `api/auth.ts`：login、smsLogin、socialLogin、refreshToken、logout |
| 1.10 | Token 刷新拦截器 | 请求 401 时自动刷新 Token，并发请求排队等待刷新完成后重放 |
| 1.11 | 登录页 | 微信一键登录按钮 + 手机号短信验证码登录 tab |
| 1.12 | 个人中心页 | Profile 页：头像、昵称、手机号、修改密码入口、设置入口 |
| 1.13 | 个人信息编辑页 | 修改昵称、头像 |
| 1.14 | 修改密码页 | 旧密码 + 新密码表单 |
| 1.15 | 路由守卫 | 未登录用户访问需认证页面时自动跳转登录页 |

## 测试任务

| 测试文件 | 覆盖内容 |
|----------|---------|
| `test_auth_service.py` | 密码校验、Token 生成/刷新/失效、Refresh Token 单次使用、并发刷新只成功一次 |
| `test_auth_api.py` | 3 种登录的请求/响应/错误码、Token 过期返回 401、公开接口无需 Token |
| `test_wechat_mock.py` | respx mock 微信 code2Session API，各种错误场景 |
| `test_user_api.py` | 用户信息查询/更新、密码修改（旧密码错误、新密码校验） |
| `auth.test.tsx` | 登录表单验证、提交、错误提示、Token 存储 |
| `useAuth.test.ts` | Token 刷新逻辑、并发请求排队、401 重试 |
| `login-page.test.tsx` | 微信登录按钮渲染、短信登录表单交互 |

### 集成测试

- `test_login_flow.py`：短信登录（新用户自动注册）→ 获取用户信息 → Token 刷新 → 再次获取信息 → 登出

## 交付物

- [ ] 微信小程序登录正常（开发者工具 + 真机）
- [ ] 短信验证码登录正常（登录即注册）
- [ ] Token 刷新机制正常工作，并发安全
- [ ] 前端登录页、个人中心页可用
- [ ] 未登录自动跳转登录页
- [ ] 后端测试覆盖率 ≥ 85%
