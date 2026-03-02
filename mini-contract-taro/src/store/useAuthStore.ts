import Taro from '@tarojs/taro'
import { create } from 'zustand'

interface AuthState {
  token: string
  refreshToken: string
  userId: number | null
  role: string
  userInfo: {
    nickname: string
    avatar: string
    mobile: string
  } | null

  setTokens: (token: string, refreshToken: string) => void
  setUserId: (userId: number) => void
  setUserInfo: (info: AuthState['userInfo']) => void
  setRole: (role: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: Taro.getStorageSync('token') || '',
  refreshToken: Taro.getStorageSync('refreshToken') || '',
  userId: Taro.getStorageSync('userId') || null,
  role: Taro.getStorageSync('role') || 'landlord',
  userInfo: null,

  setTokens: (token, refreshToken) => {
    Taro.setStorageSync('token', token)
    Taro.setStorageSync('refreshToken', refreshToken)
    set({ token, refreshToken })
  },

  setUserId: (userId) => {
    Taro.setStorageSync('userId', userId)
    set({ userId })
  },

  setUserInfo: (userInfo) => set({ userInfo }),

  setRole: (role) => {
    Taro.setStorageSync('role', role)
    set({ role })
  },

  logout: () => {
    Taro.removeStorageSync('token')
    Taro.removeStorageSync('refreshToken')
    Taro.removeStorageSync('userId')
    Taro.removeStorageSync('role')
    set({ token: '', refreshToken: '', userId: null, userInfo: null, role: 'landlord' })
  },
}))
