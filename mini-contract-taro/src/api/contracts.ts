import { request } from './request'

/** 合同统计 */
export function getStatistics() {
  return request({ url: '/api/v1/seal/sign-task/statistics' })
}

/** 合同列表 */
export function getContractList(params: Record<string, any>) {
  return request({ url: '/api/v1/seal/sign-task/page', data: params })
}

/** 合同详情 */
export function getContractDetail(id: string | number) {
  return request({ url: `/api/v1/seal/sign-task/get?id=${id}` })
}

/** 创建合同 */
export function createContract(data: Record<string, any>) {
  return request({ url: '/api/v1/seal/sign-task/create', method: 'POST', data })
}

/** 取消合同 */
export function cancelContract(id: string | number) {
  return request({ url: `/api/v1/seal/sign-task/cancel?id=${id}`, method: 'DELETE' })
}

/** 删除合同 */
export function deleteContract(id: string | number) {
  return request({ url: `/api/v1/seal/sign-task/delete?id=${id}`, method: 'DELETE' })
}

/** 催签 */
export function urgeSign(id: string | number) {
  return request({ url: `/api/v1/seal/sign-task/${id}/urge`, method: 'POST' })
}
