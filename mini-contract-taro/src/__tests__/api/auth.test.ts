/**
 * Auth API 测试
 * 验证：login、register、logout 函数签名正确，smsLogin/sendSmsCode 已删除
 */
import { login, register, logout } from '@/api/auth'

jest.mock('@/api/request', () => ({
  request: jest.fn().mockResolvedValue({ accessToken: 'at', refreshToken: 'rt', userId: 1 }),
}))

const { request } = require('@/api/request')

beforeEach(() => {
  jest.clearAllMocks()
})

describe('auth API', () => {
  test('login 调用正确的 URL 和参数', async () => {
    await login({ mobile: '13800138000', password: 'test123' })
    expect(request).toHaveBeenCalledWith({
      url: '/member/auth/login',
      method: 'POST',
      data: { mobile: '13800138000', password: 'test123' },
      isAuth: false,
    })
  })

  test('register 调用正确的 URL 和参数', async () => {
    await register({ mobile: '13800138000', password: 'test123', nickname: 'test' })
    expect(request).toHaveBeenCalledWith({
      url: '/member/auth/register',
      method: 'POST',
      data: { mobile: '13800138000', password: 'test123', nickname: 'test' },
      isAuth: false,
    })
  })

  test('register 昵称为可选参数', async () => {
    await register({ mobile: '13800138000', password: 'test123' })
    expect(request).toHaveBeenCalledWith({
      url: '/member/auth/register',
      method: 'POST',
      data: { mobile: '13800138000', password: 'test123' },
      isAuth: false,
    })
  })

  test('logout 调用正确的 URL', async () => {
    await logout()
    expect(request).toHaveBeenCalledWith({
      url: '/member/auth/logout',
      method: 'POST',
    })
  })

  test('smsLogin 和 sendSmsCode 不应存在', () => {
    const authModule = require('@/api/auth')
    expect(authModule.smsLogin).toBeUndefined()
    expect(authModule.sendSmsCode).toBeUndefined()
  })
})
