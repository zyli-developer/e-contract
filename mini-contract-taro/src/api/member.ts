import { request } from './request'

/** 获取当前用户信息 */
export function getUserInfo() {
  return request<{
    id: number
    mobile: string
    nickname: string | null
    avatar: string | null
  }>({ url: '/member/user/get' })
}

/** 更新用户信息 */
export function updateUserInfo(data: { nickname?: string; avatar?: string }) {
  return request({ url: '/member/user/update', method: 'PUT', data })
}

/** 修改密码 */
export function updatePassword(data: { password: string; code: string }) {
  return request({ url: '/member/user/update-password', method: 'PUT', data })
}
