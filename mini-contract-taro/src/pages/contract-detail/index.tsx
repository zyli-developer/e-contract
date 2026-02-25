import { useState, useEffect } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
import { Button, Cell } from '@nutui/nutui-react-taro'
import { useRequireAuth } from '@/hooks/useAuth'
import {
  getContractDetail,
  cancelContract,
  deleteContract,
  initiateSign,
  getEvidence,
  urgeSign,
  downloadContract,
} from '@/api/contracts'
import './index.scss'

const STATUS_MAP: Record<number, { text: string; color: string }> = {
  1: { text: '草稿', color: '#999' },
  2: { text: '签署中', color: '#fa8c16' },
  3: { text: '已完成', color: '#00C28A' },
  4: { text: '已取消', color: '#ff4d4f' },
  5: { text: '已拒签', color: '#ff4d4f' },
  6: { text: '已过期', color: '#999' },
}

const ACTION_LABEL: Record<string, string> = {
  CONTRACT_CREATED: '合同创建',
  CONTRACT_SENT: '发起签署',
  SIGNER_VIEWED: '查看合同',
  SIGN_CODE_SENT: '发送验证码',
  SIGN_CODE_VERIFIED: '验证码验证通过',
  CONTRACT_SIGNED: '签署完成',
  CONTRACT_COMPLETED: '合同完成',
  CONTRACT_CANCELLED: '合同取消',
  CONTRACT_REJECTED: '拒签',
}

export default function ContractDetailPage() {
  useRequireAuth()
  const router = useRouter()
  const contractId = Number(router.params.id)
  const [detail, setDetail] = useState<any>(null)
  const [evidenceList, setEvidenceList] = useState<any[]>([])
  const [showEvidence, setShowEvidence] = useState(false)

  useEffect(() => {
    if (contractId) {
      fetchDetail()
    }
  }, [contractId])

  const fetchDetail = async () => {
    try {
      const data = await getContractDetail(contractId)
      setDetail(data)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '加载失败', icon: 'none' })
    }
  }

  const fetchEvidence = async () => {
    try {
      const data = await getEvidence(contractId)
      setEvidenceList(data || [])
      setShowEvidence(true)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取证据链失败', icon: 'none' })
    }
  }

  const handleInitiate = async () => {
    const res = await Taro.showModal({ title: '提示', content: '确定发起签署？签署方将收到通知。' })
    if (!res.confirm) return
    try {
      await initiateSign(contractId)
      Taro.showToast({ title: '已发起签署', icon: 'success' })
      fetchDetail()
    } catch (e: any) {
      Taro.showToast({ title: e.message || '操作失败', icon: 'none' })
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

  const handleUrge = async () => {
    try {
      await urgeSign(contractId)
      Taro.showToast({ title: '催签通知已发送', icon: 'success' })
    } catch (e: any) {
      Taro.showToast({ title: e.message || '操作失败', icon: 'none' })
    }
  }

  const handleDownload = async () => {
    try {
      const data = await downloadContract(contractId)
      const fileUrl = data?.signed_file_url || data?.file_url
      if (fileUrl) {
        await Taro.downloadFile({ url: fileUrl })
        Taro.showToast({ title: '下载成功', icon: 'success' })
      } else {
        Taro.showToast({ title: '暂无可下载文件', icon: 'none' })
      }
    } catch (e: any) {
      Taro.showToast({ title: e.message || '下载失败', icon: 'none' })
    }
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
        {detail.complete_time && <Cell title='完成时间' extra={detail.complete_time} />}
        {detail.remark && <Cell title='备注' extra={detail.remark} />}
        {detail.file_hash && <Cell title='文档哈希' extra={detail.file_hash.slice(0, 16) + '...'} />}
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

      {/* 证据链 */}
      <View className='evidence-section'>
        <View className='evidence-header' onClick={fetchEvidence}>
          <Text className='section-title'>证据链</Text>
          <Text className='toggle-btn'>{showEvidence ? '收起' : '展开'}</Text>
        </View>
        {showEvidence && (
          <View className='evidence-timeline'>
            {evidenceList.length === 0 ? (
              <Text className='no-evidence'>暂无记录</Text>
            ) : (
              evidenceList.map((log: any) => (
                <View key={log.id} className='timeline-item'>
                  <View className='timeline-dot' />
                  <View className='timeline-content'>
                    <Text className='timeline-action'>{ACTION_LABEL[log.action] || log.action}</Text>
                    <Text className='timeline-time'>{log.create_time}</Text>
                    {log.ip && <Text className='timeline-ip'>IP: {log.ip}</Text>}
                  </View>
                </View>
              ))
            )}
          </View>
        )}
      </View>

      {/* 操作按钮 */}
      <View className='action-section'>
        {detail.status === 1 && (
          <Button type='primary' block onClick={handleInitiate}>发起签署</Button>
        )}
        {detail.status === 2 && (
          <Button type='primary' block onClick={handleSign}>去签署</Button>
        )}
        {detail.status === 2 && (
          <Button block onClick={handleUrge}>催签</Button>
        )}
        {detail.status === 3 && (
          <Button type='primary' block onClick={handleDownload}>下载合同</Button>
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
