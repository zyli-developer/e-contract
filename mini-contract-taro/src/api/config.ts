/** API 基础配置 */

// 开发环境：真机调试时需改为电脑的局域网 IP（手机无法访问 localhost）
const DEV_HOST = '192.168.10.7'

export const BASE_URL =
  process.env.NODE_ENV === 'development'
    ? `http://${DEV_HOST}:8000/app-api`
    : '/app-api'

/** 第三方 H5 签署服务地址 */
export const SIGN_H5_URL =
  process.env.NODE_ENV === 'development'
    ? `http://${DEV_HOST}:3100`
    : 'https://h5-sign.leepm.com'

export const DEFAULT_TIMEOUT = 30000
