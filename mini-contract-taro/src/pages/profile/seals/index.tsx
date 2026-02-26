import { useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
import { useRequireAuth } from '@/hooks/useAuth'
import { getSealList, deleteSeal, setDefaultSeal } from '@/api/seals'
import './index.scss'

interface SealItem {
  id: number
  name: string
  type: number
  seal_data: string
  is_default: number
}

export default function SealsPage() {
  useRequireAuth()
  const [seals, setSeals] = useState<SealItem[]>([])
  const [loading, setLoading] = useState(false)

  const fetchSeals = async () => {
    setLoading(true)
    try {
      const data = await getSealList({ pageNo: 1, pageSize: 50 })
      setSeals(data?.list || [])
    } catch {
      // 静默
    } finally {
      setLoading(false)
    }
  }

  useDidShow(() => {
    fetchSeals()
  })

  const handleDelete = async (id: number) => {
    const res = await Taro.showModal({ title: '提示', content: '确定删除该签名？' })
    if (res.confirm) {
      try {
        await deleteSeal(id)
        Taro.showToast({ title: '已删除', icon: 'success' })
        fetchSeals()
      } catch (e: any) {
        Taro.showToast({ title: e.message || '删除失败', icon: 'none' })
      }
    }
  }

  const handleSetDefault = async (id: number) => {
    try {
      await setDefaultSeal(id)
      Taro.showToast({ title: '已设为默认', icon: 'success' })
      fetchSeals()
    } catch (e: any) {
      Taro.showToast({ title: e.message || '操作失败', icon: 'none' })
    }
  }

  return (
    <View className='seals-page'>
      <View className='header'>
        <Text className='title'>我的签名</Text>
        <View
          className='btn btn-primary btn-small'
          onClick={() => Taro.navigateTo({ url: '/pages/profile/seal-create/index' })}
        >
          <Text>创建签名</Text>
        </View>
      </View>

      {seals.length === 0 && !loading ? (
        <View className='empty-wrap'>
          <Text className='empty-icon'>✍️</Text>
          <Text className='empty-text'>暂无签名</Text>
        </View>
      ) : (
        <View className='seal-list'>
          {seals.map((seal) => (
            <View key={seal.id} className='seal-item'>
              <View className='seal-preview'>
                <View
                  className='seal-image'
                  style={{ backgroundImage: `url(${seal.seal_data})` }}
                />
              </View>
              <View className='seal-info'>
                <Text className='seal-name'>
                  {seal.name}
                  {seal.is_default === 1 && <Text className='default-tag'>默认</Text>}
                </Text>
                <Text className='seal-type'>
                  {seal.type === 11 ? '个人签名' : '个人印章'}
                </Text>
              </View>
              <View className='seal-actions'>
                {seal.is_default !== 1 && (
                  <Text className='action-btn' onClick={() => handleSetDefault(seal.id)}>
                    设为默认
                  </Text>
                )}
                <Text className='action-btn delete' onClick={() => handleDelete(seal.id)}>
                  删除
                </Text>
              </View>
            </View>
          ))}
        </View>
      )}
    </View>
  )
}
