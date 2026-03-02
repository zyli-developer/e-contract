import { useState, useEffect } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import { View, Text, RichText, ScrollView, Image } from '@tarojs/components'
import { useRequireAuth } from '@/hooks/useAuth'
import { useAuthStore } from '@/store/useAuthStore'
import {
  getContractDetail,
  cancelContract,
  deleteContract,
  initiateSign,
  getEvidence,
  urgeSign,
  downloadContract,
} from '@/api/contracts'
import { getTemplateDetail } from '@/api/templates'
import { resolveStaticUrl } from '@/api/config'
import './index.scss'

const STATUS_MAP: Record<number, { text: string; type: string }> = {
  1: { text: '草稿', type: 'default' },
  2: { text: '签署中', type: 'warning' },
  3: { text: '已完成', type: 'success' },
  4: { text: '已取消', type: 'danger' },
  5: { text: '已拒签', type: 'danger' },
  6: { text: '已过期', type: 'default' },
}

const ACTION_LABEL: Record<string, string> = {
  CONTRACT_CREATED: '合同创建',
  CONTRACT_SENT: '发起签署',
  SIGNER_VIEWED: '查看合同',
  CONTRACT_SIGNED: '签署完成',
  CONTRACT_COMPLETED: '合同完成',
  CONTRACT_CANCELLED: '合同取消',
  CONTRACT_REJECTED: '拒签',
}

export default function ContractDetailPage() {
  useRequireAuth()
  const router = useRouter()
  const contractId = Number(router.params.id)
  const { role } = useAuthStore()
  const [detail, setDetail] = useState<any>(null)
  const [evidenceList, setEvidenceList] = useState<any[]>([])
  const [showEvidence, setShowEvidence] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [contractHtml, setContractHtml] = useState<string>('')

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
    if (showEvidence) {
      setShowEvidence(false)
      return
    }
    try {
      const data = await getEvidence(contractId)
      setEvidenceList(data || [])
      setShowEvidence(true)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取证据链失败', icon: 'none' })
    }
  }

  const buildSignatureHtml = (party: 'A' | 'B') => {
    const participants = detail?.participants || []
    // 甲方=order_num 1, 乙方=order_num 2
    const orderNum = party === 'A' ? 1 : 2
    const p = participants.find((item: any) => item.order_num === orderNum)
    if (!p) return '<p style="color:#ccc">（未指定签署方）</p>'
    if (p.status === 2 && p.seal_data) {
      return `<div><img src="${resolveStaticUrl(p.seal_data)}" style="max-width:150px;max-height:80px;" /></div>`
    }
    if (p.status === 2) {
      return `<p>${p.name || ''}（已签署）</p>`
    }
    return '<p style="color:#ccc">（待签署）</p>'
  }

  const handlePreview = async () => {
    if (showPreview) {
      setShowPreview(false)
      return
    }
    if (!detail?.template_id) return
    try {
      const tpl = await getTemplateDetail(detail.template_id)
      if (tpl?.content) {
        let html = tpl.content as string
        const vars = detail.variables || {}
        // 统一替换所有占位符（签章 + 普通变量）
        html = html.replace(/\{\{(\w+)\}\}/g, (_match: string, varName: string) => {
          if (varName === 'partyASignature') return buildSignatureHtml('A')
          if (varName === 'partyBSignature') return buildSignatureHtml('B')
          return vars[varName] || '<span style="color:#ccc">未填写</span>'
        })
        setContractHtml(html)
      }
      setShowPreview(true)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '加载合同内容失败', icon: 'none' })
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
    // 模板合同没有实际文件，使用预览方式查看完整合同
    if (detail?.template_id) {
      handlePreview()
      return
    }
    try {
      const data = await downloadContract(contractId)
      const fileUrl = data?.signed_file_url || data?.file_url
      if (fileUrl) {
        const downloadRes = await Taro.downloadFile({ url: fileUrl })
        if (downloadRes.statusCode === 200) {
          await Taro.openDocument({ filePath: downloadRes.tempFilePath })
        }
      } else {
        Taro.showToast({ title: '暂无可下载文件', icon: 'none' })
      }
    } catch (e: any) {
      Taro.showToast({ title: e.message || '下载失败', icon: 'none' })
    }
  }

  if (!detail) {
    return (
      <View className='contract-detail loading-state'>
        <Text>数据加载中...</Text>
      </View>
    )
  }

  const status = STATUS_MAP[detail.status] || { text: '未知', type: 'default' }

  return (
    <View className='contract-detail'>
      {/* 顶部状态卡片 */}
      <View className='status-header-card'>
        <View className='header-top'>
          <Text className='contract-name'>{detail.name}</Text>
          <Text className={`status-tag status-tag-${status.type} tag-large`}>{status.text}</Text>
        </View>
        <View className='header-info'>
          <Text className='info-label'>合同编号：</Text>
          <Text className='info-value'>{detail.id}</Text>
        </View>
      </View>

      <View className='detail-container'>
        <View className='info-group'>
          <Text className='group-title'>基本信息</Text>
          <View className='cell-row'>
            <Text className='cell-title'>创建时间</Text>
            <Text className='cell-extra'>{detail.create_time || '-'}</Text>
          </View>
          {detail.complete_time && (
            <View className='cell-row'>
              <Text className='cell-title'>完成时间</Text>
              <Text className='cell-extra'>{detail.complete_time}</Text>
            </View>
          )}
          {detail.remark && (
            <View className='cell-row'>
              <Text className='cell-title'>备注</Text>
              <Text className='cell-extra'>{detail.remark}</Text>
            </View>
          )}
          {detail.file_hash && (
            <View className='cell-row'>
              <Text className='cell-title'>文档哈希</Text>
              <Text className='cell-extra hash-text'>{detail.file_hash.slice(0, 16) + '...'}</Text>
            </View>
          )}
          {detail.template_id && (
            <View className='cell-row clickable' onClick={handlePreview}>
              <Text className='cell-title'>合同内容</Text>
              <Text className='cell-link'>预览合同 &gt;</Text>
            </View>
          )}
        </View>

        {/* 签署方 */}
        {detail.participants?.length > 0 && (
          <View className='info-group'>
            <Text className='group-title'>签署各方</Text>
            {detail.participants.map((p: any, index: number) => (
              <View key={p.id || index} className='participant-card'>
                <View className='p-main'>
                  <Text className='p-name'>{p.name || '未指定'}</Text>
                  <Text className='p-mobile'>{p.mobile}</Text>
                </View>
                <Text className={`status-tag status-tag-${p.status === 2 ? 'success' : p.status === 1 ? 'danger' : 'warning'}`}>
                  {p.status === 0 ? '待签署' : p.status === 2 ? '已签署' : '已拒签'}
                </Text>
              </View>
            ))}
          </View>
        )}

        {/* 证据链 */}
        <View className='info-group'>
          <View className='group-header' onClick={fetchEvidence}>
            <Text className='group-title'>签署证据链</Text>
            <Text className='toggle-arrow'>{showEvidence ? '▲' : '▼'}</Text>
          </View>
          {showEvidence && (
            <View className='evidence-timeline'>
              {evidenceList.length === 0 ? (
                <Text className='no-data'>暂无存证记录</Text>
              ) : (
                evidenceList.map((log: any) => (
                  <View key={log.id} className='timeline-item'>
                    <View className='timeline-dot' />
                    <View className='timeline-content'>
                      <Text className='action'>{ACTION_LABEL[log.action] || log.action}</Text>
                      <Text className='time'>{log.create_time}</Text>
                      {log.ip && <Text className='ip'>IP: {log.ip}</Text>}
                    </View>
                  </View>
                ))
              )}
            </View>
          )}
        </View>
      </View>

      {/* 合同内容预览弹层 */}
      {showPreview && (
        <View className='preview-overlay'>
          <View className='preview-panel'>
            <View className='preview-header'>
              <Text className='preview-title'>合同内容预览</Text>
              <Text className='preview-close' onClick={() => setShowPreview(false)}>关闭</Text>
            </View>
            <ScrollView scrollY className='preview-scroll'>
              <View className='preview-body'>
                <RichText nodes={contractHtml} />

                {/* 签署方信息 */}
                {detail.participants?.length > 0 && (
                  <View className='preview-signers'>
                    <Text className='preview-signers-title'>签署信息</Text>
                    {detail.participants.map((p: any, index: number) => (
                      <View key={p.id || index} className='preview-signer-item'>
                        <View className='preview-signer-info'>
                          <Text className='preview-signer-name'>{p.name || '未指定'}</Text>
                          <Text className={`preview-signer-status ${p.status === 2 ? 'signed' : ''}`}>
                            {p.status === 0 ? '待签署' : p.status === 2 ? '已签署' : '已拒签'}
                          </Text>
                        </View>
                        {p.sign_time && (
                          <Text className='preview-signer-time'>签署时间：{p.sign_time}</Text>
                        )}
                        {p.seal_data && (
                          <Image className='preview-seal-img' src={resolveStaticUrl(p.seal_data)} mode='aspectFit' />
                        )}
                      </View>
                    ))}
                  </View>
                )}
              </View>
            </ScrollView>
          </View>
        </View>
      )}

      {/* 悬浮操作栏 */}
      <View className='action-bar-placeholder' />
      <View className='action-bar'>
        <View className='btn-group'>
          {detail.status === 1 && role !== 'tenant' && (
            <View className='btn btn-primary btn-block' onClick={handleInitiate}>
              <Text>发起签署</Text>
            </View>
          )}
          {detail.status === 2 && (
            <View className='btn btn-primary btn-block' onClick={handleSign}>
              <Text>立即签署</Text>
            </View>
          )}
          {detail.status === 3 && (
            <View className='btn btn-success btn-block' onClick={handleDownload}>
              <Text>{detail.template_id ? '查看签署件' : '下载签署件'}</Text>
            </View>
          )}

          <View className='secondary-btns'>
            {detail.status === 2 && role !== 'tenant' && (
              <View className='btn btn-default btn-small sec-btn' onClick={handleUrge}>
                <Text>催签</Text>
              </View>
            )}
            {detail.status <= 2 && role !== 'tenant' && (
              <View className='btn btn-small sec-btn cancel-btn' onClick={handleCancel}>
                <Text>取消</Text>
              </View>
            )}
            {(detail.status === 1 || detail.status === 4) && role !== 'tenant' && (
              <View className='btn btn-small sec-btn delete-btn' onClick={handleDelete}>
                <Text>删除</Text>
              </View>
            )}
          </View>
        </View>
      </View>
    </View>
  )
}
