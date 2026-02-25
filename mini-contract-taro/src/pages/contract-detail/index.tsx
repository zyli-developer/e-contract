import { useState, useEffect } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
import { Button, Cell } from '@nutui/nutui-react-taro'
import { getContractDetail, cancelContract, deleteContract } from '@/api/contracts'
import './index.scss'

const STATUS_MAP: Record<number, { text: string; color: string }> = {
  1: { text: '草稿', color: '#999' },
  2: { text: '签署中', color: '#fa8c16' },
  3: { text: '已完成', color: '#00C28A' },
  4: { text: '已取消', color: '#ff4d4f' },
  5: { text: '已拒签', color: '#ff4d4f' },
  6: { text: '已过期', color: '#999' },
}

export default function ContractDetailPage() {
  const router = useRouter()
  const contractId = Number(router.params.id)
  const [detail, setDetail] = useState<any>(null)

  useEffect(() => {
    if (contractId) fetchDetail()
  }, [contractId])

  const fetchDetail = async () => {
    try {
      const data = await getContractDetail(contractId)
      setDetail(data)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '加载失败', icon: 'none' })
    }
  }

  const handleCancel = async () => {
    const res = await Taro.showModal({ title: '提示', content: '确定取消此合同？' })
    if (!res.confirm) return
    try {
      await cancelContract(contractId)
      Taro.showToast({ title: '已取消', icon: 'success' })
      fetchDetail()
    } catch (e: any) {
      Taro.showToast({ title: e.message || '操作失败', icon: 'none' })
    }
  }

  const handleDelete = async () => {
    const res = await Taro.showModal({ title: '提示', content: '确定删除此合同？删除后不可恢复。' })
    if (!res.confirm) return
    try {
      await deleteContract(contractId)
      Taro.showToast({ title: '已删除', icon: 'success' })
      setTimeout(() => Taro.navigateBack(), 1500)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '操作失败', icon: 'none' })
    }
  }

  const handleSign = () => {
    Taro.navigateTo({ url: `/pages/contract-sign/index?id=${contractId}` })
  }

  if (!detail) {
    return <View className='contract-detail'><Text>加载中...</Text></View>
  }

  const status = STATUS_MAP[detail.status] || { text: '未知', color: '#999' }

  return (
    <View className='contract-detail'>
      {/* 合同基本信息 */}
      <View className='detail-header'>
        <Text className='detail-name'>{detail.name}</Text>
        <Text className='detail-status' style={{ color: status.color }}>{status.text}</Text>
      </View>

      <View className='info-section'>
        <Cell title='创建时间' extra={detail.create_time || '-'} />
        {detail.remark && <Cell title='备注' extra={detail.remark} />}
      </View>

      {/* 签署方 */}
      {detail.participants?.length > 0 && (
        <View className='participants-section'>
          <Text className='section-title'>签署方</Text>
          {detail.participants.map((p: any, index: number) => (
            <View key={p.id || index} className='participant-item'>
              <View className='p-info'>
                <Text className='p-name'>{p.name || '未指定'}</Text>
                <Text className='p-mobile'>{p.mobile}</Text>
              </View>
              <Text className='p-status'>
                {p.status === 0 ? '待签署' : p.status === 2 ? '已签署' : '已拒签'}
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* 操作按钮 */}
      <View className='action-section'>
        {detail.status === 2 && (
          <Button type='primary' block onClick={handleSign}>去签署</Button>
        )}
        {detail.status <= 2 && (
          <Button block onClick={handleCancel} className='cancel-btn'>取消合同</Button>
        )}
        {(detail.status === 1 || detail.status === 4) && (
          <Button block onClick={handleDelete} className='delete-btn'>删除合同</Button>
        )}
      </View>
    </View>
  )
}
