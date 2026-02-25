import { useState } from 'react'
import Taro from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
import { Button, Input, Tabs } from '@nutui/nutui-react-taro'
import { login, smsLogin, sendSmsCode, socialLogin } from '@/api/auth'
import { useAuthStore } from '@/store/useAuthStore'
import './index.scss'

export default function LoginPage() {
  const [activeTab, setActiveTab] = useState(0)
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
    // 返回上一页或跳转首页
    const pages = Taro.getCurrentPages()
    if (pages.length > 1) {
      Taro.navigateBack()
    } else {
      Taro.switchTab({ url: '/pages/index/index' })
    }
  }

  /** 密码登录 */
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

  /** 短信验证码登录 */
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

  /** 发送验证码 */
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

  /** 微信一键登录 */
  const handleWechatLogin = () => {
    setLoading(true)
    Taro.login({
      success: async (res) => {
        try {
          const data = await socialLogin({ type: 34, code: res.code })
          handleLoginSuccess(data)
        } catch (e: any) {
          Taro.showToast({ title: e.message || '微信登录失败', icon: 'none' })
        } finally {
          setLoading(false)
        }
      },
      fail: () => {
        setLoading(false)
        Taro.showToast({ title: '微信登录授权失败', icon: 'none' })
      },
    })
  }

  return (
    <View className='login-page'>
      <View className='login-header'>
        <Text className='login-title'>Mini Contract</Text>
        <Text className='login-subtitle'>电子合同签署平台</Text>
      </View>

      {/* 微信一键登录 */}
      <View className='wechat-login'>
        <Button
          type='primary'
          block
          loading={loading}
          onClick={handleWechatLogin}
        >
          微信一键登录
        </Button>
      </View>

      <View className='divider'>
        <View className='divider-line' />
        <Text className='divider-text'>或</Text>
        <View className='divider-line' />
      </View>

      {/* 手机号登录 */}
      <Tabs value={activeTab} onChange={(val) => setActiveTab(val as number)}>
        <Tabs.TabPane title='密码登录'>
          <View className='form'>
            <Input
              placeholder='请输入手机号'
              type='number'
              maxLength={11}
              value={mobile}
              onChange={(val) => setMobile(val)}
            />
            <Input
              placeholder='请输入密码'
              type='password'
              value={password}
              onChange={(val) => setPassword(val)}
            />
            <Button
              type='primary'
              block
              loading={loading}
              onClick={handlePasswordLogin}
              className='login-btn'
            >
              登录
            </Button>
          </View>
        </Tabs.TabPane>

        <Tabs.TabPane title='验证码登录'>
          <View className='form'>
            <Input
              placeholder='请输入手机号'
              type='number'
              maxLength={11}
              value={mobile}
              onChange={(val) => setMobile(val)}
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
              onClick={handleSmsLogin}
              className='login-btn'
            >
              登录
            </Button>
          </View>
        </Tabs.TabPane>
      </Tabs>
    </View>
  )
}
