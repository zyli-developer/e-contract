import { useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
import { Tabs, Empty } from '@nutui/nutui-react-taro'
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

const STATUS_MAP: Record<number, { text: string; color: string }> = {
  1: { text: '草稿', color: '#999' },
  2: { text: '签署中', color: '#fa8c16' },
  3: { text: '已完成', color: '#00C28A' },
  4: { text: '已取消', color: '#ff4d4f' },
  5: { text: '已拒签', color: '#ff4d4f' },
  6: { text: '已过期', color: '#999' },
}

export default function ContractManagePage() {
  const { isLoggedIn } = useAuth()
  const [activeTab, setActiveTab] = useState(0)
  const [statusFilter, setStatusFilter] = useState<number | undefined>(undefined)

  const { list, loading, hasMore, refresh, loadMore } = usePagination({
    fetchFn: async (params) => {
      const data = await getContractList({
        ...params,
        status: statusFilter,
      })
      return data || { list: [], total: 0 }
    },
  })

  useDidShow(() => {
    if (isLoggedIn) refresh()
  })

  const handleTabChange = (index: number) => {
    setActiveTab(index)
    setStatusFilter(STATUS_TABS[index].value)
    // 切换 tab 后刷新
    setTimeout(() => refresh(), 0)
  }

  if (!isLoggedIn) {
    return (
      <View className='contract-manage'>
        <View className='login-prompt'>
          <Text className='prompt-text'>请先登录查看合同</Text>
          <Text
            className='login-link'
            onClick={() => Taro.navigateTo({ url: '/pages/login/index' })}
          >
            去登录
          </Text>
        </View>
      </View>
    )
  }

  return (
    <View className='contract-manage'>
      <Tabs value={activeTab} onChange={handleTabChange}>
        {STATUS_TABS.map((tab) => (
          <Tabs.TabPane key={tab.label} title={tab.label} />
        ))}
      </Tabs>

      <View className='contract-list'>
        {list.length === 0 && !loading ? (
          <Empty description='暂无合同' />
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
                <Text className='contract-name'>{item.name}</Text>
                <Text
                  className='contract-status'
                  style={{ color: STATUS_MAP[item.status]?.color }}
                >
                  {STATUS_MAP[item.status]?.text || '未知'}
                </Text>
              </View>
              {item.participants?.length > 0 && (
                <Text className='participants'>
                  签署方：{item.participants.map((p: any) => p.name || p.mobile).join('、')}
                </Text>
              )}
              <Text className='create-time'>{item.create_time || ''}</Text>
            </View>
          ))
        )}

        {hasMore && (
          <View className='load-more' onClick={loadMore}>
            <Text>{loading ? '加载中...' : '加载更多'}</Text>
          </View>
        )}
      </View>
    </View>
  )
}
