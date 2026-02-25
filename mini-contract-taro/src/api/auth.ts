import { request } from './request'

/** 密码登录 */
export function login(data: { mobile: string; password: string }) {
  return request({ url: '/api/v1/member/auth/login', method: 'POST', data, isAuth: false })
}

/** 短信验证码登录 */
export function smsLogin(data: { mobile: string; code: string }) {
  return request({ url: '/api/v1/member/auth/sms-login', method: 'POST', data, isAuth: false })
}

/** 发送短信验证码 */
export function sendSmsCode(data: { mobile: string; scene: number }) {
  return request({ url: '/api/v1/member/auth/send-sms-code', method: 'POST', data, isAuth: false })
}

/** 社交登录 */
export function socialLogin(data: { type: number; code: string; state?: string }) {
  return request({ url: '/api/v1/member/auth/social-login', method: 'POST', data, isAuth: false })
}

/** 退出登录 */
export function logout() {
  return request({ url: '/api/v1/member/auth/logout', method: 'POST' })
}
