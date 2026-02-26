import { useState } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, Input } from '@tarojs/components'
import { login, smsLogin, sendSmsCode } from '@/api/auth'
import { useAuthStore } from '@/store/useAuthStore'
import './index.scss'

type TabType = 'password' | 'sms'

export default function LoginPage() {
  const [activeTab, setActiveTab] = useState<TabType>('password')
  const [mobile, setMobile] = useState('')
  const [password, setPassword] = useState('')
  const [smsCode, setSmsCode] = useState('')
  const [countdown, setCountdown] = useState(0)
  const [loading, setLoading] = useState(false)

  const { setTokens, setUserId } = useAuthStore()

  const handleLoginSuccess = (data: any) => {
    setTokens(data.accessToken, data.refreshToken)
    setUserId(data.userId)
    Taro.showToast({ title: '登录成功', icon: 'success' })
    const pages = Taro.getCurrentPages()
    if (pages.length > 1) {
      Taro.navigateBack()
    } else {
      Taro.switchTab({ url: '/pages/index/index' })
    }
  }

  const handlePasswordLogin = async () => {
    if (!mobile || !password) {
      Taro.showToast({ title: '请输入手机号和密码', icon: 'none' })
      return
    }
    setLoading(true)
    try {
      const data = await login({ mobile, password })
      handleLoginSuccess(data)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '登录失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  const handleSmsLogin = async () => {
    if (!mobile || !smsCode) {
      Taro.showToast({ title: '请输入手机号和验证码', icon: 'none' })
      return
    }
    setLoading(true)
    try {
      const data = await smsLogin({ mobile, code: smsCode })
      handleLoginSuccess(data)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '登录失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  const handleSendCode = async () => {
    if (!mobile) {
      Taro.showToast({ title: '请输入手机号', icon: 'none' })
      return
    }
    if (countdown > 0) return
    try {
      await sendSmsCode({ mobile, scene: 1 })
      Taro.showToast({ title: '验证码已发送', icon: 'success' })
      setCountdown(60)
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '发送失败', icon: 'none' })
    }
  }

  return (
    <View className='login-page flex flex-col items-center min-h-screen'>
      {/* Header */}
      <View className='w-full pt-[100px] pb-[60px] text-center'>
        <View className='inline-flex items-center justify-center w-[140px] h-[140px] rounded-[40px] bg-white/25 mb-[32px] shadow-lg'>
          <Text className='text-white text-[56px] font-black tracking-[4px]'>MC</Text>
        </View>
        <Text className='block text-[44px] font-extrabold text-white mb-[12px] tracking-[2px]'>Mini Contract</Text>
        <Text className='block text-[26px] text-white/85 tracking-[1px]'>电子合同签署平台</Text>
      </View>

      {/* Card */}
      <View className='w-[calc(100%-64px)] mx-[32px] bg-white rounded-[40px] px-[48px] pt-[60px] pb-[48px] shadow-xl'>
        {/* Tabs */}
        <View className='flex mb-[48px] bg-[#f5f7fa] rounded-[20px] p-[8px]'>
          <View
            className={`flex-1 text-center py-[20px] text-[28px] rounded-[16px] ${
              activeTab === 'password'
                ? 'text-brand font-extrabold bg-white shadow-sm'
                : 'text-[#999]'
            }`}
            onClick={() => setActiveTab('password')}
          >
            <Text>密码登录</Text>
          </View>
          <View
            className={`flex-1 text-center py-[20px] text-[28px] rounded-[16px] ${
              activeTab === 'sms'
                ? 'text-brand font-extrabold bg-white shadow-sm'
                : 'text-[#999]'
            }`}
            onClick={() => setActiveTab('sms')}
          >
            <Text>验证码登录</Text>
          </View>
        </View>

        {/* Password Form */}
        {activeTab === 'password' ? (
          <View>
            <View className='mb-[32px]'>
              <Text className='block text-[24px] text-[#888] mb-[16px] pl-[8px] font-semibold'>手机号</Text>
              <View className='bg-[#f7f8fa] rounded-[20px] px-[32px] h-[96px] flex items-center'>
                <Input
                  className='w-full h-[96px] text-[30px] text-[#333] bg-transparent'
                  type='number'
                  placeholder='请输入11位手机号'
                  maxlength={11}
                  value={mobile}
                  onInput={(e) => setMobile(e.detail.value)}
                />
              </View>
            </View>
            <View className='mb-[32px]'>
              <Text className='block text-[24px] text-[#888] mb-[16px] pl-[8px] font-semibold'>密码</Text>
              <View className='bg-[#f7f8fa] rounded-[20px] px-[32px] h-[96px] flex items-center'>
                <Input
                  className='w-full h-[96px] text-[30px] text-[#333] bg-transparent'
                  password
                  placeholder='请输入登录密码'
                  value={password}
                  onInput={(e) => setPassword(e.detail.value)}
                />
              </View>
            </View>
            <View
              className='mt-[48px] w-full h-[100px] rounded-full flex items-center justify-center submit-btn'
              onClick={handlePasswordLogin}
            >
              <Text className='text-[32px] font-bold text-white tracking-[4px]'>{loading ? '登录中...' : '登 录'}</Text>
            </View>
          </View>
        ) : (
          <View>
            <View className='mb-[32px]'>
              <Text className='block text-[24px] text-[#888] mb-[16px] pl-[8px] font-semibold'>手机号</Text>
              <View className='bg-[#f7f8fa] rounded-[20px] px-[32px] h-[96px] flex items-center'>
                <Input
                  className='w-full h-[96px] text-[30px] text-[#333] bg-transparent'
                  type='number'
                  placeholder='请输入11位手机号'
                  maxlength={11}
                  value={mobile}
                  onInput={(e) => setMobile(e.detail.value)}
                />
              </View>
            </View>
            <View className='mb-[32px]'>
              <Text className='block text-[24px] text-[#888] mb-[16px] pl-[8px] font-semibold'>验证码</Text>
              <View className='flex items-center gap-[20px]'>
                <View className='flex-1 bg-[#f7f8fa] rounded-[20px] px-[32px] h-[96px] flex items-center'>
                  <Input
                    className='w-full h-[96px] text-[30px] text-[#333] bg-transparent'
                    type='number'
                    placeholder='请输入验证码'
                    maxlength={6}
                    value={smsCode}
                    onInput={(e) => setSmsCode(e.detail.value)}
                  />
                </View>
                <View
                  className={`shrink-0 h-[96px] px-[28px] rounded-[20px] flex items-center justify-center border-[2px] ${
                    countdown > 0
                      ? 'bg-[#f5f5f5] border-transparent'
                      : 'bg-[#f0faf6] border-[#d4f0e5]'
                  }`}
                  onClick={handleSendCode}
                >
                  <Text className={`text-[24px] font-semibold whitespace-nowrap ${
                    countdown > 0 ? 'text-[#ccc]' : 'text-brand'
                  }`}>
                    {countdown > 0 ? `${countdown}s` : '获取验证码'}
                  </Text>
                </View>
              </View>
            </View>
            <View
              className='mt-[48px] w-full h-[100px] rounded-full flex items-center justify-center submit-btn'
              onClick={handleSmsLogin}
            >
              <Text className='text-[32px] font-bold text-white tracking-[4px]'>{loading ? '登录中...' : '登 录'}</Text>
            </View>
          </View>
        )}
      </View>

      {/* Footer */}
      <View className='w-full py-[60px] pb-[80px] text-center'>
        <Text className='text-[24px] text-[#ccc]'>
          登录即同意 <Text className='text-brand font-medium'>用户协议</Text> 和 <Text className='text-brand font-medium'>隐私政策</Text>
        </Text>
      </View>
    </View>
  )
}
