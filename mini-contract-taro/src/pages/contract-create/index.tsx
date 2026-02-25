import { useState } from 'react'
import Taro from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
import { Button, Input } from '@nutui/nutui-react-taro'
import { useRequireAuth } from '@/hooks/useAuth'
import { createContract } from '@/api/contracts'
import './index.scss'

interface Participant {
  name: string
  mobile: string
  order_num: number
}

export default function ContractCreatePage() {
  useRequireAuth()
  const [name, setName] = useState('')
  const [remark, setRemark] = useState('')
  const [participants, setParticipants] = useState<Participant[]>([])
  const [loading, setLoading] = useState(false)

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

  const handleSubmit = async () => {
    if (!name.trim()) {
      Taro.showToast({ title: '请输入合同名称', icon: 'none' })
      return
    }

    // 校验签署方
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

  return (
    <View className='contract-create'>
      {/* 创建方式选择 */}
      <View className='section'>
        <Text className='section-title'>创建方式</Text>
        <View className='create-options'>
          <View className='option-card' onClick={handleFromTemplate}>
            <Text className='option-icon'>T</Text>
            <Text className='option-label'>从模板创建</Text>
          </View>
          <View className='option-card active'>
            <Text className='option-icon'>F</Text>
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
            placeholder='请输入合同名称'
            value={name}
            onChange={(val) => setName(val)}
          />
        </View>
        <View className='form-item'>
          <Text className='form-label'>备注</Text>
          <Input
            placeholder='请输入备注（选填）'
            value={remark}
            onChange={(val) => setRemark(val)}
          />
        </View>
      </View>

      {/* 签署方 */}
      <View className='section'>
        <View className='section-header'>
          <Text className='section-title'>签署方</Text>
          <Button size='small' onClick={addParticipant}>添加签署方</Button>
        </View>

        {participants.map((p, index) => (
          <View key={index} className='participant-card'>
            <View className='participant-header'>
              <Text className='participant-num'>签署方 {index + 1}</Text>
              <Text className='remove-btn' onClick={() => removeParticipant(index)}>删除</Text>
            </View>
            <Input
              placeholder='姓名'
              value={p.name}
              onChange={(val) => updateParticipant(index, 'name', val)}
            />
            <Input
              placeholder='手机号'
              type='number'
              maxLength={11}
              value={p.mobile}
              onChange={(val) => updateParticipant(index, 'mobile', val)}
            />
          </View>
        ))}

        {participants.length === 0 && (
          <Text className='empty-hint'>暂未添加签署方</Text>
        )}
      </View>

      {/* 提交 */}
      <View className='bottom-bar'>
        <Button type='primary' block loading={loading} onClick={handleSubmit}>
          创建合同
        </Button>
      </View>
    </View>
  )
}
