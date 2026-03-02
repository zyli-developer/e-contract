/**
 * Contracts API 测试
 * 验证：sendSignCode/verifySignCode 已删除，executeSign 仍存在
 */
import { executeSign, rejectSign } from '@/api/contracts'

jest.mock('@/api/request', () => ({
  request: jest.fn().mockResolvedValue({}),
}))

const { request } = require('@/api/request')

beforeEach(() => {
  jest.clearAllMocks()
})

describe('contracts API', () => {
  test('sendSignCode 和 verifySignCode 不应存在', () => {
    const contractModule = require('@/api/contracts')
    expect(contractModule.sendSignCode).toBeUndefined()
    expect(contractModule.verifySignCode).toBeUndefined()
  })

  test('executeSign 仍然存在且调用正确', async () => {
    await executeSign(1)
    expect(request).toHaveBeenCalledWith({
      url: '/seal/sign-task/1/sign',
      method: 'POST',
      data: { seal_id: undefined },
    })
  })

  test('rejectSign 调用正确', async () => {
    await rejectSign(1, '不同意')
    expect(request).toHaveBeenCalledWith({
      url: '/seal/sign-task/1/reject',
      method: 'POST',
      data: { reason: '不同意' },
    })
  })
})
