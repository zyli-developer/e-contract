/**
 * Member API 测试
 * 验证：updatePassword 使用 confirmPassword 而非 code
 */
import { updatePassword, updateUserInfo } from '@/api/member'

jest.mock('@/api/request', () => ({
  request: jest.fn().mockResolvedValue({}),
}))

const { request } = require('@/api/request')

beforeEach(() => {
  jest.clearAllMocks()
})

describe('member API', () => {
  test('updatePassword 使用 confirmPassword 参数', async () => {
    await updatePassword({ password: 'newpwd123', confirmPassword: 'newpwd123' })
    expect(request).toHaveBeenCalledWith({
      url: '/member/user/update-password',
      method: 'PUT',
      data: { password: 'newpwd123', confirmPassword: 'newpwd123' },
    })
  })

  test('updateUserInfo 调用正确', async () => {
    await updateUserInfo({ nickname: 'test' })
    expect(request).toHaveBeenCalledWith({
      url: '/member/user/update',
      method: 'PUT',
      data: { nickname: 'test' },
    })
  })
})
