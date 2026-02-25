import { request } from './request'

/** 搜索模板 */
export function searchTemplates(params: Record<string, any>) {
  return request({ url: '/api/v1/seal/seal-template/search', data: params })
}

/** 模板详情 */
export function getTemplateDetail(id: string | number) {
  return request({ url: `/api/v1/seal/seal-template/get?id=${id}` })
}

/** 模板分类 */
export function getCategories() {
  return request({ url: '/api/v1/seal/seal-template/categories' })
}

/** 热门模板 */
export function getHotTemplates(limit = 6) {
  return request({ url: `/api/v1/seal/seal-template/hot?limit=${limit}` })
}

/** 常用模板 */
export function getFrequentlyUsed(limit = 8) {
  return request({ url: `/api/v1/seal/seal-template/frequently-used?limit=${limit}` })
}
