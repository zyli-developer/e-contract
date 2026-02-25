import Taro from '@tarojs/taro'
import { useCallback } from 'react'
import { exchangeSealToken } from '@/api/seals'

const SEAL_TOKEN_KEY = 'sealToken'
const SEAL_TOKEN_EXPIRE_KEY = 'sealTokenExpire'

/** Seal Token 管理 Hook */
export function useSealToken() {
  const getSealToken = useCallback(async (): Promise<string> => {
    const cached = Taro.getStorageSync(SEAL_TOKEN_KEY)
    const expire = Taro.getStorageSync(SEAL_TOKEN_EXPIRE_KEY)

    // 缓存有效且未过期（预留 10 分钟）
    if (cached && expire && Date.now() < expire - 10 * 60 * 1000) {
      return cached
    }

    // 重新获取
    const result = await exchangeSealToken()
    Taro.setStorageSync(SEAL_TOKEN_KEY, result.token)
    Taro.setStorageSync(SEAL_TOKEN_EXPIRE_KEY, new Date(result.expireTime).getTime())
    return result.token
  }, [])

  const clearSealToken = useCallback(() => {
    Taro.removeStorageSync(SEAL_TOKEN_KEY)
    Taro.removeStorageSync(SEAL_TOKEN_EXPIRE_KEY)
  }, [])

  return { getSealToken, clearSealToken }
}
