import { request } from './request'

/** 合同统计 */
export function getStatistics() {
  return request({ url: '/seal/sign-task/statistics' })
}

/** 合同列表 */
export function getContractList(params: Record<string, any>) {
  return request({ url: '/seal/sign-task/page', data: params })
}

/** 合同详情 */
export function getContractDetail(id: string | number) {
  return request({ url: `/seal/sign-task/get?id=${id}` })
}

/** 创建合同 */
export function createContract(data: Record<string, any>) {
  return request({ url: '/seal/sign-task/create', method: 'POST', data })
}

/** 取消合同 */
export function cancelContract(id: string | number) {
  return request({ url: `/seal/sign-task/cancel?id=${id}`, method: 'DELETE' })
}

/** 删除合同 */
export function deleteContract(id: string | number) {
  return request({ url: `/seal/sign-task/delete?id=${id}`, method: 'DELETE' })
}

/** 催签 */
export function urgeSign(id: string | number) {
  return request({ url: `/seal/sign-task/${id}/urge`, method: 'POST' })
}

/** 发起签署（草稿 → 签署中）*/
export function initiateSign(id: string | number) {
  return request({ url: `/seal/sign-task/${id}/initiate`, method: 'POST' })
}

/** 执行签署 */
export function executeSign(id: string | number, sealId?: number, variables?: Record<string, string>) {
  return request({ url: `/seal/sign-task/${id}/sign`, method: 'POST', data: { seal_id: sealId, variables } })
}

/** 拒签 */
export function rejectSign(id: string | number, reason?: string) {
  return request({ url: `/seal/sign-task/${id}/reject`, method: 'POST', data: { reason } })
}

/** 获取证据链 */
export function getEvidence(id: string | number) {
  return request({ url: `/seal/sign-task/${id}/evidence` })
}

/** 校验文档哈希 */
export function verifyHash(id: string | number) {
  return request({ url: `/seal/sign-task/${id}/verify-hash` })
}

/** 验证权限 */
export function validatePermission(id: string | number) {
  return request({ url: `/seal/sign-task/validate-permission?id=${id}` })
}

/** 下载已签署合同 */
export function downloadContract(id: string | number) {
  return request({ url: `/seal/sign-task/${id}/download` })
}
