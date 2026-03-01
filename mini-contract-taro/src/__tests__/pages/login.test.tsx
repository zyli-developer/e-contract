/**
 * 登录页测试
 * 验证：仅密码登录，无短信登录 tab，有注册链接
 */
import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'

jest.mock('@/api/auth', () => ({
  login: jest.fn(),
}))
jest.mock('@/store/useAuthStore', () => ({
  useAuthStore: jest.fn(() => ({
    setTokens: jest.fn(),
    setUserId: jest.fn(),
  })),
}))
jest.mock('@/hooks/useAuth', () => ({
  useRequireAuth: jest.fn(),
}))

import Taro from '@tarojs/taro'
import { login } from '@/api/auth'
import LoginPage from '@/pages/login/index'

beforeEach(() => {
  jest.clearAllMocks()
})

describe('LoginPage', () => {
  test('渲染密码登录表单', () => {
    render(<LoginPage />)
    expect(screen.getByText('密码登录')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请输入11位手机号')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请输入登录密码')).toBeInTheDocument()
  })

  test('不渲染短信登录 tab', () => {
    render(<LoginPage />)
    expect(screen.queryByText('验证码登录')).not.toBeInTheDocument()
    expect(screen.queryByText('获取验证码')).not.toBeInTheDocument()
  })

  test('显示注册链接', () => {
    render(<LoginPage />)
    expect(screen.getByText('还没有账号？立即注册')).toBeInTheDocument()
  })

  test('点击注册链接跳转到注册页', () => {
    render(<LoginPage />)
    fireEvent.click(screen.getByText('还没有账号？立即注册'))
    expect(Taro.navigateTo).toHaveBeenCalledWith({ url: '/pages/register/index' })
  })

  test('空表单提交显示提示', () => {
    render(<LoginPage />)
    fireEvent.click(screen.getByText('登 录'))
    expect(Taro.showToast).toHaveBeenCalledWith({
      title: '请输入手机号和密码',
      icon: 'none',
    })
  })

  test('登录成功后设置 token 并跳转', async () => {
    const mockSetTokens = jest.fn()
    const mockSetUserId = jest.fn()
    const { useAuthStore } = require('@/store/useAuthStore')
    useAuthStore.mockReturnValue({ setTokens: mockSetTokens, setUserId: mockSetUserId })
    ;(login as jest.Mock).mockResolvedValue({
      accessToken: 'at',
      refreshToken: 'rt',
      userId: 1,
    })

    render(<LoginPage />)
    fireEvent.change(screen.getByPlaceholderText('请输入11位手机号'), {
      target: { value: '13800138000' },
    })
    fireEvent.change(screen.getByPlaceholderText('请输入登录密码'), {
      target: { value: 'test123' },
    })
    fireEvent.click(screen.getByText('登 录'))

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith({ mobile: '13800138000', password: 'test123' })
      expect(mockSetTokens).toHaveBeenCalledWith('at', 'rt')
      expect(mockSetUserId).toHaveBeenCalledWith(1)
    })
  })

  test('登录失败显示错误信息', async () => {
    ;(login as jest.Mock).mockRejectedValue(new Error('密码错误'))

    render(<LoginPage />)
    fireEvent.change(screen.getByPlaceholderText('请输入11位手机号'), {
      target: { value: '13800138000' },
    })
    fireEvent.change(screen.getByPlaceholderText('请输入登录密码'), {
      target: { value: 'wrong' },
    })
    fireEvent.click(screen.getByText('登 录'))

    await waitFor(() => {
      expect(Taro.showToast).toHaveBeenCalledWith({
        title: '密码错误',
        icon: 'none',
      })
    })
  })
})
