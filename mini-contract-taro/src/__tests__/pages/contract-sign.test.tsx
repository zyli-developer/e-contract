/**
 * 合同签署页测试
 * 验证：合同内容展示、签名选择、签署/拒签流程
 */
import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'

const mockGetContractDetail = jest.fn()
const mockExecuteSign = jest.fn()
const mockRejectSign = jest.fn()
const mockGetTemplateDetail = jest.fn()
const mockGetSealList = jest.fn()

jest.mock('@/api/contracts', () => ({
  getContractDetail: (...args: any[]) => mockGetContractDetail(...args),
  executeSign: (...args: any[]) => mockExecuteSign(...args),
  rejectSign: (...args: any[]) => mockRejectSign(...args),
}))
jest.mock('@/api/templates', () => ({
  getTemplateDetail: (...args: any[]) => mockGetTemplateDetail(...args),
}))
jest.mock('@/api/seals', () => ({
  getSealList: (...args: any[]) => mockGetSealList(...args),
}))
jest.mock('@/hooks/useAuth', () => ({
  useRequireAuth: jest.fn(),
}))

import Taro, { useRouter } from '@tarojs/taro'

;(useRouter as jest.Mock).mockReturnValue({ params: { id: '1' } })

import ContractSignPage from '@/pages/contract-sign/index'

const mockDetail = {
  name: '测试合同',
  template_id: 1,
  variables: { partyAName: '张三' },
  participants: [
    { id: 1, name: '张三', mobile: '13800138000', status: 0 },
    { id: 2, name: '李四', mobile: '13900139000', status: 2 },
  ],
}

const mockSeals = {
  list: [
    { id: 10, name: '我的签名', type: 11, seal_data: 'data:image/png;base64,...', is_default: 1 },
  ],
}

beforeEach(() => {
  jest.clearAllMocks()
  ;(useRouter as jest.Mock).mockReturnValue({ params: { id: '1' } })
  mockGetContractDetail.mockResolvedValue(mockDetail)
  mockGetTemplateDetail.mockResolvedValue({ content: '<p>合同内容 {{partyAName}}</p>' })
  mockGetSealList.mockResolvedValue(mockSeals)
})

describe('ContractSignPage', () => {
  test('加载合同详情并显示签署方信息', async () => {
    await act(async () => {
      render(<ContractSignPage />)
    })
    await waitFor(() => {
      expect(screen.getByText('测试合同')).toBeInTheDocument()
      expect(screen.getByText('张三')).toBeInTheDocument()
      expect(screen.getByText('待签署')).toBeInTheDocument()
      expect(screen.getByText('已签署')).toBeInTheDocument()
    })
  })

  test('显示签名选择区域', async () => {
    await act(async () => {
      render(<ContractSignPage />)
    })
    await waitFor(() => {
      expect(screen.getByText('选择签名')).toBeInTheDocument()
      expect(screen.getByText('我的签名(默认)')).toBeInTheDocument()
    })
  })

  test('无签名时提示创建', async () => {
    mockGetSealList.mockResolvedValue({ list: [] })

    await act(async () => {
      render(<ContractSignPage />)
    })
    await waitFor(() => {
      expect(screen.getByText('您还没有签名，请先创建签名')).toBeInTheDocument()
    })
  })

  test('确认签署后调用 executeSign 并传入 sealId', async () => {
    ;(Taro.showModal as jest.Mock).mockResolvedValue({ confirm: true })
    mockExecuteSign.mockResolvedValue({})

    await act(async () => {
      render(<ContractSignPage />)
    })

    await waitFor(() => {
      expect(screen.getByText('确认签署')).toBeInTheDocument()
    })

    await act(async () => {
      fireEvent.click(screen.getByText('确认签署'))
    })

    await waitFor(() => {
      expect(mockExecuteSign).toHaveBeenCalledWith(1, 10)
      expect(Taro.showToast).toHaveBeenCalledWith({ title: '签署成功', icon: 'success' })
    })
  })

  test('拒签流程', async () => {
    ;(Taro.showModal as jest.Mock).mockResolvedValue({ confirm: true })
    mockRejectSign.mockResolvedValue({})

    await act(async () => {
      render(<ContractSignPage />)
    })

    await waitFor(() => {
      expect(screen.getByText('拒签')).toBeInTheDocument()
    })

    await act(async () => {
      fireEvent.click(screen.getByText('拒签'))
    })

    await waitFor(() => {
      expect(mockRejectSign).toHaveBeenCalledWith(1)
      expect(Taro.showToast).toHaveBeenCalledWith({ title: '已拒签', icon: 'success' })
    })
  })
})
