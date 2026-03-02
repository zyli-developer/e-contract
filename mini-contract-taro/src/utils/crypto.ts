import WxmpRsa from 'wxmp-rsa'
import { request } from '@/api/request'

let _publicKey: string | null = null

/** 从后端获取 RSA 公钥（缓存） */
async function getPublicKey(): Promise<string> {
  if (_publicKey) return _publicKey
  const data = await request<{ publicKey: string }>({
    url: '/member/auth/public-key',
    isAuth: false,
  })
  _publicKey = data.publicKey
  return _publicKey
}

/** RSA 加密密码 */
export async function encryptPassword(password: string): Promise<string> {
  const publicKey = await getPublicKey()
  const rsa = new WxmpRsa()
  rsa.setPublicKey(publicKey)
  const encrypted = rsa.encryptLong(password)
  if (!encrypted) {
    throw new Error('密码加密失败')
  }
  return encrypted
}
