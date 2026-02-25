import Taro from '@tarojs/taro'
import { useAuthStore } from '@/store/useAuthStore'

/** 认证相关 Hook */
export function useAuth() {
  const { token, logout } = useAuthStore()

  const isLoggedIn = !!token

  const requireAuth = () => {
    if (!isLoggedIn) {
      Taro.navigateTo({ url: '/pages/login/index' })
      return false
    }
    return true
  }

  return { isLoggedIn, requireAuth, logout }
}
