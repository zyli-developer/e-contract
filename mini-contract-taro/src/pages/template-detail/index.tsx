import { useState, useEffect } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import { View, Text, RichText } from '@tarojs/components'
import { Button, Input } from '@nutui/nutui-react-taro'
import { getTemplateDetail } from '@/api/templates'
import { createContract } from '@/api/contracts'
import './index.scss'

interface TemplateVariable {
  key: string
  label: string
  type: string
  required?: boolean
}

export default function TemplateDetailPage() {
  const router = useRouter()
  const templateId = Number(router.params.id)
  const [detail, setDetail] = useState<any>(null)
  const [variables, setVariables] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (templateId) fetchDetail()
  }, [templateId])

  const fetchDetail = async () => {
    try {
      const data = await getTemplateDetail(templateId)
      setDetail(data)
      const vars: Record<string, string> = {}
      ;(data?.variables || []).forEach((v: TemplateVariable) => {
        vars[v.key] = ''
      })
      setVariables(vars)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '加载失败', icon: 'none' })
    }
  }

  const handleUseTemplate = async () => {
    const requiredVars = (detail?.variables || []).filter((v: TemplateVariable) => v.required)
    for (const v of requiredVars) {
      if (!variables[v.key]) {
        Taro.showToast({ title: `请填写${v.label}`, icon: 'none' })
        return
      }
    }

    setLoading(true)
    try {
      await createContract({
        name: detail?.name || '新合同',
        template_id: templateId,
        participants: [],
      })
      Taro.showToast({ title: '合同创建成功', icon: 'success' })
      setTimeout(() => Taro.switchTab({ url: '/pages/contract-manage/index' }), 1500)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '创建失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  if (!detail) {
    return <View className='template-detail'><Text>加载中...</Text></View>
  }

  return (
    <View className='template-detail'>
      <View className='detail-header'>
        <Text className='detail-name'>{detail.name}</Text>
        {detail.description && <Text className='detail-desc'>{detail.description}</Text>}
      </View>

      {detail.content && (
        <View className='content-preview'>
          <Text className='section-title'>模板预览</Text>
          <RichText nodes={detail.content} />
        </View>
      )}

      {detail.variables && detail.variables.length > 0 && (
        <View className='variables-form'>
          <Text className='section-title'>填写信息</Text>
          {detail.variables.map((v: TemplateVariable) => (
            <View key={v.key} className='form-item'>
              <Text className='form-label'>
                {v.label}
                {v.required && <Text className='required'>*</Text>}
              </Text>
              <Input
                placeholder={`请输入${v.label}`}
                value={variables[v.key] || ''}
                onChange={(val) => setVariables((prev) => ({ ...prev, [v.key]: val }))}
              />
            </View>
          ))}
        </View>
      )}

      <View className='bottom-bar'>
        <Button type='primary' block loading={loading} onClick={handleUseTemplate}>
          使用此模板创建合同
        </Button>
      </View>
    </View>
  )
}
