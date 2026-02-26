import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text, Image } from '@tarojs/components'
import { useAuth } from '@/hooks/useAuth'
import { useAuthStore } from '@/store/useAuthStore'
import { getUserInfo } from '@/api/member'
import { logout as logoutApi } from '@/api/auth'
import './index.scss'

export default function ProfilePage() {
  const { isLoggedIn } = useAuth()
  const { userInfo, setUserInfo, logout, token } = useAuthStore()

  const fetchUserInfo = async () => {
    if (!token) return
    try {
      const info = await getUserInfo()
      setUserInfo({
        nickname: info.nickname || '',
        avatar: info.avatar || '',
        mobile: info.mobile || '',
      })
    } catch {
      // 静默失败
    }
  }

  useDidShow(() => {
    if (isLoggedIn) {
      fetchUserInfo()
    }
  })

  const handleLogout = async () => {
    const res = await Taro.showModal({
      title: '提示',
      content: '确定退出登录？',
    })
    if (res.confirm) {
      try {
        await logoutApi()
      } catch {
        // 忽略
      }
      logout()
      Taro.showToast({ title: '已退出登录', icon: 'success' })
    }
  }

  if (!isLoggedIn) {
    return (
      <View className='profile-page'>
        <View className='profile-header-guest'>
          <View className='avatar-placeholder'>
            <Text className='avatar-placeholder-text'>👤</Text>
          </View>
          <Text
            className='login-link'
            onClick={() => Taro.navigateTo({ url: '/pages/login/index' })}
          >
            点击登录 / 注册
          </Text>
          <Text className='guest-hint'>登录后体验完整电子合同服务</Text>
        </View>
      </View>
    )
  }

  return (
    <View className='profile-page'>
      {/* 用户信息头部 */}
      <View className='profile-header'>
        <View className='avatar-wrap'>
          {userInfo?.avatar ? (
            <Image className='avatar' src={userInfo.avatar} mode='aspectFill' />
          ) : (
            <View className='avatar-default'>
              <Text className='avatar-text'>{userInfo?.nickname?.[0] || '用'}</Text>
            </View>
          )}
        </View>
        <View className='profile-info'>
          <Text className='nickname'>{userInfo?.nickname || '未设置昵称'}</Text>
          <View className='mobile-tag'>
            <Text className='mobile'>{userInfo?.mobile || ''}</Text>
          </View>
        </View>
      </View>

      {/* 功能列表 */}
      <View className='menu-container'>
        <View className='menu-group'>
          <View
            className='menu-item'
            onClick={() => Taro.navigateTo({ url: '/pages/profile/seals/index' })}
          >
            <Text className='menu-icon'>✍️</Text>
            <Text className='menu-title'>个人签名管理</Text>
            <Text className='menu-arrow'>›</Text>
          </View>
          <View
            className='menu-item'
            onClick={() => Taro.navigateTo({ url: '/pages/profile/settings/index' })}
          >
            <Text className='menu-icon'>⚙️</Text>
            <Text className='menu-title'>修改个人信息</Text>
            <Text className='menu-arrow'>›</Text>
          </View>
        </View>

        <View className='menu-group logout-group'>
          <View className='menu-item logout-item' onClick={handleLogout}>
            <Text className='menu-icon'>🚪</Text>
            <Text className='menu-title logout-text'>退出登录</Text>
          </View>
        </View>
      </View>

      <View className='version-info'>
        <Text>Version 1.0.0</Text>
      </View>
    </View>
  )
}
