const storage: Record<string, any> = {}

const Taro = {
  getStorageSync: jest.fn((key: string) => storage[key] || ''),
  setStorageSync: jest.fn((key: string, value: any) => { storage[key] = value }),
  removeStorageSync: jest.fn((key: string) => { delete storage[key] }),
  showToast: jest.fn(),
  showModal: jest.fn().mockResolvedValue({ confirm: true }),
  navigateTo: jest.fn(),
  navigateBack: jest.fn(),
  switchTab: jest.fn(),
  getCurrentPages: jest.fn(() => [{}]),
  request: jest.fn(),
  useRouter: jest.fn(() => ({ params: {} })),
  downloadFile: jest.fn(),
}

export default Taro
export const useRouter = Taro.useRouter
