import { useState, useRef } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, Canvas } from '@tarojs/components'
import { useRequireAuth } from '@/hooks/useAuth'
import { createSeal } from '@/api/seals'
import { BASE_URL } from '@/api/config'
import { useAuthStore } from '@/store/useAuthStore'
import './index.scss'

export default function SealCreatePage() {
  useRequireAuth()
  const [activeTab, setActiveTab] = useState(0)
  const [sealType, setSealType] = useState(11) // 11=签名 12=印章
  const [loading, setLoading] = useState(false)

  const [isDrawing, setIsDrawing] = useState(false)
  const [hasDrawn, setHasDrawn] = useState(false)
  const pointsRef = useRef<{ x: number; y: number }[]>([])

  const handleTouchStart = (e: any) => {
    const touch = e.touches[0]
    pointsRef.current = [{ x: touch.x, y: touch.y }]
    setIsDrawing(true)
  }

  const handleTouchMove = (e: any) => {
    if (!isDrawing) return
    const touch = e.touches[0]
    pointsRef.current.push({ x: touch.x, y: touch.y })
    setHasDrawn(true)

    const ctx = Taro.createCanvasContext('signCanvas')
    const points = pointsRef.current
    if (points.length >= 2) {
      ctx.setStrokeStyle('#000')
      ctx.setLineWidth(3)
      ctx.setLineCap('round')
      ctx.setLineJoin('round')
      ctx.beginPath()
      ctx.moveTo(points[points.length - 2].x, points[points.length - 2].y)
      ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y)
      ctx.stroke()
      ctx.draw(true)
    }
  }

  const handleTouchEnd = () => {
    setIsDrawing(false)
  }

  const handleClear = () => {
    const ctx = Taro.createCanvasContext('signCanvas')
    ctx.clearRect(0, 0, 600, 300)
    ctx.draw()
    setHasDrawn(false)
    pointsRef.current = []
  }

  /** 将本地临时文件上传到服务器，返回服务器 URL */
  const uploadToServer = async (tempFilePath: string): Promise<string> => {
    const { token } = useAuthStore.getState()
    const uploadRes = await Taro.uploadFile({
      url: `${BASE_URL}/infra/file/upload`,
      filePath: tempFilePath,
      name: 'file',
      header: { Authorization: `Bearer ${token}` },
    })
    const data = JSON.parse(uploadRes.data)
    if (data.code === 0 || data.code === 200) {
      return data.data.url
    }
    throw new Error(data.msg || '上传失败')
  }

  const handleSaveDrawing = async () => {
    if (!hasDrawn) {
      Taro.showToast({ title: '请先签名', icon: 'none' })
      return
    }
    setLoading(true)
    try {
      const res = await Taro.canvasToTempFilePath({
        canvasId: 'signCanvas',
        fileType: 'png',
      })
      const serverUrl = await uploadToServer(res.tempFilePath)
      await createSeal({
        name: sealType === 11 ? '我的签名' : '我的印章',
        type: sealType,
        seal_data: serverUrl,
      })
      Taro.showToast({ title: '创建成功', icon: 'success' })
      setTimeout(() => Taro.navigateBack(), 1500)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '创建失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  const handleUploadImage = async () => {
    try {
      const chooseRes = await Taro.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
      })
      const tempPath = chooseRes.tempFilePaths[0]

      setLoading(true)
      const serverUrl = await uploadToServer(tempPath)
      await createSeal({
        name: sealType === 11 ? '我的签名' : '我的印章',
        type: sealType,
        seal_data: serverUrl,
      })
      Taro.showToast({ title: '创建成功', icon: 'success' })
      setTimeout(() => Taro.navigateBack(), 1500)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '创建失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  const TABS = ['手绘签名', '图片上传']

  return (
    <View className='seal-create-page'>
      {/* 类型选择 */}
      <View className='type-section'>
        <Text className='section-label'>签名类型</Text>
        <View className='radio-group'>
          <View
            className={`radio-item ${sealType === 11 ? 'active' : ''}`}
            onClick={() => setSealType(11)}
          >
            <View className='radio-dot'>{sealType === 11 && <View className='radio-inner' />}</View>
            <Text className='radio-label'>个人签名</Text>
          </View>
          <View
            className={`radio-item ${sealType === 12 ? 'active' : ''}`}
            onClick={() => setSealType(12)}
          >
            <View className='radio-dot'>{sealType === 12 && <View className='radio-inner' />}</View>
            <Text className='radio-label'>个人印章</Text>
          </View>
        </View>
      </View>

      {/* 创建方式 Tab */}
      <View className='tab-bar'>
        {TABS.map((tab, index) => (
          <Text
            key={tab}
            className={`tab-item ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
          >
            {tab}
          </Text>
        ))}
      </View>

      {activeTab === 0 ? (
        <View className='canvas-section'>
          <View className='canvas-wrapper' catchMove>
            <Canvas
              canvasId='signCanvas'
              className='sign-canvas'
              onTouchStart={handleTouchStart}
              onTouchMove={handleTouchMove}
              onTouchEnd={handleTouchEnd}
            />
            {!hasDrawn && (
              <Text className='canvas-placeholder'>请在此处签名</Text>
            )}
          </View>
          <View className='canvas-actions'>
            <View className='btn btn-default btn-small' onClick={handleClear}>
              <Text>清除</Text>
            </View>
            <View
              className={`btn btn-primary btn-small ${loading ? 'btn-loading' : ''}`}
              onClick={loading ? undefined : handleSaveDrawing}
            >
              <Text>{loading ? '保存中...' : '保存签名'}</Text>
            </View>
          </View>
        </View>
      ) : (
        <View className='upload-section'>
          <Text className='upload-hint'>从相册选择或拍照上传签名图片</Text>
          <View
            className={`btn btn-primary btn-block ${loading ? 'btn-loading' : ''}`}
            onClick={loading ? undefined : handleUploadImage}
          >
            <Text>{loading ? '上传中...' : '选择图片'}</Text>
          </View>
        </View>
      )}
    </View>
  )
}
