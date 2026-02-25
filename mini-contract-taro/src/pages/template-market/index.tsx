import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, ScrollView } from '@tarojs/components'
import { SearchBar, Tabs, Empty } from '@nutui/nutui-react-taro'
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

  const handleCategoryChange = (index: number) => {
    const cat = categories[index]?.code || ''
    setActiveCategory(cat)
    fetchTemplates(cat, keyword)
  }

  const handleSearch = (val: string) => {
    setKeyword(val)
    fetchTemplates(activeCategory, val)
  }

  const goToDetail = (id: number) => {
    Taro.navigateTo({ url: `/pages/template-detail/index?id=${id}` })
  }

  return (
    <View className='template-market'>
      <SearchBar
        placeholder='搜索合同模板'
        value={keyword}
        onChange={(val) => setKeyword(val)}
        onSearch={handleSearch}
      />

      {hotTemplates.length > 0 && !keyword && (
        <View className='hot-section'>
          <Text className='section-title'>热门模板</Text>
          <ScrollView scrollX className='hot-scroll'>
            {hotTemplates.map((t) => (
              <View key={t.id} className='hot-item' onClick={() => goToDetail(t.id)}>
                <Text className='hot-name'>{t.name}</Text>
                <Text className='hot-count'>{t.use_count} 次使用</Text>
              </View>
            ))}
          </ScrollView>
        </View>
      )}

      {categories.length > 0 && (
        <Tabs
          value={categories.findIndex((c) => c.code === activeCategory)}
          onChange={handleCategoryChange}
        >
          {categories.map((cat) => (
            <Tabs.TabPane key={cat.code} title={cat.name} />
          ))}
        </Tabs>
      )}

      <View className='template-list'>
        {templates.length === 0 && !loading ? (
          <Empty description='暂无模板' />
        ) : (
          templates.map((t) => (
            <View key={t.id} className='template-card' onClick={() => goToDetail(t.id)}>
              <Text className='template-name'>{t.name}</Text>
              {t.description && <Text className='template-desc'>{t.description}</Text>}
              <Text className='template-count'>{t.use_count} 次使用</Text>
            </View>
          ))
        )}
      </View>
    </View>
  )
}
