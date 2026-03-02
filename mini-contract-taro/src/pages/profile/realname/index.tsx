import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, Input, Image } from '@tarojs/components'
import { useRequireAuth } from '@/hooks/useAuth'
import { getUserInfo, verifyRealName } from '@/api/member'
import { useAuthStore } from '@/store/useAuthStore'
import { BASE_URL } from '@/api/config'
import './index.scss'

export default function RealNamePage() {
  useRequireAuth()
  const [verified, setVerified] = useState(false)
  const [maskedName, setMaskedName] = useState('')
  const [realName, setRealName] = useState('')
  const [idCard, setIdCard] = useState('')
  const [frontImage, setFrontImage] = useState('')
  const [backImage, setBackImage] = useState('')
  const [loading, setLoading] = useState(false)
  const [pageLoading, setPageLoading] = useState(true)

  useEffect(() => {
    loadStatus()
  }, [])

  const loadStatus = async () => {
    try {
      const info = await getUserInfo()
      if (info.real_name_verified === 1) {
        setVerified(true)
        setMaskedName(info.real_name || '')
      }
    } catch {
      // ignore
    } finally {
      setPageLoading(false)
    }
  }

  const validateIdCard = (value: string) => {
    return /^\d{17}[\dXx]$/.test(value)
  }

  /** 选择并上传图片，返回服务器 URL */
  const chooseAndUpload = async (type: 'front' | 'back'): Promise<string | null> => {
    try {
      const chooseRes = await Taro.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
      })

      const tempPath = chooseRes.tempFilePaths[0]
      // 先显示本地预览
      if (type === 'front') setFrontImage(tempPath)
      else setBackImage(tempPath)

      // 上传到服务器
      const { token } = useAuthStore.getState()
      const uploadRes = await Taro.uploadFile({
        url: `${BASE_URL}/infra/file/upload`,
        filePath: tempPath,
        name: 'file',
        header: { Authorization: `Bearer ${token}` },
      })

      const data = JSON.parse(uploadRes.data)
      if (data.code === 0 || data.code === 200) {
        return data.data.url
      }
      Taro.showToast({ title: data.msg || '上传失败', icon: 'none' })
      return null
    } catch {
      Taro.showToast({ title: '选择图片失败', icon: 'none' })
      return null
    }
  }

  const handleChooseFront = () => { chooseAndUpload('front') }
  const handleChooseBack = () => { chooseAndUpload('back') }

  const handleSubmit = async () => {
    const name = realName.trim()
    if (!name) {
      Taro.showToast({ title: '请输入真实姓名', icon: 'none' })
      return
    }
    const card = idCard.trim()
    if (!validateIdCard(card)) {
      Taro.showToast({ title: '请输入正确的18位身份证号', icon: 'none' })
      return
    }
    if (!frontImage) {
      Taro.showToast({ title: '请上传身份证正面照片', icon: 'none' })
      return
    }
    if (!backImage) {
      Taro.showToast({ title: '请上传身份证背面照片', icon: 'none' })
      return
    }

    setLoading(true)
    try {
      // 上传正面照片
      Taro.showLoading({ title: '上传正面照片...' })
      const frontUrl = await uploadImage(frontImage)
      if (!frontUrl) { setLoading(false); return }

      // 上传背面照片
      Taro.showLoading({ title: '上传背面照片...' })
      const backUrl = await uploadImage(backImage)
      if (!backUrl) { setLoading(false); return }

      // 提交认证
      Taro.showLoading({ title: '认证中...' })
      const result = await verifyRealName({
        real_name: name,
        id_card: card,
        id_card_front_url: frontUrl,
        id_card_back_url: backUrl,
      })
      Taro.hideLoading()

      setVerified(true)
      setMaskedName(result.real_name || name)
      Taro.showToast({ title: '认证成功', icon: 'success' })
    } catch (e: any) {
      Taro.hideLoading()
      Taro.showToast({ title: e.message || '认证失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  /** 上传已选择的图片到服务器 */
  const uploadImage = async (tempPath: string): Promise<string | null> => {
    // 如果已经是服务器 URL（以 /static 开头），直接返回
    if (tempPath.startsWith('/static')) return tempPath

    try {
      const { token } = useAuthStore.getState()
      const uploadRes = await Taro.uploadFile({
        url: `${BASE_URL}/infra/file/upload`,
        filePath: tempPath,
        name: 'file',
        header: { Authorization: `Bearer ${token}` },
      })

      const data = JSON.parse(uploadRes.data)
      if (data.code === 0 || data.code === 200) {
        return data.data.url
      }
      Taro.showToast({ title: data.msg || '上传失败', icon: 'none' })
      return null
    } catch {
      Taro.showToast({ title: '图片上传失败', icon: 'none' })
      return null
    }
  }

  if (pageLoading) {
    return (
      <View className='realname-page'>
        <Text className='loading-text'>加载中...</Text>
      </View>
    )
  }

  // 已认证状态
  if (verified) {
    return (
      <View className='realname-page'>
        <View className='success-card'>
          <View className='success-icon'>
            <Text className='success-icon-text'>&#10003;</Text>
          </View>
          <Text className='success-title'>实名认证成功</Text>
          <Text className='success-desc'>您已完成实名认证</Text>
          <View className='info-row'>
            <Text className='info-label'>真实姓名</Text>
            <Text className='info-value'>{maskedName}</Text>
          </View>
        </View>
      </View>
    )
  }

  // 未认证状态：表单
  return (
    <View className='realname-page'>
      <View className='notice-bar'>
        <Text className='notice-text'>
          实名认证用于保障租约合同的法律效力，认证后方可签署合同
        </Text>
      </View>

      <View className='form-card'>
        <View className='form-item'>
          <Text className='form-label'>真实姓名</Text>
          <Input
            className='form-input'
            placeholder='请输入身份证上的姓名'
            value={realName}
            onInput={(e) => setRealName(e.detail.value)}
          />
        </View>
        <View className='form-item'>
          <Text className='form-label'>身份证号</Text>
          <Input
            className='form-input'
            placeholder='请输入18位身份证号码'
            maxlength={18}
            value={idCard}
            onInput={(e) => setIdCard(e.detail.value)}
          />
        </View>
      </View>

      <View className='upload-card'>
        <Text className='upload-title'>上传身份证照片</Text>
        <View className='upload-row'>
          <View className='upload-box' onClick={handleChooseFront}>
            {frontImage ? (
              <Image className='upload-preview' src={frontImage} mode='aspectFit' />
            ) : (
              <View className='upload-placeholder'>
                <Text className='upload-plus'>+</Text>
                <Text className='upload-label'>人像面</Text>
              </View>
            )}
          </View>
          <View className='upload-box' onClick={handleChooseBack}>
            {backImage ? (
              <Image className='upload-preview' src={backImage} mode='aspectFit' />
            ) : (
              <View className='upload-placeholder'>
                <Text className='upload-plus'>+</Text>
                <Text className='upload-label'>国徽面</Text>
              </View>
            )}
          </View>
        </View>
      </View>

      <View className='submit-wrap'>
        <View
          className={`btn btn-primary btn-block submit-btn ${loading ? 'btn-disabled' : ''}`}
          onClick={loading ? undefined : handleSubmit}
        >
          <Text>{loading ? '认证中...' : '提交认证'}</Text>
        </View>
      </View>

      <View className='tips'>
        <Text className='tips-title'>温馨提示</Text>
        <Text className='tips-item'>1. 请确保填写的姓名与身份证一致</Text>
        <Text className='tips-item'>2. 请上传清晰的身份证正反面照片</Text>
        <Text className='tips-item'>3. 系统将通过 OCR 识别校验身份信息</Text>
        <Text className='tips-item'>4. 身份证信息仅用于实名认证，将加密存储</Text>
        <Text className='tips-item'>5. 认证成功后不可修改</Text>
      </View>
    </View>
  )
}
