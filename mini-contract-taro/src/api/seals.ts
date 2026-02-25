import { request } from './request'

/** 印章列表 */
export function getSealList(params: Record<string, any>) {
  return request({ url: '/seal/seal-info/page', data: params })
}

/** 创建印章 */
export function createSeal(data: Record<string, any>) {
  return request({ url: '/seal/seal-info/create', method: 'POST', data })
}

/** 删除印章 */
export function deleteSeal(id: string | number) {
  return request({ url: `/seal/seal-info/delete?id=${id}`, method: 'DELETE' })
}

/** 设为默认 */
export function setDefaultSeal(id: string | number) {
  return request({ url: `/seal/seal-info/set-default?id=${id}`, method: 'PUT' })
}
