import { request } from './request'
import { encryptPassword } from '@/utils/crypto'

/** 获取当前用户信息 */
export function getUserInfo() {
  return request<{
    id: number
    mobile: string
    nickname: string | null
    avatar: string | null
    real_name_verified: number
    real_name: string | null
  }>({ url: '/member/user/get' })
}

/** 更新用户信息 */
export function updateUserInfo(data: { nickname?: string; avatar?: string }) {
  return request({ url: '/member/user/update', method: 'PUT', data })
}

/** 修改密码（密码 RSA 加密传输） */
export async function updatePassword(data: { password: string; confirmPassword: string }) {
  const encPwd = await encryptPassword(data.password)
  const encConfirm = await encryptPassword(data.confirmPassword)
  return request({ url: '/member/user/update-password', method: 'PUT', data: { password: encPwd, confirmPassword: encConfirm } })
}

/** 实名认证 */
export function verifyRealName(data: {
  real_name: string
  id_card: string
  id_card_front_url: string
  id_card_back_url: string
}) {
  return request({ url: '/member/user/verify-realname', method: 'POST', data })
}
