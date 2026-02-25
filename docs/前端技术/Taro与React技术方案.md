# 前端 — Taro + React 技术方案

> **技术选型变更说明：** 原参考项目使用 uni-app + Vue 3（UTS/UVue）。本项目前端改用 **Taro + React + TypeScript**，编译为微信小程序，同时支持 H5 多端。所有业务功能和页面保持不变，仅替换前端框架。

## 一、技术栈总览

| 层级 | 技术 | 说明 |
|------|------|------|
| **框架** | Taro 4.x | 京东出品，React 语法编译为多端小程序 |
| **UI 框架** | React 18 | 函数组件 + Hooks |
| **语言** | TypeScript | 类型安全 |
| **状态管理** | Zustand 或 Jotai | 轻量级，替代原项目的 localStorage 直接读写 |
| **UI 组件库** | Taro UI / NutUI-React | 适配小程序的 React 组件库 |
| **CSS 方案** | CSS Modules 或 Tailwind CSS | 样式隔离 |
| **包管理** | pnpm | 与原项目一致 |
| **编译目标** | 微信小程序 / H5 | 多端输出 |

> **Taro** 是京东开源的多端统一开发框架，使用 React 语法编写，编译为微信/支付宝/百度小程序及 H5。
>
> 文档：https://taro-docs.jd.com/

---

## 二、Taro 项目初始化

```bash
# 安装 Taro CLI
npm install -g @tarojs/cli

# 创建项目（选择 React + TypeScript 模板）
taro init mini-contract-app
# 框架选择: React
# 模板选择: 默认模板
# CSS 预处理: Sass
# 包管理工具: pnpm

# 安装依赖
cd mini-contract-app
pnpm install

# 开发模式（微信小程序）
pnpm run dev:weixin

# 生产构建
pnpm run build:weixin

# H5 开发
pnpm run dev:h5
```

构建产物在 `dist/` 目录下，在微信开发者工具中导入 `dist/` 即可预览。

---

## 三、项目目录结构

```
mini-contract-app/
│
├── src/
│   ├── app.ts                       # 应用入口
│   ├── app.config.ts                # 全局配置（页面路由、tabBar）
│   ├── app.scss                     # 全局样式
│   │
│   ├── pages/                       # 页面组件
│   │   ├── index/                   # 首页
│   │   │   ├── index.tsx
│   │   │   ├── index.config.ts      # 页面配置（导航栏标题等）
│   │   │   └── index.scss
│   │   ├── login/                   # 登录
│   │   ├── register/                # 注册
│   │   ├── contract-manage/         # 合同管理
│   │   ├── contract-detail/         # 合同详情
│   │   ├── contract-sign/           # 合同签署
│   │   ├── contract-create/         # 合同创建
│   │   ├── profile/                 # 个人中心
│   │   ├── enterprise/              # 企业管理
│   │   ├── template-market/         # 模板市场
│   │   ├── contract-audit/          # 天眼审查
│   │   ├── contract-verify/         # 合同验真
│   │   ├── quota/                   # 配额管理
│   │   └── kyc/                     # KYC 认证（子包）
│   │
│   ├── components/                  # 通用组件
│   │   ├── KycModal/
│   │   ├── EnterpriseKycModal/
│   │   ├── H5LoadingContainer/
│   │   ├── H5ErrorContainer/
│   │   ├── QuotaBalanceCard/
│   │   └── PrivacyGuideModal/
│   │
│   ├── api/                         # API 请求层
│   │   ├── request.ts               # 统一请求封装（Token 注入、401 刷新）
│   │   ├── config.ts                # API 基础配置
│   │   ├── auth.ts                  # 认证接口
│   │   ├── social.ts                # 社交登录
│   │   ├── contracts.ts             # 合同管理
│   │   ├── seals.ts                 # 印章管理
│   │   ├── enterprise.ts            # 企业管理
│   │   ├── templates.ts             # 合同模板
│   │   ├── quota.ts                 # 配额
│   │   ├── verification.ts          # 合同验真
│   │   └── file.ts                  # 文件上传
│   │
│   ├── store/                       # 状态管理 (Zustand)
│   │   ├── useAuthStore.ts          # 认证状态（token, user, kycStatus）
│   │   ├── useIdentityStore.ts      # 身份切换（个人/企业）
│   │   └── useContractStore.ts      # 合同相关状态
│   │
│   ├── hooks/                       # 自定义 Hooks
│   │   ├── useAuth.ts               # 认证相关
│   │   ├── useKycGuard.ts           # KYC 校验守卫
│   │   └── usePagination.ts         # 分页加载
│   │
│   ├── utils/                       # 工具函数
│   │   ├── date.ts                  # 日期格式化
│   │   ├── network.ts               # 网络检测
│   │   ├── platform.ts              # 平台检测
│   │   ├── storage.ts               # 存储封装
│   │   └── share.ts                 # 分享配置
│   │
│   └── config/                      # 应用配置
│       └── app.config.ts            # 品牌名、版本号
│
├── config/                          # Taro 编译配置
│   ├── index.ts                     # 通用配置
│   ├── dev.ts                       # 开发环境
│   └── prod.ts                      # 生产环境
│
├── project.config.json              # 微信小程序项目配置
├── tsconfig.json
├── package.json
└── pnpm-lock.yaml
```

---

## 四、uni-app → Taro 迁移对照

### 4.1 API 差异

| 功能 | uni-app (原项目) | Taro (新项目) |
|------|-----------------|---------------|
| 网络请求 | `uni.request()` | `Taro.request()` |
| 路由跳转 | `uni.navigateTo()` | `Taro.navigateTo()` |
| Tab 切换 | `uni.switchTab()` | `Taro.switchTab()` |
| 存储 | `uni.setStorageSync()` | `Taro.setStorageSync()` |
| 登录 | `uni.login()` | `Taro.login()` |
| 获取手机号 | `<button open-type="getPhoneNumber">` | `<Button openType="getPhoneNumber">` |
| WebView | `<web-view>` | `<WebView>` |
| 下拉刷新 | `onPullDownRefresh()` | `usePullDownRefresh()` |
| 分享 | `onShareAppMessage()` | `useShareAppMessage()` |
| 条件编译 | `#ifdef MP-WEIXIN` | `process.env.TARO_ENV === 'weixin'` |

### 4.2 组件差异

| uni-app 组件 | Taro 组件 |
|-------------|-----------|
| `<view>` | `<View>` |
| `<text>` | `<Text>` |
| `<image>` | `<Image>` |
| `<scroll-view>` | `<ScrollView>` |
| `<swiper>` | `<Swiper>` |
| `<button>` | `<Button>` |
| `<input>` | `<Input>` |
| `<web-view>` | `<WebView>` |
| `<uni-icons>` | NutUI `<Icon>` 或自定义 |
| `<uni-popup>` | NutUI `<Popup>` |

### 4.3 生命周期差异

| uni-app (Vue 3) | Taro (React Hooks) |
|-----------------|-------------------|
| `onLoad(options)` | `useLoad((options) => {})` |
| `onShow()` | `useDidShow(() => {})` |
| `onHide()` | `useDidHide(() => {})` |
| `onReady()` | `useReady(() => {})` |
| `onPullDownRefresh()` | `usePullDownRefresh(() => {})` |
| `onReachBottom()` | `useReachBottom(() => {})` |
| `onShareAppMessage()` | `useShareAppMessage(() => ({}))` |
| `onPageScroll(e)` | `usePageScroll((e) => {})` |

### 4.4 状态管理差异

```
原项目: localStorage 直接读写
  uni.setStorageSync('token', value)
  uni.getStorageSync('token')

新项目: Zustand + 持久化
  const useAuthStore = create(persist(
    (set) => ({
      token: '',
      setToken: (token) => set({ token }),
    }),
    { name: 'auth-storage', getStorage: () => taroStorage }
  ))
```

---

## 五、路由配置

Taro 路由在 `src/app.config.ts` 中配置，与原项目 `pages.json` 对应：

```typescript
// src/app.config.ts
export default defineAppConfig({
  pages: [
    'pages/login/index',
    'pages/register/index',
    'pages/index/index',
    'pages/contract-manage/index',
    'pages/contract-manage/draft',
    'pages/contract-detail/index',
    'pages/contract-sign/index',
    'pages/contract-sign/h5-sign',
    'pages/contract-create/h5-create',
    'pages/profile/index',
    'pages/profile/seals',
    'pages/profile/seal-create',
    'pages/profile/settings',
    'pages/enterprise/list',
    'pages/enterprise/detail',
    'pages/enterprise/members',
    'pages/template-market/index',
    'pages/template-detail/index',
    'pages/contract-audit/report',
    'pages/contract-verify/index',
    'pages/quota/purchase',
    // ... 其余页面
  ],
  subPackages: [
    {
      root: 'pages/kyc',
      pages: [
        'personal/index',
        'enterprise/index',
      ],
    },
  ],
  tabBar: {
    color: '#999999',
    selectedColor: '#00C28A',
    list: [
      { pagePath: 'pages/index/index', text: '首页', iconPath: '...', selectedIconPath: '...' },
      { pagePath: 'pages/contract-manage/index', text: '合同', iconPath: '...', selectedIconPath: '...' },
      { pagePath: 'pages/profile/index', text: '我的', iconPath: '...', selectedIconPath: '...' },
    ],
  },
  window: {
    navigationBarBackgroundColor: '#00C28A',
    navigationBarTextStyle: 'white',
  },
})
```

---

## 六、API 请求封装

```typescript
// src/api/request.ts
import Taro from '@tarojs/taro'
import { useAuthStore } from '@/store/useAuthStore'

const BASE_URL = process.env.NODE_ENV === 'development'
  ? 'http://localhost:8000/app-api'
  : '/app-api'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  isAuth?: boolean
  timeout?: number
}

let isRefreshing = false
let requestQueue: (() => void)[] = []

export async function request<T>(options: RequestOptions): Promise<T> {
  const { token } = useAuthStore.getState()
  const header: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (options.isAuth !== false && token) {
    header['Authorization'] = `Bearer ${token}`
  }

  try {
    const res = await Taro.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header,
      timeout: options.timeout || 30000,
    })

    const data = res.data
    if (data.code === 0 || data.code === 200) {
      return data.data as T
    }

    // 401: Token 刷新
    if ([401, 1012005005, 1012005006].includes(data.code)) {
      return handleTokenRefresh(options)
    }

    throw new Error(data.msg || '请求失败')
  } catch (err) {
    throw err
  }
}
```

---

## 七、微信登录（Taro 写法）

```tsx
// src/pages/login/index.tsx
import { View, Button, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { socialLogin, weixinMiniAppLogin } from '@/api/auth'

export default function LoginPage() {
  // 微信静默登录
  const handleWechatLogin = async () => {
    const { code } = await Taro.login()
    const result = await socialLogin({ type: 34, code, state: 'default' })
    // 存储 token ...
  }

  // 微信手机号快捷登录
  const handleGetPhoneNumber = async (e) => {
    if (e.detail.errMsg !== 'getPhoneNumber:ok') return
    const phoneCode = e.detail.code
    const { code: loginCode } = await Taro.login()
    const result = await weixinMiniAppLogin({
      phoneCode,
      loginCode,
      state: 'default'
    })
    // 存储 token ...
  }

  return (
    <View>
      <Button onClick={handleWechatLogin}>微信登录</Button>
      <Button openType="getPhoneNumber" onGetPhoneNumber={handleGetPhoneNumber}>
        手机号快捷登录
      </Button>
    </View>
  )
}
```

---

## 八、开发命令

```bash
# 微信小程序
pnpm run dev:weixin          # 开发模式
pnpm run build:weixin        # 生产构建

# H5
pnpm run dev:h5              # H5 开发模式
pnpm run build:h5            # H5 生产构建

# 其他小程序
pnpm run dev:alipay          # 支付宝小程序
pnpm run dev:swan            # 百度小程序
pnpm run dev:tt              # 头条小程序
```

构建后在微信开发者工具中导入 `dist/` 目录即可预览。

---

## 九、原 uni-app 项目 → Taro 迁移注意事项

| 注意事项 | 说明 |
|---------|------|
| **条件编译** | uni-app 用 `#ifdef`，Taro 用 `process.env.TARO_ENV` 判断 |
| **全局变量** | uni-app 用 `uni.xxx`，Taro 用 `Taro.xxx`（API 基本一致） |
| **组件库** | uni-ui 替换为 NutUI-React 或 Taro UI |
| **样式单位** | uni-app 用 `rpx`，Taro 也支持 `rpx`（自动转换） |
| **WebView** | Taro 中使用 `<WebView src={url} />` 组件 |
| **分包加载** | 配置 `subPackages`，与 uni-app 逻辑一致 |
| **主题色** | 保持 `#00C28A` 绿色主题不变 |
