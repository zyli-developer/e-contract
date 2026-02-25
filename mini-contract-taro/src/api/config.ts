/** API 基础配置 */

export const BASE_URL =
  process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000/app-api'
    : '/app-api'

export const SEAL_H5_URL =
  process.env.NODE_ENV === 'development'
    ? 'http://localhost:3100'
    : 'https://h5-sign.leepm.com'

export const DEFAULT_TIMEOUT = 30000
export const AI_TIMEOUT = 180000
export const TENANT_ID = '1'
