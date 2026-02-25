import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
import { Button } from '@nutui/nutui-react-taro'
import { useAuth } from '@/hooks/useAuth'
import { useContractStore } from '@/store/useContractStore'
import { getStatistics } from '@/api/contracts'
import './index.scss'

export default function IndexPage() {
  const { isLoggedIn, requireAuth } = useAuth()
  const { statistics, setStatistics } = useContractStore()

  useDidShow(() => {
    if (isLoggedIn) {
      fetchStats()
    }
  })

  const fetchStats = async () => {
    try {
      const data = await getStatistics()
      if (data) setStatistics(data)
    } catch {
      // 静默
    }
  }

  const handleCreateContract = () => {
    if (!requireAuth()) return
    Taro.navigateTo({ url: '/pages/contract-create/index' })
  }

  const handleViewTemplates = () => {
    if (!requireAuth()) return
    Taro.navigateTo({ url: '/pages/template-market/index' })
  }

  return (
    <View className='index-page'>
      {/* 顶部统计卡片 */}
      <View className='stats-card'>
        <Text className='stats-title'>合同概览</Text>
        <View className='stats-grid'>
          <View className='stat-item'>
            <Text className='stat-value'>{statistics?.totalCount || 0}</Text>
            <Text className='stat-label'>全部</Text>
          </View>
          <View className='stat-item'>
            <Text className='stat-value'>{statistics?.draftCount || 0}</Text>
            <Text className='stat-label'>草稿</Text>
          </View>
          <View className='stat-item'>
            <Text className='stat-value signing'>{statistics?.signingCount || 0}</Text>
            <Text className='stat-label'>签署中</Text>
          </View>
          <View className='stat-item'>
            <Text className='stat-value completed'>{statistics?.completedCount || 0}</Text>
            <Text className='stat-label'>已完成</Text>
          </View>
        </View>
      </View>

      {/* 快捷操作 */}
      <View className='quick-actions'>
        <Text className='section-title'>快捷操作</Text>
        <View className='action-grid'>
          <View className='action-item' onClick={handleCreateContract}>
            <View className='action-icon create'>+</View>
            <Text className='action-text'>创建合同</Text>
          </View>
          <View className='action-item' onClick={handleViewTemplates}>
            <View className='action-icon template'>T</View>
            <Text className='action-text'>模板市场</Text>
          </View>
          <View
            className='action-item'
            onClick={() => {
              if (!requireAuth()) return
              Taro.switchTab({ url: '/pages/contract-manage/index' })
            }}
          >
            <View className='action-icon manage'>M</View>
            <Text className='action-text'>合同管理</Text>
          </View>
          <View
            className='action-item'
            onClick={() => {
              if (!requireAuth()) return
              Taro.navigateTo({ url: '/pages/profile/seals/index' })
            }}
          >
            <View className='action-icon seal'>S</View>
            <Text className='action-text'>我的签名</Text>
          </View>
        </View>
      </View>

      {/* 未登录提示 */}
      {!isLoggedIn && (
        <View className='login-prompt'>
          <Text className='prompt-text'>登录后查看合同数据</Text>
          <Button
            type='primary'
            size='small'
            onClick={() => Taro.navigateTo({ url: '/pages/login/index' })}
          >
            立即登录
          </Button>
        </View>
      )}
    </View>
  )
}
