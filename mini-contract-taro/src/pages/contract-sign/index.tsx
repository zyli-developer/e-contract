import { useState, useEffect } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import { View, Text, WebView } from '@tarojs/components'
import { Button } from '@nutui/nutui-react-taro'
import { SIGN_H5_URL } from '@/api/config'
import { getContractDetail } from '@/api/contracts'
import { useAuthStore } from '@/store/useAuthStore'
import './index.scss'

export default function ContractSignPage() {
  const router = useRouter()
  const contractId = Number(router.params.id)
  const { token } = useAuthStore()
  const [detail, setDetail] = useState<any>(null)
  const [showWebView, setShowWebView] = useState(false)

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

  const handleStartSign = () => {
    // 跳转到 H5 签署页面
    setShowWebView(true)
  }

  const handleWebViewMessage = (e: any) => {
    // H5 签署完成后回调
    const data = e.detail?.data?.[0]
    if (data?.type === 'sign_complete') {
      Taro.showToast({ title: '签署完成', icon: 'success' })
      setTimeout(() => Taro.navigateBack(), 1500)
    }
  }

  if (showWebView) {
    const signUrl = `${SIGN_H5_URL}/sign?taskId=${contractId}&token=${token}`
    return <WebView src={signUrl} onMessage={handleWebViewMessage} />
  }

  if (!detail) {
    return <View className='contract-sign'><Text>加载中...</Text></View>
  }

  return (
    <View className='contract-sign'>
      <View className='sign-header'>
        <Text className='sign-title'>{detail.name}</Text>
        <Text className='sign-hint'>请确认合同内容后签署</Text>
      </View>

      {/* 签署方信息 */}
      <View className='sign-info'>
        <Text className='section-title'>签署方</Text>
        {detail.participants?.map((p: any, index: number) => (
          <View key={p.id || index} className='signer-item'>
            <Text className='signer-name'>{p.name || p.mobile}</Text>
            <Text className='signer-status'>
              {p.status === 0 ? '待签署' : p.status === 2 ? '已签署' : '已拒签'}
            </Text>
          </View>
        ))}
      </View>

      <View className='sign-action'>
        <Button type='primary' block onClick={handleStartSign}>
          开始签署
        </Button>
      </View>
    </View>
  )
}
