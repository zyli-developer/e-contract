import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text, Image } from '@tarojs/components'
import { Cell, Avatar } from '@nutui/nutui-react-taro'
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
          <Avatar size='large' />
          <Text
            className='login-link'
            onClick={() => Taro.navigateTo({ url: '/pages/login/index' })}
          >
            点击登录
          </Text>
        </View>
      </View>
    )
  }

  return (
    <View className='profile-page'>
      {/* 用户信息头部 */}
      <View className='profile-header'>
        {userInfo?.avatar ? (
          <Image className='avatar' src={userInfo.avatar} mode='aspectFill' />
        ) : (
          <Avatar size='large'>{userInfo?.nickname?.[0] || '用'}</Avatar>
        )}
        <View className='profile-info'>
          <Text className='nickname'>{userInfo?.nickname || '未设置昵称'}</Text>
          <Text className='mobile'>{userInfo?.mobile || ''}</Text>
        </View>
      </View>

      {/* 功能列表 */}
      <View className='menu-group'>
        <Cell
          title='个人签名管理'
          extra='>'
          onClick={() => Taro.navigateTo({ url: '/pages/profile/seals/index' })}
        />
        <Cell
          title='修改个人信息'
          extra='>'
          onClick={() => Taro.navigateTo({ url: '/pages/profile/settings/index' })}
        />
      </View>

      <View className='logout-section'>
        <Cell
          title='退出登录'
          onClick={handleLogout}
          className='logout-cell'
        />
      </View>
    </View>
  )
}
