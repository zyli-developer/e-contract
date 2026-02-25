import Taro from '@tarojs/taro'

export const storage = {
  get<T = string>(key: string): T | null {
    try {
      return Taro.getStorageSync(key) || null
    } catch {
      return null
    }
  },

  set(key: string, value: any): void {
    Taro.setStorageSync(key, value)
  },

  remove(key: string): void {
    Taro.removeStorageSync(key)
  },
}
