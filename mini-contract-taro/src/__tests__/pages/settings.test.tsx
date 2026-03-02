/**
 * 设置页测试
 * 验证：密码修改使用确认密码而非验证码
 */
import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'

const mockUpdatePassword = jest.fn()

jest.mock('@/api/member', () => ({
  updateUserInfo: jest.fn().mockResolvedValue({}),
  updatePassword: (...args: any[]) => mockUpdatePassword(...args),
}))
jest.mock('@/store/useAuthStore', () => ({
  useAuthStore: jest.fn(() => ({
    userInfo: { nickname: 'test', avatar: '', mobile: '13800138000' },
    setUserInfo: jest.fn(),
  })),
}))
jest.mock('@/hooks/useAuth', () => ({
  useRequireAuth: jest.fn(),
}))

import Taro from '@tarojs/taro'
import SettingsPage from '@/pages/profile/settings/index'

beforeEach(() => {
  jest.clearAllMocks()
})

describe('SettingsPage', () => {
  test('显示用户手机号', () => {
    render(<SettingsPage />)
    expect(screen.getByText('13800138000')).toBeInTheDocument()
  })

  test('不显示短信验证码相关 UI', () => {
    render(<SettingsPage />)
    expect(screen.queryByText('获取验证码')).not.toBeInTheDocument()
    expect(screen.queryByPlaceholderText('请输入验证码')).not.toBeInTheDocument()
  })

  test('展开密码表单后显示确认密码字段', () => {
    render(<SettingsPage />)
    fireEvent.click(screen.getByText('修改密码'))
    expect(screen.getByPlaceholderText('请输入新密码（至少 6 位）')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('请再次输入新密码')).toBeInTheDocument()
  })

  test('密码不足6位提示', () => {
    render(<SettingsPage />)
    fireEvent.click(screen.getByText('修改密码'))
    fireEvent.change(screen.getByPlaceholderText('请输入新密码（至少 6 位）'), {
      target: { value: '123' },
    })
    fireEvent.click(screen.getByText('确认修改'))
    expect(Taro.showToast).toHaveBeenCalledWith({
      title: '密码长度不能少于 6 位',
      icon: 'none',
    })
  })

  test('两次密码不一致提示', () => {
    render(<SettingsPage />)
    fireEvent.click(screen.getByText('修改密码'))
    fireEvent.change(screen.getByPlaceholderText('请输入新密码（至少 6 位）'), {
      target: { value: 'test123' },
    })
    fireEvent.change(screen.getByPlaceholderText('请再次输入新密码'), {
      target: { value: 'test456' },
    })
    fireEvent.click(screen.getByText('确认修改'))
    expect(Taro.showToast).toHaveBeenCalledWith({
      title: '两次密码输入不一致',
      icon: 'none',
    })
  })

  test('密码一致时调用 updatePassword with confirmPassword', async () => {
    mockUpdatePassword.mockResolvedValue({})

    render(<SettingsPage />)
    fireEvent.click(screen.getByText('修改密码'))
    fireEvent.change(screen.getByPlaceholderText('请输入新密码（至少 6 位）'), {
      target: { value: 'newpwd123' },
    })
    fireEvent.change(screen.getByPlaceholderText('请再次输入新密码'), {
      target: { value: 'newpwd123' },
    })
    fireEvent.click(screen.getByText('确认修改'))

    await waitFor(() => {
      expect(mockUpdatePassword).toHaveBeenCalledWith({
        password: 'newpwd123',
        confirmPassword: 'newpwd123',
      })
      expect(Taro.showToast).toHaveBeenCalledWith({
        title: '密码修改成功',
        icon: 'success',
      })
    })
  })
})
