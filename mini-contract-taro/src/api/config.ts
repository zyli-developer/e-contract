/** API 基础配置 */

export const BASE_URL =
  process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000/app-api'
    : '/app-api'

/** 第三方 H5 签署服务地址 */
export const SIGN_H5_URL =
  process.env.NODE_ENV === 'development'
    ? 'http://localhost:3100'
    : 'https://h5-sign.leepm.com'

export const DEFAULT_TIMEOUT = 30000
