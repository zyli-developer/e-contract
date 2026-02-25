import { useState, useRef } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, Canvas } from '@tarojs/components'
import { Button, Tabs, Radio } from '@nutui/nutui-react-taro'
import { createSeal } from '@/api/seals'
import './index.scss'

export default function SealCreatePage() {
  const [activeTab, setActiveTab] = useState(0)
  const [sealType, setSealType] = useState(11) // 11=签名 12=印章
  const [loading, setLoading] = useState(false)

  /** 手绘签名 - 使用 Canvas */
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

    // 绘制
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

  const handleSaveDrawing = async () => {
    if (!hasDrawn) {
      Taro.showToast({ title: '请先签名', icon: 'none' })
      return
    }
    setLoading(true)
    try {
      // 导出 Canvas 为图片
      const res = await Taro.canvasToTempFilePath({
        canvasId: 'signCanvas',
        fileType: 'png',
      })
      // MVP: 直接用临时路径作为 seal_data
      await createSeal({
        name: sealType === 11 ? '我的签名' : '我的印章',
        type: sealType,
        seal_data: res.tempFilePath,
      })
      Taro.showToast({ title: '创建成功', icon: 'success' })
      setTimeout(() => Taro.navigateBack(), 1500)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '创建失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  /** 图片上传 */
  const handleUploadImage = async () => {
    try {
      const chooseRes = await Taro.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
      })
      const tempPath = chooseRes.tempFilePaths[0]

      setLoading(true)
      await createSeal({
        name: sealType === 11 ? '我的签名' : '我的印章',
        type: sealType,
        seal_data: tempPath,
      })
      Taro.showToast({ title: '创建成功', icon: 'success' })
      setTimeout(() => Taro.navigateBack(), 1500)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '创建失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <View className='seal-create-page'>
      {/* 类型选择 */}
      <View className='type-section'>
        <Text className='section-label'>签名类型</Text>
        <Radio.Group
          value={String(sealType)}
          direction='horizontal'
          onChange={(val) => setSealType(Number(val))}
        >
          <Radio value='11'>个人签名</Radio>
          <Radio value='12'>个人印章</Radio>
        </Radio.Group>
      </View>

      {/* 创建方式 */}
      <Tabs value={activeTab} onChange={(val) => setActiveTab(val as number)}>
        <Tabs.TabPane title='手绘签名'>
          <View className='canvas-section'>
            <View className='canvas-wrapper'>
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
              <Button size='small' onClick={handleClear}>清除</Button>
              <Button
                type='primary'
                size='small'
                loading={loading}
                onClick={handleSaveDrawing}
              >
                保存签名
              </Button>
            </View>
          </View>
        </Tabs.TabPane>

        <Tabs.TabPane title='图片上传'>
          <View className='upload-section'>
            <Text className='upload-hint'>从相册选择或拍照上传签名图片</Text>
            <Button
              type='primary'
              block
              loading={loading}
              onClick={handleUploadImage}
            >
              选择图片
            </Button>
          </View>
        </Tabs.TabPane>
      </Tabs>
    </View>
  )
}
