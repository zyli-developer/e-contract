import { useState } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, Input } from '@tarojs/components'
import { login } from '@/api/auth'
import { useAuthStore } from '@/store/useAuthStore'
import Logo from '@/components/Logo'
import './index.scss'

export default function LoginPage() {
  const [mobile, setMobile] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const { setTokens, setUserId } = useAuthStore()

  const handleLogin = async () => {
    if (!mobile || !password) {
      Taro.showToast({ title: '请输入手机号和密码', icon: 'none' })
      return
    }
    setLoading(true)
    try {
      const data = await login({ mobile, password })
      setTokens(data.accessToken, data.refreshToken)
      setUserId(data.userId)
      useAuthStore.getState().setRole(data.role || 'landlord')
      Taro.showToast({ title: '登录成功', icon: 'success' })
      const pages = Taro.getCurrentPages()
      if (pages.length > 1) {
        Taro.navigateBack()
      } else {
        Taro.switchTab({ url: '/pages/index/index' })
      }
    } catch (e: any) {
      Taro.showToast({ title: e.message || '登录失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <View className='login-page flex flex-col items-center min-h-screen'>
      {/* Header */}
      <View className='w-full pt-[80px] pb-[60px] text-center'>
        <View className='inline-flex items-center justify-center w-[160px] h-[160px] rounded-[40px] bg-white mb-[32px] shadow-lg'>
          <Logo size={120} />
        </View>
        <Text className='block text-[44px] font-extrabold text-white mb-[12px] tracking-[2px]'>点点租约</Text>
        <Text className='block text-[26px] text-white/85 tracking-[1px]'>租房的第一份安全感，从‘点点’开始。</Text>
      </View>

      {/* Card */}
      <View className='w-[calc(100%-64px)] mx-[32px] bg-white rounded-[40px] px-[48px] pt-[60px] pb-[48px] shadow-xl'>
        <Text className='block text-[36px] font-extrabold text-[#333] mb-[48px] text-center'>密码登录</Text>

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
          onClick={handleLogin}
        >
          <Text className='text-[32px] font-bold text-white tracking-[4px]'>{loading ? '登录中...' : '登 录'}</Text>
        </View>

        <View className='mt-[32px] text-center'>
          <Text
            className='text-[26px] text-brand font-medium'
            onClick={() => Taro.navigateTo({ url: '/pages/register/index' })}
          >
            还没有账号？立即注册
          </Text>
        </View>
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
