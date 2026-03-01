import { useState, useEffect } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import { View, Text, RichText } from '@tarojs/components'
import { getTemplateDetail } from '@/api/templates'
import './index.scss'

export default function TemplateDetailPage() {
  const router = useRouter()
  const templateId = Number(router.params.id)
  const [detail, setDetail] = useState<any>(null)

  useEffect(() => {
    if (templateId) fetchDetail()
  }, [templateId])

  const fetchDetail = async () => {
    try {
      const data = await getTemplateDetail(templateId)
      setDetail(data)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '加载失败', icon: 'none' })
    }
  }

  const handleUseTemplate = () => {
    Taro.navigateTo({ url: `/pages/contract-create/index?templateId=${templateId}` })
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

      <View className='bottom-bar'>
        <View className='btn btn-primary btn-block' onClick={handleUseTemplate}>
          <Text>使用此模板</Text>
        </View>
      </View>
    </View>
  )
}
