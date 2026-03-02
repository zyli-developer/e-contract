/** API 基础配置 */

// 开发环境：真机调试时需改为电脑的局域网 IP（手机无法访问 localhost）
const DEV_HOST = '192.168.77.10'

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

/** 服务器根地址（不含 /app-api），用于拼接静态资源绝对路径 */
export const SERVER_BASE =
  process.env.NODE_ENV === 'development'
    ? `http://${DEV_HOST}:8000`
    : ''

/**
 * 将服务端返回的相对路径（如 /static/uploads/...）转为小程序可用的绝对 URL。
 * 已经是绝对 URL 或 data: 开头的不做处理。
 */
export function resolveStaticUrl(url: string | undefined | null): string {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('data:')) return url
  return `${SERVER_BASE}${url}`
}
