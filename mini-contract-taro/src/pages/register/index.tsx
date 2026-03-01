import { useState } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, Input } from '@tarojs/components'
import { register, login } from '@/api/auth'
import { useAuthStore } from '@/store/useAuthStore'
import './index.scss'

export default function RegisterPage() {
  const [mobile, setMobile] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [nickname, setNickname] = useState('')
  const [loading, setLoading] = useState(false)

  const { setTokens, setUserId } = useAuthStore()

  const handleRegister = async () => {
    if (!mobile || mobile.length !== 11) {
      Taro.showToast({ title: '请输入11位手机号', icon: 'none' })
      return
    }
    if (!password || password.length < 6) {
      Taro.showToast({ title: '密码长度不能少于6位', icon: 'none' })
      return
    }
    if (password !== confirmPassword) {
      Taro.showToast({ title: '两次密码输入不一致', icon: 'none' })
      return
    }
    setLoading(true)
    try {
      await register({ mobile, password, nickname: nickname.trim() || undefined })
      // 注册成功后自动登录
      const data = await login({ mobile, password })
      setTokens(data.accessToken, data.refreshToken)
      setUserId(data.userId)
      Taro.showToast({ title: '注册成功', icon: 'success' })
      Taro.switchTab({ url: '/pages/index/index' })
    } catch (e: any) {
      Taro.showToast({ title: e.message || '注册失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <View className='register-page flex flex-col items-center min-h-screen'>
      {/* Header */}
      <View className='w-full pt-[100px] pb-[60px] text-center'>
        <View className='inline-flex items-center justify-center w-[140px] h-[140px] rounded-[40px] bg-white/25 mb-[32px] shadow-lg'>
          <Text className='text-white text-[56px] font-black tracking-[4px]'>MC</Text>
        </View>
        <Text className='block text-[44px] font-extrabold text-white mb-[12px] tracking-[2px]'>创建账号</Text>
        <Text className='block text-[26px] text-white/85 tracking-[1px]'>注册 Mini Contract 账号</Text>
      </View>

      {/* Card */}
      <View className='w-[calc(100%-64px)] mx-[32px] bg-white rounded-[40px] px-[48px] pt-[60px] pb-[48px] shadow-xl'>
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
              placeholder='请输入密码（至少6位）'
              value={password}
              onInput={(e) => setPassword(e.detail.value)}
            />
          </View>
        </View>

        <View className='mb-[32px]'>
          <Text className='block text-[24px] text-[#888] mb-[16px] pl-[8px] font-semibold'>确认密码</Text>
          <View className='bg-[#f7f8fa] rounded-[20px] px-[32px] h-[96px] flex items-center'>
            <Input
              className='w-full h-[96px] text-[30px] text-[#333] bg-transparent'
              password
              placeholder='请再次输入密码'
              value={confirmPassword}
              onInput={(e) => setConfirmPassword(e.detail.value)}
            />
          </View>
        </View>

        <View className='mb-[32px]'>
          <Text className='block text-[24px] text-[#888] mb-[16px] pl-[8px] font-semibold'>昵称（选填）</Text>
          <View className='bg-[#f7f8fa] rounded-[20px] px-[32px] h-[96px] flex items-center'>
            <Input
              className='w-full h-[96px] text-[30px] text-[#333] bg-transparent'
              placeholder='请输入昵称'
              value={nickname}
              onInput={(e) => setNickname(e.detail.value)}
            />
          </View>
        </View>

        <View
          className='mt-[48px] w-full h-[100px] rounded-full flex items-center justify-center submit-btn'
          onClick={handleRegister}
        >
          <Text className='text-[32px] font-bold text-white tracking-[4px]'>{loading ? '注册中...' : '注 册'}</Text>
        </View>

        <View className='mt-[32px] text-center'>
          <Text
            className='text-[26px] text-brand font-medium'
            onClick={() => Taro.navigateBack()}
          >
            已有账号？返回登录
          </Text>
        </View>
      </View>

      <View className='w-full py-[60px] pb-[80px]' />
    </View>
  )
}
