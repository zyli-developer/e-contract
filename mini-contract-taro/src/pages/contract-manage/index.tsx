import { useState, useCallback } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
import { useAuth } from '@/hooks/useAuth'
import { usePagination } from '@/hooks/usePagination'
import { getContractList } from '@/api/contracts'
import './index.scss'

const STATUS_TABS = [
  { label: '全部', value: undefined },
  { label: '草稿', value: 1 },
  { label: '签署中', value: 2 },
  { label: '已完成', value: 3 },
]

const STATUS_MAP: Record<number, { text: string; type: string }> = {
  1: { text: '草稿', type: 'default' },
  2: { text: '签署中', type: 'warning' },
  3: { text: '已完成', type: 'success' },
  4: { text: '已取消', type: 'danger' },
  5: { text: '已拒签', type: 'danger' },
  6: { text: '已过期', type: 'default' },
}

export default function ContractManagePage() {
  const { isLoggedIn } = useAuth()
  const [activeTab, setActiveTab] = useState(0)
  const [statusFilter, setStatusFilter] = useState<number | undefined>(undefined)

  const { list, loading, hasMore, refresh, loadMore } = usePagination({
    fetchFn: async (params) => {
      try {
        const data = await getContractList({
          ...params,
          ...(statusFilter != null ? { status: statusFilter } : {}),
        })
        return data || { list: [], total: 0 }
      } catch (e: any) {
        Taro.showToast({ title: e.message || '获取列表失败', icon: 'none' })
        return { list: [], total: 0 }
      }
    },
  })

  useDidShow(() => {
    if (isLoggedIn) refresh()
  })

  const handleTabChange = useCallback((index: number) => {
    setActiveTab(index)
    setStatusFilter(STATUS_TABS[index].value)
    setTimeout(() => refresh(), 50)
  }, [refresh])

  if (!isLoggedIn) {
    return (
      <View className='contract-manage'>
        <View className='login-prompt'>
          <Text className='prompt-icon'>📋</Text>
          <Text className='prompt-text'>登录后即可管理您的电子合同</Text>
          <Text
            className='login-link'
            onClick={() => Taro.navigateTo({ url: '/pages/login/index' })}
          >
            立即登录
          </Text>
        </View>
      </View>
    )
  }

  return (
    <View className='contract-manage'>
      <View className='tabs-wrapper'>
        <View className='tab-bar'>
          {STATUS_TABS.map((tab, index) => (
            <Text
              key={tab.label}
              className={`tab-item ${activeTab === index ? 'active' : ''}`}
              onClick={() => handleTabChange(index)}
            >
              {tab.label}
            </Text>
          ))}
        </View>
      </View>

      <View className='contract-list'>
        {list.length === 0 && !loading ? (
          <View className='empty-container'>
            <Text className='empty-icon'>📄</Text>
            <Text className='empty-text'>暂无合同记录</Text>
          </View>
        ) : (
          list.map((item: any) => (
            <View
              key={item.id}
              className='contract-card'
              onClick={() =>
                Taro.navigateTo({ url: `/pages/contract-detail/index?id=${item.id}` })
              }
            >
              <View className='card-header'>
                <View className='title-area'>
                  <Text className='title-icon'>📋</Text>
                  <Text className='contract-name'>{item.name}</Text>
                </View>
                <Text className={`status-tag status-tag-${STATUS_MAP[item.status]?.type || 'default'}`}>
                  {STATUS_MAP[item.status]?.text || '未知'}
                </Text>
              </View>

              <View className='card-body'>
                {item.participants?.length > 0 && (
                  <View className='info-row'>
                    <Text className='row-icon'>👤</Text>
                    <Text className='label'>签署方</Text>
                    <Text className='value'>
                      {item.participants.map((p: any) => p.name || p.mobile).join('、')}
                    </Text>
                  </View>
                )}
                <View className='info-row'>
                  <Text className='row-icon'>🕐</Text>
                  <Text className='label'>创建时间</Text>
                  <Text className='value'>{item.create_time || '-'}</Text>
                </View>
              </View>
            </View>
          ))
        )}

        {hasMore && (
          <View className='load-more' onClick={loadMore}>
            <Text>{loading ? '正在加载...' : '点击加载更多'}</Text>
          </View>
        )}
      </View>
    </View>
  )
}
