import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
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
    <View className='index-page min-h-screen bg-[#f7f8fa] pb-[40px]'>
      {/* 顶部统计卡片 */}
      <View className='stats-container'>
        <View className='bg-white rounded-[24px] p-[40px] shadow-lg'>
          <View className='mb-[40px] border-l-[8px] border-brand pl-[20px]'>
            <Text className='block text-[34px] text-[#333] font-extrabold mb-[8px]'>合同概览</Text>
            <Text className='text-[24px] text-[#999]'>实时数据更新</Text>
          </View>
          <View className='flex justify-between'>
            <View className='flex-1 text-center'>
              <Text className='block text-[48px] font-extrabold text-[#333] mb-[12px]'>{statistics?.totalCount || 0}</Text>
              <Text className='block text-[24px] text-[#666]'>全部</Text>
            </View>
            <View className='flex-1 text-center'>
              <Text className='block text-[48px] font-extrabold text-[#333] mb-[12px]'>{statistics?.draftCount || 0}</Text>
              <Text className='block text-[24px] text-[#666]'>草稿</Text>
            </View>
            <View className='flex-1 text-center'>
              <Text className='block text-[48px] font-extrabold text-[#faad14] mb-[12px]'>{statistics?.signingCount || 0}</Text>
              <Text className='block text-[24px] text-[#666]'>签署中</Text>
            </View>
            <View className='flex-1 text-center'>
              <Text className='block text-[48px] font-extrabold text-brand mb-[12px]'>{statistics?.completedCount || 0}</Text>
              <Text className='block text-[24px] text-[#666]'>已完成</Text>
            </View>
          </View>
        </View>
      </View>

      {/* 快捷操作 */}
      <View className='bg-white p-[40px] mx-[32px] mt-[20px] rounded-[24px] shadow-sm'>
        <Text className='block text-[30px] font-extrabold text-[#333] mb-[32px]'>快捷操作</Text>
        <View className='action-grid'>
          <View className='flex flex-col items-center' onClick={handleCreateContract}>
            <View className='action-icon create'>
              <Text className='text-white text-[40px] font-bold'>+</Text>
            </View>
            <Text className='text-[24px] text-[#333] font-medium'>创建合同</Text>
          </View>
          <View className='flex flex-col items-center' onClick={handleViewTemplates}>
            <View className='action-icon template'>
              <Text className='text-white text-[32px]'>T</Text>
            </View>
            <Text className='text-[24px] text-[#333] font-medium'>模板市场</Text>
          </View>
          <View
            className='flex flex-col items-center'
            onClick={() => {
              if (!requireAuth()) return
              Taro.switchTab({ url: '/pages/contract-manage/index' })
            }}
          >
            <View className='action-icon manage'>
              <Text className='text-white text-[32px]'>M</Text>
            </View>
            <Text className='text-[24px] text-[#333] font-medium'>合同管理</Text>
          </View>
          <View
            className='flex flex-col items-center'
            onClick={() => {
              if (!requireAuth()) return
              Taro.navigateTo({ url: '/pages/profile/seals/index' })
            }}
          >
            <View className='action-icon seal'>
              <Text className='text-white text-[32px]'>S</Text>
            </View>
            <Text className='text-[24px] text-[#333] font-medium'>我的签名</Text>
          </View>
        </View>
      </View>

      {/* 未登录提示 */}
      {!isLoggedIn && (
        <View className='bg-white p-[48px] mx-[32px] mt-[20px] rounded-[24px] text-center shadow-sm'>
          <Text className='block text-[26px] text-[#999] mb-[32px]'>登录后查看合同数据</Text>
          <View
            className='inline-flex items-center justify-center px-[40px] py-[16px] bg-brand rounded-full'
            onClick={() => Taro.navigateTo({ url: '/pages/login/index' })}
          >
            <Text className='text-white text-[28px] font-semibold'>立即登录</Text>
          </View>
        </View>
      )}
    </View>
  )
}
