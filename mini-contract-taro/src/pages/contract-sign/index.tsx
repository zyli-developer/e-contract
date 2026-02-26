import { useState, useEffect, useRef } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import { View, Text, Input, WebView } from '@tarojs/components'
import { SIGN_H5_URL } from '@/api/config'
import {
  getContractDetail,
  sendSignCode,
  verifySignCode,
  executeSign,
  rejectSign,
} from '@/api/contracts'
import { useRequireAuth } from '@/hooks/useAuth'
import { useAuthStore } from '@/store/useAuthStore'
import './index.scss'

type Step = 'info' | 'verify' | 'signing' | 'result'

export default function ContractSignPage() {
  useRequireAuth()
  const router = useRouter()
  const contractId = Number(router.params.id)
  const { token } = useAuthStore()
  const [detail, setDetail] = useState<any>(null)
  const [step, setStep] = useState<Step>('info')

  const [code, setCode] = useState('')
  const [countdown, setCountdown] = useState(0)
  const [verifying, setVerifying] = useState(false)
  const timerRef = useRef<any>(null)

  useEffect(() => {
    if (contractId) fetchDetail()
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
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

  const handleStartSign = () => {
    setStep('verify')
    handleSendCode()
  }

  const handleSendCode = async () => {
    try {
      await sendSignCode(contractId)
      Taro.showToast({ title: '验证码已发送', icon: 'success' })
      setCountdown(60)
      timerRef.current = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timerRef.current)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '发送失败', icon: 'none' })
    }
  }

  const handleVerifyAndSign = async () => {
    if (!code || code.length !== 6) {
      Taro.showToast({ title: '请输入6位验证码', icon: 'none' })
      return
    }
    setVerifying(true)
    try {
      await verifySignCode(contractId, code)
      await executeSign(contractId)
      Taro.showToast({ title: '签署成功', icon: 'success' })
      setStep('result')
      setTimeout(() => Taro.navigateBack(), 2000)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '签署失败', icon: 'none' })
    } finally {
      setVerifying(false)
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

  const handleWebViewMessage = (e: any) => {
    const data = e.detail?.data?.[0]
    if (data?.type === 'sign_complete') {
      Taro.showToast({ title: '签署完成', icon: 'success' })
      setTimeout(() => Taro.navigateBack(), 1500)
    }
  }

  if (step === 'result') {
    return (
      <View className='contract-sign result-page'>
        <View className='result-icon'>✓</View>
        <Text className='result-title'>签署成功</Text>
        <Text className='result-hint'>合同已签署完成，即将返回</Text>
      </View>
    )
  }

  if (step === 'signing') {
    const signUrl = `${SIGN_H5_URL}/sign?taskId=${contractId}&token=${token}`
    return <WebView src={signUrl} onMessage={handleWebViewMessage} />
  }

  if (!detail) {
    return <View className='contract-sign'><Text>加载中...</Text></View>
  }

  if (step === 'verify') {
    return (
      <View className='contract-sign'>
        <View className='verify-section'>
          <Text className='verify-title'>签署意愿验证</Text>
          <Text className='verify-hint'>
            为确保签署意愿真实，已向您的手机发送验证码
          </Text>

          <View className='code-input-row'>
            <Input
              className='code-input'
              type='number'
              maxlength={6}
              placeholder='请输入6位验证码'
              value={code}
              onInput={(e) => setCode(e.detail.value)}
            />
            <Text
              className={`resend-btn ${countdown > 0 ? 'disabled' : ''}`}
              onClick={countdown === 0 ? handleSendCode : undefined}
            >
              {countdown > 0 ? `${countdown}s` : '重新发送'}
            </Text>
          </View>

          <View
            className={`btn btn-primary btn-block ${verifying ? 'btn-loading' : ''} ${code.length !== 6 ? 'btn-disabled' : ''}`}
            onClick={!verifying && code.length === 6 ? handleVerifyAndSign : undefined}
          >
            <Text>{verifying ? '签署中...' : '确认签署'}</Text>
          </View>

          <Text className='back-link' onClick={() => setStep('info')}>返回合同信息</Text>
        </View>
      </View>
    )
  }

  return (
    <View className='contract-sign'>
      <View className='sign-header'>
        <Text className='sign-title'>{detail.name}</Text>
        <Text className='sign-hint'>请确认合同内容后签署</Text>
      </View>

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
        <View className='btn btn-primary btn-block' onClick={handleStartSign}>
          <Text>开始签署</Text>
        </View>
        <View className='btn btn-default btn-block reject-btn' onClick={handleReject}>
          <Text>拒签</Text>
        </View>
      </View>
    </View>
  )
}
