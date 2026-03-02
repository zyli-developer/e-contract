/**
 * 注册页测试
 * 验证：表单验证、注册成功自动登录、返回登录链接
 */
import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'

jest.mock('@/api/auth', () => ({
  register: jest.fn(),
  login: jest.fn(),
}))
jest.mock('@/store/useAuthStore', () => ({
  useAuthStore: jest.fn(() => ({
    setTokens: jest.fn(),
    setUserId: jest.fn(),
  })),
}))

import Taro from '@tarojs/taro'
import { register, login } from '@/api/auth'
import RegisterPage from '@/pages/register/index'

beforeEach(() => {
  jest.clearAllMocks()
})

describe('RegisterPage', () => {
  test('渲染所有表单字段', () => {
    render(<RegisterPage />)
    expect(screen.getByText('创建账号')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请输入11位手机号')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请输入密码（至少6位）')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请再次输入密码')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请输入昵称')).toBeInTheDocument()
  })

  test('昵称标记为选填', () => {
    render(<RegisterPage />)
    expect(screen.getByText('昵称（选填）')).toBeInTheDocument()
  })

  test('显示返回登录链接', () => {
    render(<RegisterPage />)
    expect(screen.getByText('已有账号？返回登录')).toBeInTheDocument()
  })

  test('点击返回登录', () => {
    render(<RegisterPage />)
    fireEvent.click(screen.getByText('已有账号？返回登录'))
    expect(Taro.navigateBack).toHaveBeenCalled()
  })

  test('手机号不足11位提示', () => {
    render(<RegisterPage />)
    fireEvent.change(screen.getByPlaceholderText('请输入11位手机号'), {
      target: { value: '1380013' },
    })
    fireEvent.click(screen.getByText('注 册'))
    expect(Taro.showToast).toHaveBeenCalledWith({
      title: '请输入11位手机号',
      icon: 'none',
    })
  })

  test('密码不足6位提示', () => {
    render(<RegisterPage />)
    fireEvent.change(screen.getByPlaceholderText('请输入11位手机号'), {
      target: { value: '13800138000' },
    })
    fireEvent.change(screen.getByPlaceholderText('请输入密码（至少6位）'), {
      target: { value: '123' },
    })
    fireEvent.click(screen.getByText('注 册'))
    expect(Taro.showToast).toHaveBeenCalledWith({
      title: '密码长度不能少于6位',
      icon: 'none',
    })
  })

  test('两次密码不一致提示', () => {
    render(<RegisterPage />)
    fireEvent.change(screen.getByPlaceholderText('请输入11位手机号'), {
      target: { value: '13800138000' },
    })
    fireEvent.change(screen.getByPlaceholderText('请输入密码（至少6位）'), {
      target: { value: 'test123' },
    })
    fireEvent.change(screen.getByPlaceholderText('请再次输入密码'), {
      target: { value: 'test456' },
    })
    fireEvent.click(screen.getByText('注 册'))
    expect(Taro.showToast).toHaveBeenCalledWith({
      title: '两次密码输入不一致',
      icon: 'none',
    })
  })

  test('注册成功后自动登录并跳转首页', async () => {
    const mockSetTokens = jest.fn()
    const mockSetUserId = jest.fn()
    const { useAuthStore } = require('@/store/useAuthStore')
    useAuthStore.mockReturnValue({ setTokens: mockSetTokens, setUserId: mockSetUserId })

    ;(register as jest.Mock).mockResolvedValue({})
    ;(login as jest.Mock).mockResolvedValue({
      accessToken: 'at',
      refreshToken: 'rt',
      userId: 1,
    })

    render(<RegisterPage />)
    fireEvent.change(screen.getByPlaceholderText('请输入11位手机号'), {
      target: { value: '13800138000' },
    })
    fireEvent.change(screen.getByPlaceholderText('请输入密码（至少6位）'), {
      target: { value: 'test123' },
    })
    fireEvent.change(screen.getByPlaceholderText('请再次输入密码'), {
      target: { value: 'test123' },
    })
    fireEvent.click(screen.getByText('注 册'))

    await waitFor(() => {
      expect(register).toHaveBeenCalledWith({
        mobile: '13800138000',
        password: 'test123',
        nickname: undefined,
      })
      expect(login).toHaveBeenCalledWith({ mobile: '13800138000', password: 'test123' })
      expect(mockSetTokens).toHaveBeenCalledWith('at', 'rt')
      expect(Taro.switchTab).toHaveBeenCalledWith({ url: '/pages/index/index' })
    })
  })

  test('注册时可传入昵称', async () => {
    ;(register as jest.Mock).mockResolvedValue({})
    ;(login as jest.Mock).mockResolvedValue({
      accessToken: 'at',
      refreshToken: 'rt',
      userId: 1,
    })

    render(<RegisterPage />)
    fireEvent.change(screen.getByPlaceholderText('请输入11位手机号'), {
      target: { value: '13800138000' },
    })
    fireEvent.change(screen.getByPlaceholderText('请输入密码（至少6位）'), {
      target: { value: 'test123' },
    })
    fireEvent.change(screen.getByPlaceholderText('请再次输入密码'), {
      target: { value: 'test123' },
    })
    fireEvent.change(screen.getByPlaceholderText('请输入昵称'), {
      target: { value: '小明' },
    })
    fireEvent.click(screen.getByText('注 册'))

    await waitFor(() => {
      expect(register).toHaveBeenCalledWith({
        mobile: '13800138000',
        password: 'test123',
        nickname: '小明',
      })
    })
  })

  test('注册失败显示错误信息', async () => {
    ;(register as jest.Mock).mockRejectedValue(new Error('手机号已注册'))

    render(<RegisterPage />)
    fireEvent.change(screen.getByPlaceholderText('请输入11位手机号'), {
      target: { value: '13800138000' },
    })
    fireEvent.change(screen.getByPlaceholderText('请输入密码（至少6位）'), {
      target: { value: 'test123' },
    })
    fireEvent.change(screen.getByPlaceholderText('请再次输入密码'), {
      target: { value: 'test123' },
    })
    fireEvent.click(screen.getByText('注 册'))

    await waitFor(() => {
      expect(Taro.showToast).toHaveBeenCalledWith({
        title: '手机号已注册',
        icon: 'none',
      })
    })
  })
})
