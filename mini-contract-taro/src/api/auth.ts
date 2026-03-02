import { request } from './request'
import { encryptPassword } from '@/utils/crypto'

/** 密码登录（密码 RSA 加密传输） */
export async function login(data: { mobile: string; password: string }) {
  const encrypted = await encryptPassword(data.password)
  return request({ url: '/member/auth/login', method: 'POST', data: { mobile: data.mobile, password: encrypted }, isAuth: false })
}

/** 注册（密码 RSA 加密传输） */
export async function register(data: { mobile: string; password: string; nickname?: string; role?: string }) {
  const encrypted = await encryptPassword(data.password)
  return request({
    url: '/member/auth/register',
    method: 'POST',
    data: { mobile: data.mobile, password: encrypted, nickname: data.nickname, role: data.role },
    isAuth: false,
  })
}

/** 退出登录 */
export function logout() {
  return request({ url: '/member/auth/logout', method: 'POST' })
}
