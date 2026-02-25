import { useState } from 'react'
import Taro from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
import { Input, Button, Cell } from '@nutui/nutui-react-taro'
import { useAuthStore } from '@/store/useAuthStore'
import { updateUserInfo, updatePassword } from '@/api/member'
import { sendSmsCode } from '@/api/auth'
import './index.scss'

export default function SettingsPage() {
  const { userInfo, setUserInfo } = useAuthStore()
  const [nickname, setNickname] = useState(userInfo?.nickname || '')
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [smsCode, setSmsCode] = useState('')
  const [countdown, setCountdown] = useState(0)
  const [loading, setLoading] = useState(false)

  /** 保存昵称 */
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

  /** 发送验证码 */
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

  /** 修改密码 */
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
            onChange={(val) => setNickname(val)}
            placeholder='请输入昵称'
            className='form-input'
          />
        </View>
        <Button
          type='primary'
          size='small'
          loading={loading}
          onClick={handleSaveNickname}
          className='save-btn'
        >
          保存
        </Button>
      </View>

      {/* 修改密码 */}
      <View className='section'>
        <Cell
          title='修改密码'
          extra={showPasswordForm ? '' : '>'}
          onClick={() => setShowPasswordForm(!showPasswordForm)}
        />
        {showPasswordForm && (
          <View className='password-form'>
            <Input
              placeholder='请输入新密码（至少 6 位）'
              type='password'
              value={newPassword}
              onChange={(val) => setNewPassword(val)}
            />
            <View className='sms-row'>
              <Input
                placeholder='请输入验证码'
                type='number'
                maxLength={6}
                value={smsCode}
                onChange={(val) => setSmsCode(val)}
                className='sms-input'
              />
              <Button
                size='small'
                disabled={countdown > 0}
                onClick={handleSendCode}
                className='sms-btn'
              >
                {countdown > 0 ? `${countdown}s` : '获取验证码'}
              </Button>
            </View>
            <Button
              type='primary'
              block
              loading={loading}
              onClick={handleChangePassword}
            >
              确认修改
            </Button>
          </View>
        )}
      </View>
    </View>
  )
}
