import Taro from '@tarojs/taro'
import { useAuthStore } from '@/store/useAuthStore'
import { BASE_URL, DEFAULT_TIMEOUT } from './config'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  isAuth?: boolean
  timeout?: number
}

interface ApiResponse<T = any> {
  code: number
  msg: string
  data: T
}

let isRefreshing = false
let requestQueue: (() => void)[] = []

export async function request<T = any>(options: RequestOptions): Promise<T> {
  const { token } = useAuthStore.getState()

  const header: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (options.isAuth !== false && token) {
    header['Authorization'] = `Bearer ${token}`
  }

  const res = await Taro.request<ApiResponse<T>>({
    url: `${BASE_URL}${options.url}`,
    method: options.method || 'GET',
    data: options.data,
    header,
    timeout: options.timeout || DEFAULT_TIMEOUT,
  })

  const result = res.data

  if (result.code === 0 || result.code === 200) {
    return result.data
  }

  // Token 过期，尝试刷新
  if ([401, 1012005005, 1012005006].includes(result.code)) {
    if (!isRefreshing) {
      isRefreshing = true
      try {
        await refreshTokenRequest()
        isRefreshing = false
        // 重放队列中的请求
        requestQueue.forEach((cb) => cb())
        requestQueue = []
        return request<T>(options)
      } catch {
        isRefreshing = false
        requestQueue = []
        useAuthStore.getState().logout()
        Taro.navigateTo({ url: '/pages/login/index' })
        throw new Error('登录已过期，请重新登录')
      }
    } else {
      // 排队等待刷新完成
      return new Promise<T>((resolve) => {
        requestQueue.push(() => resolve(request<T>(options)))
      })
    }
  }

  throw new Error(result.msg || '请求失败')
}

async function refreshTokenRequest() {
  const { refreshToken, setTokens } = useAuthStore.getState()
  if (!refreshToken) throw new Error('No refresh token')

  const res = await Taro.request<ApiResponse>({
    url: `${BASE_URL}/member/auth/refresh-token`,
    method: 'POST',
    header: {
      'Content-Type': 'application/json',
    },
    data: { refreshToken },
  })

  if (res.data.code === 0 || res.data.code === 200) {
    setTokens(res.data.data.accessToken, res.data.data.refreshToken)
  } else {
    throw new Error('Refresh failed')
  }
}
