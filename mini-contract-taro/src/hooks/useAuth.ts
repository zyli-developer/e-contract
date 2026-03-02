import Taro, { useDidShow } from '@tarojs/taro'
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

/** 路由守卫 Hook：页面显示时自动检查登录状态，未登录则跳转登录页 */
export function useRequireAuth() {
  const { token } = useAuthStore()

  useDidShow(() => {
    if (!token) {
      Taro.redirectTo({ url: '/pages/login/index' })
    }
  })

  return !!token
}

/** 路由守卫 Hook：要求房东角色，租客跳转回上一页 */
export function useRequireLandlord() {
  const { token } = useAuthStore()
  const role = useAuthStore.getState().role

  useDidShow(() => {
    if (!token) {
      Taro.redirectTo({ url: '/pages/login/index' })
    } else if (role === 'tenant') {
      Taro.showToast({ title: '该功能仅房东可用', icon: 'none' })
      Taro.navigateBack()
    }
  })
}
