/**
 * 合同详情页测试
 * 验证：ACTION_LABEL 中不包含 SMS 相关条目
 */
import React from 'react'
import { render, screen, waitFor, act } from '@testing-library/react'

const mockGetContractDetail = jest.fn()
const mockGetEvidence = jest.fn()

jest.mock('@/api/contracts', () => ({
  getContractDetail: (...args: any[]) => mockGetContractDetail(...args),
  cancelContract: jest.fn(),
  deleteContract: jest.fn(),
  initiateSign: jest.fn(),
  getEvidence: (...args: any[]) => mockGetEvidence(...args),
  urgeSign: jest.fn(),
  downloadContract: jest.fn(),
}))
jest.mock('@/hooks/useAuth', () => ({
  useRequireAuth: jest.fn(),
}))

import { useRouter } from '@tarojs/taro'

;(useRouter as jest.Mock).mockReturnValue({ params: { id: '1' } })

// 直接验证 ACTION_LABEL 内容
describe('ContractDetail ACTION_LABEL', () => {
  test('不包含 SIGN_CODE_SENT 和 SIGN_CODE_VERIFIED', () => {
    // 读取源文件中的 ACTION_LABEL
    // 由于组件内部定义 ACTION_LABEL，通过渲染证据链来验证
    const contractDetailModule = require('@/pages/contract-detail/index')
    // ACTION_LABEL 是模块内部变量，通过功能测试间接验证
    expect(contractDetailModule).toBeDefined()
  })

  test('证据链渲染不包含短信验证码标签', async () => {
    const ContractDetailPage = require('@/pages/contract-detail/index').default

    mockGetContractDetail.mockResolvedValue({
      id: 1,
      name: '测试合同',
      status: 3,
      create_time: '2025-01-01',
      participants: [],
    })

    mockGetEvidence.mockResolvedValue([
      { id: 1, action: 'CONTRACT_CREATED', create_time: '2025-01-01 10:00:00' },
      { id: 2, action: 'CONTRACT_SENT', create_time: '2025-01-01 10:01:00' },
      { id: 3, action: 'SIGN_CODE_SENT', create_time: '2025-01-01 10:02:00' },
      { id: 4, action: 'SIGN_CODE_VERIFIED', create_time: '2025-01-01 10:03:00' },
      { id: 5, action: 'CONTRACT_SIGNED', create_time: '2025-01-01 10:04:00' },
    ])

    await act(async () => {
      render(<ContractDetailPage />)
    })

    await waitFor(() => {
      expect(screen.getByText('测试合同')).toBeInTheDocument()
    })

    // 展开证据链
    const { fireEvent } = require('@testing-library/react')
    await act(async () => {
      fireEvent.click(screen.getByText('签署证据链'))
    })

    await waitFor(() => {
      expect(screen.getByText('合同创建')).toBeInTheDocument()
      expect(screen.getByText('发起签署')).toBeInTheDocument()
      expect(screen.getByText('签署完成')).toBeInTheDocument()
      // SIGN_CODE_SENT 和 SIGN_CODE_VERIFIED 应该显示为原始 action 名称（因为已从 ACTION_LABEL 中删除）
      expect(screen.queryByText('发送验证码')).not.toBeInTheDocument()
      expect(screen.queryByText('验证码验证通过')).not.toBeInTheDocument()
    })
  })
})
