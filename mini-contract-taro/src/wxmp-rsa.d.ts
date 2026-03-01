declare module 'wxmp-rsa' {
  export default class WxmpRsa {
    setPublicKey(key: string): void
    setPrivateKey(key: string): void
    encrypt(str: string): string | false
    decrypt(str: string): string | false
    encryptLong(str: string): string | false
    decryptLong(str: string): string | false
  }
}
