import { useState, useEffect, useRef } from 'react'
import Taro, { useRouter, useDidShow } from '@tarojs/taro'
import { View, Text, RichText, Image, ScrollView, Input, Picker } from '@tarojs/components'
import {
  getContractDetail,
  executeSign,
  rejectSign,
} from '@/api/contracts'
import { getTemplateDetail } from '@/api/templates'
import { getSealList } from '@/api/seals'
import { getUserInfo } from '@/api/member'
import { useRequireAuth } from '@/hooks/useAuth'
import { resolveStaticUrl } from '@/api/config'
import './index.scss'

interface SealItem {
  id: number
  name: string
  type: number
  seal_data: string
  is_default: number
}

export default function ContractSignPage() {
  useRequireAuth()
  const router = useRouter()
  const contractId = Number(router.params.id)

  const [detail, setDetail] = useState<any>(null)
  const [contractHtml, setContractHtml] = useState<string>('')
  const [seals, setSeals] = useState<SealItem[]>([])
  const [selectedSealId, setSelectedSealId] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [signed, setSigned] = useState(false)
  const [realNameVerified, setRealNameVerified] = useState<boolean | null>(null)
  // 当前签署方的 party 标识（'A' | 'B'）
  const [myParty, setMyParty] = useState<string>('')
  // 当前签署方待填变量
  const [myVars, setMyVars] = useState<{ name: string; label: string; type: string }[]>([])
  const [myVarValues, setMyVarValues] = useState<Record<string, string>>({})

  const loadSeals = async () => {
    try {
      const sealData = await getSealList({ pageNo: 1, pageSize: 50 })
      const sealList = sealData?.list || []
      setSeals(sealList)
      // 自动选中默认签名（仅未手动选择时）— 用函数式更新避免闭包陷阱
      setSelectedSealId(prev => {
        if (prev) return prev
        const defaultSeal = sealList.find((s: SealItem) => s.is_default === 1)
        return defaultSeal ? defaultSeal.id : null
      })
    } catch {
      // 签名获取失败不阻塞
    }
  }

  // 用 ref 保证 useDidShow 总是调用最新的 loadSeals
  const loadSealsRef = useRef(loadSeals)
  loadSealsRef.current = loadSeals

  useEffect(() => {
    if (contractId) loadData()
  }, [contractId])

  // 页面每次显示时刷新签名列表（从创建签名页返回时触发）
  useDidShow(() => {
    loadSealsRef.current()
  })

  const loadData = async () => {
    try {
      // 检查实名认证状态 + 获取当前用户手机号
      let userMobile = ''
      try {
        const userInfo = await getUserInfo()
        setRealNameVerified(userInfo.real_name_verified === 1)
        userMobile = userInfo.mobile || ''
      } catch {
        setRealNameVerified(false)
      }

      // 获取合同详情
      const contractData = await getContractDetail(contractId)
      setDetail(contractData)

      // 判断当前用户是甲方还是乙方（通过手机号匹配 participant）
      const participants = contractData.participants || []
      let currentParty = ''
      for (const p of participants) {
        if (p.mobile === userMobile) {
          currentParty = p.order_num === 1 ? 'A' : 'B'
          break
        }
      }
      setMyParty(currentParty)

      // 如果有模板，获取模板内容并替换变量
      if (contractData.template_id) {
        try {
          const tpl = await getTemplateDetail(contractData.template_id)
          if (tpl?.content) {
            let html = tpl.content as string
            const vars = contractData.variables || {}
            // 替换签章占位符
            const buildSig = (orderNum: number) => {
              const p = participants.find((item: any) => item.order_num === orderNum)
              if (!p) return '<p style="color:#ccc">（未指定签署方）</p>'
              if (p.status === 2 && p.seal_data) {
                return `<div><img src="${resolveStaticUrl(p.seal_data)}" style="max-width:150px;max-height:80px;" /></div>`
              }
              if (p.status === 2) return `<p>${p.name || ''}（已签署）</p>`
              return '<p style="color:#ccc">（待签署）</p>'
            }
            // 统一替换所有占位符（签章 + 普通变量）
            html = html.replace(/\{\{(\w+)\}\}/g, (_match: string, varName: string) => {
              if (varName === 'partyASignature') return buildSig(1)
              if (varName === 'partyBSignature') return buildSig(2)
              return vars[varName] || `<span style="color:#ccc">未填写</span>`
            })
            setContractHtml(html)

            // 提取当前签署方待填变量（属于自己这一方且尚未填写的变量）
            const tplVars = (tpl.variables || []) as { name: string; label: string; type: string; party?: string }[]
            const pendingVars = tplVars.filter(v => {
              const varParty = v.party || (v.name.startsWith('partyA') ? 'A' : v.name.startsWith('partyB') ? 'B' : 'common')
              return varParty === currentParty && !vars[v.name]
            })
            setMyVars(pendingVars)
            // 初始化值
            const initVals: Record<string, string> = {}
            pendingVars.forEach(v => { initVals[v.name] = '' })
            setMyVarValues(initVals)
          }
        } catch {
          // 模板获取失败不阻塞签署
        }
      }

      // 初次加载签名列表
      await loadSeals()
    } catch (e: any) {
      Taro.showToast({ title: e.message || '加载失败', icon: 'none' })
    }
  }

  const handleSign = async () => {
    if (!selectedSealId) {
      Taro.showToast({ title: '请先选择签名', icon: 'none' })
      return
    }

    // 校验当前签署方必填变量
    for (const v of myVars) {
      const val = myVarValues[v.name]?.trim()
      if (!val) {
        Taro.showToast({ title: `请填写${v.label}`, icon: 'none' })
        return
      }
      if (/Phone$/.test(v.name) && !/^1\d{10}$/.test(val)) {
        Taro.showToast({ title: '手机号格式不正确', icon: 'none' })
        return
      }
      if (/IdCard$/.test(v.name) && !/^\d{17}[\dXx]$/.test(val)) {
        Taro.showToast({ title: '身份证号格式不正确', icon: 'none' })
        return
      }
    }

    const res = await Taro.showModal({
      title: '确认签署',
      content: '您确定要签署此合同吗？签署后具有法律效力。',
    })
    if (!res.confirm) return

    setLoading(true)
    try {
      // 构建当前签署方变量
      const vars = myVars.length > 0 ? { ...myVarValues } : undefined
      await executeSign(contractId, selectedSealId, vars)
      setSigned(true)
      Taro.showToast({ title: '签署成功', icon: 'success' })
      setTimeout(() => Taro.navigateBack(), 2000)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '签署失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  const handleReject = async () => {
    const res = await Taro.showModal({ title: '提示', content: '确定拒签此合同？' })
    if (!res.confirm) return
    try {
      await rejectSign(contractId)
      Taro.showToast({ title: '已拒签', icon: 'success' })
      setTimeout(() => Taro.navigateBack(), 1500)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '操作失败', icon: 'none' })
    }
  }

  const handleCreateSeal = () => {
    Taro.navigateTo({ url: '/pages/profile/seal-create/index' })
  }

  // 签署成功页
  if (signed) {
    return (
      <View className='contract-sign result-page'>
        <View className='result-icon'>
          <Text>OK</Text>
        </View>
        <Text className='result-title'>签署成功</Text>
        <Text className='result-hint'>合同已签署完成，即将返回</Text>
      </View>
    )
  }

  if (!detail) {
    return <View className='contract-sign'><Text className='loading-text'>加载中...</Text></View>
  }

  return (
    <View className='contract-sign'>
      {/* 实名认证提示 */}
      {realNameVerified === false && (
        <View className='realname-warning'>
          <View className='warning-content'>
            <Text className='warning-icon'>&#9888;</Text>
            <View className='warning-text-wrap'>
              <Text className='warning-title'>请先完成实名认证</Text>
              <Text className='warning-desc'>签署合同前需要完成实名认证以保障法律效力</Text>
            </View>
          </View>
          <View
            className='btn btn-primary btn-small warning-btn'
            onClick={() => Taro.navigateTo({ url: '/pages/profile/realname/index' })}
          >
            <Text>去认证</Text>
          </View>
        </View>
      )}

      {/* 合同标题 */}
      <View className='sign-header'>
        <Text className='sign-title'>{detail.name}</Text>
        <Text className='sign-hint'>请仔细阅读合同内容后签署</Text>
      </View>

      {/* 合同内容 */}
      {contractHtml ? (
        <View className='contract-content-section'>
          <Text className='section-title'>合同内容</Text>
          <ScrollView scrollY className='contract-scroll'>
            <View className='contract-html'>
              <RichText nodes={contractHtml} />
            </View>
          </ScrollView>
        </View>
      ) : null}

      {/* 签署方状态 */}
      <View className='sign-info'>
        <Text className='section-title'>签署方</Text>
        {detail.participants?.map((p: any, index: number) => (
          <View key={p.id || index} className='signer-item'>
            <View className='signer-left'>
              <Text className='signer-name'>{p.name || p.mobile}</Text>
              <Text className='signer-mobile'>{p.mobile}</Text>
            </View>
            <Text className={`signer-status status-${p.status}`}>
              {p.status === 0 ? '待签署' : p.status === 2 ? '已签署' : '已拒签'}
            </Text>
          </View>
        ))}
      </View>

      {/* 以下内容仅在实名认证后显示 */}
      {realNameVerified !== false && (
        <>
          {/* 当前签署方信息填写 */}
          {myVars.length > 0 && (
            <View className='partyb-section'>
              <Text className='section-title'>{myParty === 'A' ? '甲方' : '乙方'}信息</Text>
              {myVars.map(v => (
                v.type === 'date' ? (
                  <View key={v.name} className='form-item'>
                    <Text className='form-label'>{v.label}</Text>
                    <Picker
                      mode='date'
                      value={myVarValues[v.name] || ''}
                      onChange={(e) => setMyVarValues(prev => ({ ...prev, [v.name]: e.detail.value }))}
                    >
                      <View className='form-input picker-input'>
                        <Text className={myVarValues[v.name] ? '' : 'placeholder-text'}>
                          {myVarValues[v.name] || `请选择${v.label}`}
                        </Text>
                      </View>
                    </Picker>
                  </View>
                ) : (
                  <View key={v.name} className='form-item'>
                    <Text className='form-label'>{v.label}</Text>
                    <Input
                      className='form-input'
                      placeholder={`请输入${v.label}`}
                      value={myVarValues[v.name] || ''}
                      onInput={(e) => setMyVarValues(prev => ({ ...prev, [v.name]: e.detail.value }))}
                    />
                  </View>
                )
              ))}
            </View>
          )}

          {/* 签名选择 */}
          <View className='seal-section'>
            <View className='section-header'>
              <Text className='section-title'>选择签名</Text>
              <View className='btn-create-seal' onClick={handleCreateSeal}>
                <Text>+ 创建签名</Text>
              </View>
            </View>

            {seals.length === 0 ? (
              <View className='no-seal-tip'>
                <Text className='no-seal-text'>您还没有签名，请先创建签名</Text>
                <View className='btn btn-primary btn-small' onClick={handleCreateSeal}>
                  <Text>去创建</Text>
                </View>
              </View>
            ) : (
              <View className='seal-list'>
                {seals.map((seal) => (
                  <View
                    key={seal.id}
                    className={`seal-option ${selectedSealId === seal.id ? 'selected' : ''}`}
                    onClick={() => setSelectedSealId(seal.id)}
                  >
                    <Image className='seal-preview-img' src={resolveStaticUrl(seal.seal_data)} mode='aspectFit' />
                    <Text className='seal-option-name'>
                      {seal.name}
                      {seal.is_default === 1 ? '(默认)' : ''}
                    </Text>
                    <View className={`radio-circle ${selectedSealId === seal.id ? 'checked' : ''}`}>
                      {selectedSealId === seal.id && <View className='radio-inner-dot' />}
                    </View>
                  </View>
                ))}
              </View>
            )}
          </View>

          {/* 操作按钮 */}
          <View className='sign-action-bar'>
            <View className='btn btn-default btn-action reject-btn' onClick={handleReject}>
              <Text>拒签</Text>
            </View>
            <View
              className={`btn btn-primary btn-action ${loading || !selectedSealId ? 'btn-disabled' : ''}`}
              onClick={loading || !selectedSealId ? undefined : handleSign}
            >
              <Text>{loading ? '签署中...' : '确认签署'}</Text>
            </View>
          </View>
        </>
      )}
    </View>
  )
}
