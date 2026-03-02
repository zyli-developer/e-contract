import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, ScrollView, Input } from '@tarojs/components'
import { useRequireLandlord } from '@/hooks/useAuth'
import { searchTemplates, getCategories, getHotTemplates } from '@/api/templates'
import './index.scss'

interface TemplateItem {
  id: number
  name: string
  description: string | null
  category: string
  use_count: number
}

interface Category {
  code: string
  name: string
}

export default function TemplateMarketPage() {
  useRequireLandlord()
  const [keyword, setKeyword] = useState('')
  const [categories, setCategories] = useState<Category[]>([])
  const [activeCategory, setActiveCategory] = useState('')
  const [templates, setTemplates] = useState<TemplateItem[]>([])
  const [hotTemplates, setHotTemplates] = useState<TemplateItem[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchCategories()
    fetchHot()
    fetchTemplates()
  }, [])

  const fetchCategories = async () => {
    try {
      const data = await getCategories()
      setCategories([{ code: '', name: '全部' }, ...(data || [])])
    } catch {}
  }

  const fetchHot = async () => {
    try {
      const data = await getHotTemplates(6)
      setHotTemplates(data || [])
    } catch {}
  }

  const fetchTemplates = async (cat?: string, kw?: string) => {
    setLoading(true)
    try {
      const params: Record<string, any> = { pageNo: 1, pageSize: 20 }
      if (cat) params.category = cat
      if (kw) params.keyword = kw
      const data = await searchTemplates(params)
      setTemplates(data?.list || [])
    } catch {} finally {
      setLoading(false)
    }
  }

  const handleCategoryChange = (code: string) => {
    setActiveCategory(code)
    fetchTemplates(code, keyword)
  }

  const handleSearch = () => {
    fetchTemplates(activeCategory, keyword)
  }

  const goToDetail = (id: number) => {
    Taro.navigateTo({ url: `/pages/template-detail/index?id=${id}` })
  }

  return (
    <View className='template-market'>
      <View className='search-header'>
        <View className='search-bar'>
          <Text className='search-icon'>🔍</Text>
          <Input
            className='search-input'
            placeholder='搜索合同模板'
            value={keyword}
            onInput={(e) => setKeyword(e.detail.value)}
            onConfirm={handleSearch}
          />
        </View>
      </View>

      {hotTemplates.length > 0 && !keyword && (
        <View className='hot-section'>
          <View className='section-header'>
            <Text className='hot-star'>🔥</Text>
            <Text className='section-title'>热门模板</Text>
          </View>
          <ScrollView scrollX className='hot-scroll'>
            <View className='hot-list-inner'>
              {hotTemplates.map((t) => (
                <View key={t.id} className='hot-card' onClick={() => goToDetail(t.id)}>
                  <Text className='hot-name'>{t.name}</Text>
                  <View className='hot-footer'>
                    <Text className='hot-count'>{t.use_count} 次使用</Text>
                  </View>
                </View>
              ))}
            </View>
          </ScrollView>
        </View>
      )}

      <View className='category-tabs'>
        {categories.length > 0 && (
          <ScrollView scrollX className='category-scroll'>
            <View className='category-list'>
              {categories.map((cat) => (
                <Text
                  key={cat.code}
                  className={`category-item ${activeCategory === cat.code ? 'active' : ''}`}
                  onClick={() => handleCategoryChange(cat.code)}
                >
                  {cat.name}
                </Text>
              ))}
            </View>
          </ScrollView>
        )}
      </View>

      <View className='template-list'>
        {templates.length === 0 && !loading ? (
          <View className='empty-wrap'>
            <Text className='empty-icon'>📄</Text>
            <Text className='empty-text'>暂无相关模板</Text>
          </View>
        ) : (
          templates.map((t) => (
            <View key={t.id} className='template-card' onClick={() => goToDetail(t.id)}>
              <View className='card-main'>
                <Text className='template-name'>{t.name}</Text>
                {t.description && <Text className='template-desc'>{t.description}</Text>}
              </View>
              <View className='card-footer'>
                <Text className='category-tag'>{t.category || '通用'}</Text>
                <Text className='use-count'>{t.use_count} 人已用</Text>
              </View>
            </View>
          ))
        )}
      </View>
    </View>
  )
}
