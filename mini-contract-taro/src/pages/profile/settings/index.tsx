import { useState } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, Input } from '@tarojs/components'
import { useRequireAuth } from '@/hooks/useAuth'
import { useAuthStore } from '@/store/useAuthStore'
import { updateUserInfo, updatePassword } from '@/api/member'
import { sendSmsCode } from '@/api/auth'
import './index.scss'

export default function SettingsPage() {
  useRequireAuth()
  const { userInfo, setUserInfo } = useAuthStore()
  const [nickname, setNickname] = useState(userInfo?.nickname || '')
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [smsCode, setSmsCode] = useState('')
  const [countdown, setCountdown] = useState(0)
  const [loading, setLoading] = useState(false)

  const handleSaveNickname = async () => {
    if (!nickname.trim()) {
      Taro.showToast({ title: '昵称不能为空', icon: 'none' })
      return
    }
    setLoading(true)
    try {
      await updateUserInfo({ nickname: nickname.trim() })
      setUserInfo({ ...userInfo!, nickname: nickname.trim() })
      Taro.showToast({ title: '保存成功', icon: 'success' })
    } catch (e: any) {
      Taro.showToast({ title: e.message || '保存失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  const handleSendCode = async () => {
    if (countdown > 0) return
    try {
      await sendSmsCode({ mobile: userInfo?.mobile || '', scene: 3 })
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

  const handleChangePassword = async () => {
    if (!newPassword || newPassword.length < 6) {
      Taro.showToast({ title: '密码长度不能少于 6 位', icon: 'none' })
      return
    }
    if (!smsCode) {
      Taro.showToast({ title: '请输入验证码', icon: 'none' })
      return
    }
    setLoading(true)
    try {
      await updatePassword({ password: newPassword, code: smsCode })
      Taro.showToast({ title: '密码修改成功', icon: 'success' })
      setShowPasswordForm(false)
      setNewPassword('')
      setSmsCode('')
    } catch (e: any) {
      Taro.showToast({ title: e.message || '修改失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <View className='settings-page'>
      {/* 基本信息 */}
      <View className='section'>
        <Text className='section-title'>基本信息</Text>
        <View className='form-item'>
          <Text className='form-label'>手机号</Text>
          <Text className='form-value'>{userInfo?.mobile || '-'}</Text>
        </View>
        <View className='form-item'>
          <Text className='form-label'>昵称</Text>
          <Input
            value={nickname}
            onInput={(e) => setNickname(e.detail.value)}
            placeholder='请输入昵称'
            className='form-input'
          />
        </View>
        <View
          className={`btn btn-primary btn-small save-btn ${loading ? 'btn-loading' : ''}`}
          onClick={loading ? undefined : handleSaveNickname}
        >
          <Text>{loading ? '保存中...' : '保存'}</Text>
        </View>
      </View>

      {/* 修改密码 */}
      <View className='section'>
        <View className='password-header' onClick={() => setShowPasswordForm(!showPasswordForm)}>
          <Text className='section-title pw-title'>修改密码</Text>
          <Text className='toggle-arrow'>{showPasswordForm ? '▲' : '›'}</Text>
        </View>
        {showPasswordForm && (
          <View className='password-form'>
            <Input
              className='pw-input'
              placeholder='请输入新密码（至少 6 位）'
              password
              value={newPassword}
              onInput={(e) => setNewPassword(e.detail.value)}
            />
            <View className='sms-row'>
              <Input
                className='sms-input'
                placeholder='请输入验证码'
                type='number'
                maxlength={6}
                value={smsCode}
                onInput={(e) => setSmsCode(e.detail.value)}
              />
              <View
                className={`btn btn-default btn-small sms-btn ${countdown > 0 ? 'btn-disabled' : ''}`}
                onClick={countdown > 0 ? undefined : handleSendCode}
              >
                <Text>{countdown > 0 ? `${countdown}s` : '获取验证码'}</Text>
              </View>
            </View>
            <View
              className={`btn btn-primary btn-block ${loading ? 'btn-loading' : ''}`}
              onClick={loading ? undefined : handleChangePassword}
            >
              <Text>{loading ? '修改中...' : '确认修改'}</Text>
            </View>
          </View>
        )}
      </View>
    </View>
  )
}
