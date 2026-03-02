import { useState, useEffect } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import { View, Text, Input, Picker } from '@tarojs/components'
import { useRequireAuth, useRequireLandlord } from '@/hooks/useAuth'
import { createContract } from '@/api/contracts'
import { getTemplateDetail } from '@/api/templates'
import { getUserInfo } from '@/api/member'
import './index.scss'

interface TemplateVariable {
  name: string
  label: string
  type: string
  party: 'A' | 'B' | 'common'
}

interface Participant {
  name: string
  mobile: string
  order_num: number
}

export default function ContractCreatePage() {
  useRequireAuth()
  useRequireLandlord()
  const router = useRouter()
  const templateId = router.params.templateId ? Number(router.params.templateId) : null

  // 共用状态
  const [name, setName] = useState('')
  const [remark, setRemark] = useState('')
  const [loading, setLoading] = useState(false)

  // 非模板模式
  const [participants, setParticipants] = useState<Participant[]>([])

  // 模板模式
  const [templateDetail, setTemplateDetail] = useState<any>(null)
  const [varValues, setVarValues] = useState<Record<string, string>>({})
  const [partyBName, setPartyBName] = useState('')
  const [partyBMobile, setPartyBMobile] = useState('')
  const [userMobile, setUserMobile] = useState('')

  useEffect(() => {
    if (templateId) {
      loadTemplateData()
    }
  }, [templateId])

  const loadTemplateData = async () => {
    try {
      const [tpl, user] = await Promise.all([
        getTemplateDetail(templateId!),
        getUserInfo(),
      ])
      setTemplateDetail(tpl)
      setName(tpl.name || '')
      setUserMobile(user.mobile || '')

      // 初始化变量值，甲方电话自动填充
      const initVars: Record<string, string> = {}
      ;(tpl.variables || []).forEach((v: TemplateVariable) => {
        const party = v.party || (v.name.startsWith('partyA') ? 'A' : v.name.startsWith('partyB') ? 'B' : 'common')
        if (v.name === 'partyAPhone') {
          initVars[v.name] = user.mobile || ''
        } else if (party !== 'B') {
          initVars[v.name] = ''
        }
      })
      setVarValues(initVars)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '加载模板失败', icon: 'none' })
    }
  }

  // --- 模板模式: 变量分组 ---
  const inferParty = (v: TemplateVariable): 'A' | 'B' | 'common' => {
    if (v.party) return v.party
    if (v.name.startsWith('partyA')) return 'A'
    if (v.name.startsWith('partyB')) return 'B'
    return 'common'
  }

  const getGroupedVars = () => {
    if (!templateDetail?.variables) return { partyA: [], common: [] }
    const vars = templateDetail.variables as TemplateVariable[]
    return {
      partyA: vars.filter(v => inferParty(v) === 'A'),
      common: vars.filter(v => inferParty(v) === 'common'),
    }
  }

  const updateVarValue = (varName: string, value: string) => {
    setVarValues(prev => ({ ...prev, [varName]: value }))
  }

  // --- 非模板模式 ---
  const addParticipant = () => {
    setParticipants([
      ...participants,
      { name: '', mobile: '', order_num: participants.length + 1 },
    ])
  }

  const removeParticipant = (index: number) => {
    setParticipants(participants.filter((_, i) => i !== index))
  }

  const updateParticipant = (index: number, field: string, value: string) => {
    const updated = [...participants]
    updated[index] = { ...updated[index], [field]: value }
    setParticipants(updated)
  }

  const handleFromTemplate = () => {
    Taro.navigateTo({ url: '/pages/template-market/index' })
  }

  // --- 提交 ---
  const handleSubmit = async () => {
    if (!name.trim()) {
      Taro.showToast({ title: '请输入合同名称', icon: 'none' })
      return
    }

    if (templateId) {
      return handleTemplateSubmit()
    }

    // 非模板模式提交
    for (const p of participants) {
      if (!p.name.trim() || !p.mobile.trim()) {
        Taro.showToast({ title: '请完善签署方信息', icon: 'none' })
        return
      }
      if (!/^1\d{10}$/.test(p.mobile)) {
        Taro.showToast({ title: `手机号格式不正确: ${p.mobile}`, icon: 'none' })
        return
      }
    }

    setLoading(true)
    try {
      await createContract({
        name: name.trim(),
        remark: remark.trim() || undefined,
        participants,
      })
      Taro.showToast({ title: '合同创建成功', icon: 'success' })
      setTimeout(() => Taro.switchTab({ url: '/pages/contract-manage/index' }), 1500)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '创建失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  const handleTemplateSubmit = async () => {
    // 验证乙方信息
    if (!partyBName.trim()) {
      Taro.showToast({ title: '请输入乙方姓名', icon: 'none' })
      return
    }
    if (!partyBMobile.trim() || !/^1\d{10}$/.test(partyBMobile)) {
      Taro.showToast({ title: '请输入正确的乙方手机号', icon: 'none' })
      return
    }

    // 校验甲方变量格式（手机号、身份证）
    for (const [key, val] of Object.entries(varValues)) {
      if (/Phone$/.test(key) && val && !/^1\d{10}$/.test(val)) {
        Taro.showToast({ title: '手机号格式不正确', icon: 'none' })
        return
      }
      if (/IdCard$/.test(key) && val && !/^\d{17}[\dXx]$/.test(val)) {
        Taro.showToast({ title: '身份证号格式不正确', icon: 'none' })
        return
      }
    }

    // 构建 variables（甲方 + 公共 + 乙方姓名/手机号）
    const variables: Record<string, string> = { ...varValues }
    variables['partyBName'] = partyBName.trim()
    variables['partyBPhone'] = partyBMobile.trim()

    // 构建签署方列表
    const templateParticipants: Participant[] = [
      { name: varValues.partyAName || '', mobile: userMobile, order_num: 1 },
      { name: partyBName.trim(), mobile: partyBMobile.trim(), order_num: 2 },
    ]

    setLoading(true)
    try {
      await createContract({
        name: name.trim(),
        template_id: templateId,
        remark: remark.trim() || undefined,
        variables,
        participants: templateParticipants,
      })
      Taro.showToast({ title: '合同创建成功', icon: 'success' })
      setTimeout(() => Taro.switchTab({ url: '/pages/contract-manage/index' }), 1500)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '创建失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  // --- 渲染变量输入 ---
  const renderVarInput = (v: TemplateVariable) => {
    const isAutoFill = v.name === 'partyAPhone'

    if (v.type === 'date') {
      return (
        <View key={v.name} className='form-item'>
          <Text className='form-label'>{v.label}</Text>
          <Picker
            mode='date'
            value={varValues[v.name] || ''}
            onChange={(e) => updateVarValue(v.name, e.detail.value)}
          >
            <View className='custom-input picker-input'>
              <Text className={varValues[v.name] ? '' : 'placeholder-text'}>
                {varValues[v.name] || `请选择${v.label}`}
              </Text>
            </View>
          </Picker>
        </View>
      )
    }

    return (
      <View key={v.name} className='form-item'>
        <View className='form-label-row'>
          <Text className='form-label'>{v.label}</Text>
          {isAutoFill && <Text className='auto-fill-tag'>自动填充</Text>}
        </View>
        <Input
          className='custom-input'
          placeholder={`请输入${v.label}`}
          value={varValues[v.name] || ''}
          disabled={isAutoFill}
          onInput={(e) => updateVarValue(v.name, e.detail.value)}
        />
      </View>
    )
  }

  // ==================== 模板模式渲染 ====================
  if (templateId) {
    if (!templateDetail) {
      return <View className='contract-create'><Text>加载中...</Text></View>
    }

    const { partyA, common } = getGroupedVars()

    return (
      <View className='contract-create'>
        {/* 合同信息 */}
        <View className='section'>
          <Text className='section-title'>合同信息</Text>
          <View className='form-item'>
            <Text className='form-label'>合同名称 <Text className='required'>*</Text></Text>
            <Input
              className='custom-input'
              placeholder='请输入合同名称'
              value={name}
              onInput={(e) => setName(e.detail.value)}
            />
          </View>
          <View className='form-item'>
            <Text className='form-label'>备注</Text>
            <Input
              className='custom-input'
              placeholder='请输入备注（选填）'
              value={remark}
              onInput={(e) => setRemark(e.detail.value)}
            />
          </View>
        </View>

        {/* 甲方信息 */}
        {partyA.length > 0 && (
          <View className='section'>
            <Text className='section-title'>甲方信息（出租方）</Text>
            {partyA.map(renderVarInput)}
          </View>
        )}

        {/* 合同条款信息 */}
        {common.length > 0 && (
          <View className='section'>
            <Text className='section-title'>合同条款信息</Text>
            {common.map(renderVarInput)}
          </View>
        )}

        {/* 签署方 */}
        <View className='section'>
          <Text className='section-title'>签署方</Text>

          {/* 甲方 - 当前用户 */}
          <View className='signer-card'>
            <View className='signer-header'>
              <Text className='signer-role'>甲方（出租方）</Text>
              <Text className='auto-fill-tag'>当前用户</Text>
            </View>
            <View className='signer-info'>
              <Text className='signer-phone'>{userMobile || '未获取到手机号'}</Text>
            </View>
          </View>

          {/* 乙方 - 手动填写 */}
          <View className='signer-card'>
            <View className='signer-header'>
              <Text className='signer-role'>乙方（承租方）</Text>
            </View>
            <View className='p-form'>
              <Input
                className='p-input'
                placeholder='乙方姓名'
                value={partyBName}
                onInput={(e) => setPartyBName(e.detail.value)}
              />
              <Input
                className='p-input'
                placeholder='乙方手机号'
                type='number'
                maxlength={11}
                value={partyBMobile}
                onInput={(e) => setPartyBMobile(e.detail.value)}
              />
            </View>
          </View>
        </View>

        {/* 提交 */}
        <View className='bottom-bar'>
          <View
            className={`btn btn-primary btn-block ${loading ? 'btn-loading' : ''}`}
            onClick={loading ? undefined : handleSubmit}
          >
            <Text>{loading ? '创建中...' : '立即创建合同'}</Text>
          </View>
        </View>
      </View>
    )
  }

  // ==================== 非模板模式渲染 ====================
  return (
    <View className='contract-create'>
      {/* 创建方式选择 */}
      <View className='section'>
        <Text className='section-title'>创建方式</Text>
        <View className='create-options'>
          <View className='option-card' onClick={handleFromTemplate}>
            <View className='option-icon template'>
              <Text>T</Text>
            </View>
            <Text className='option-label'>从模板创建</Text>
          </View>
          <View className='option-card active'>
            <View className='option-icon file'>
              <Text>F</Text>
            </View>
            <Text className='option-label'>上传文件创建</Text>
          </View>
        </View>
      </View>

      {/* 合同信息 */}
      <View className='section'>
        <Text className='section-title'>合同信息</Text>
        <View className='form-item'>
          <Text className='form-label'>合同名称 <Text className='required'>*</Text></Text>
          <Input
            className='custom-input'
            placeholder='请输入合同名称'
            value={name}
            onInput={(e) => setName(e.detail.value)}
          />
        </View>
        <View className='form-item'>
          <Text className='form-label'>备注</Text>
          <Input
            className='custom-input'
            placeholder='请输入备注（选填）'
            value={remark}
            onInput={(e) => setRemark(e.detail.value)}
          />
        </View>
      </View>

      {/* 签署方 */}
      <View className='section'>
        <View className='section-header'>
          <Text className='section-title'>签署方</Text>
          <View className='btn btn-primary btn-small' onClick={addParticipant}>
            <Text>添加签署方</Text>
          </View>
        </View>

        {participants.map((p, index) => (
          <View key={index} className='participant-card'>
            <View className='participant-header'>
              <Text className='participant-num'>签署方 {index + 1}</Text>
              <Text className='remove-icon' onClick={() => removeParticipant(index)}>x</Text>
            </View>
            <View className='p-form'>
              <Input
                className='p-input'
                placeholder='姓名'
                value={p.name}
                onInput={(e) => updateParticipant(index, 'name', e.detail.value)}
              />
              <Input
                className='p-input'
                placeholder='手机号'
                type='number'
                maxlength={11}
                value={p.mobile}
                onInput={(e) => updateParticipant(index, 'mobile', e.detail.value)}
              />
            </View>
          </View>
        ))}

        {participants.length === 0 && (
          <View className='empty-state'>
            <Text className='empty-hint'>暂未添加签署方</Text>
          </View>
        )}
      </View>

      {/* 提交 */}
      <View className='bottom-bar'>
        <View
          className={`btn btn-primary btn-block ${loading ? 'btn-loading' : ''}`}
          onClick={loading ? undefined : handleSubmit}
        >
          <Text>{loading ? '创建中...' : '立即创建合同'}</Text>
        </View>
      </View>
    </View>
  )
}
