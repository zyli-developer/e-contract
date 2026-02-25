import { useCallback, useState } from 'react'

interface PaginationOptions<T> {
  fetchFn: (params: { pageNo: number; pageSize: number }) => Promise<{
    list: T[]
    total: number
  }>
  pageSize?: number
}

/** 通用分页 Hook */
export function usePagination<T>(options: PaginationOptions<T>) {
  const { fetchFn, pageSize = 10 } = options
  const [list, setList] = useState<T[]>([])
  const [total, setTotal] = useState(0)
  const [pageNo, setPageNo] = useState(1)
  const [loading, setLoading] = useState(false)

  const hasMore = list.length < total

  const loadData = useCallback(async (page: number, append = false) => {
    setLoading(true)
    try {
      const result = await fetchFn({ pageNo: page, pageSize })
      setList(append ? (prev) => [...prev, ...result.list] : result.list)
      setTotal(result.total)
      setPageNo(page)
    } finally {
      setLoading(false)
    }
  }, [fetchFn, pageSize])

  const refresh = useCallback(() => loadData(1, false), [loadData])
  const loadMore = useCallback(() => {
    if (hasMore && !loading) loadData(pageNo + 1, true)
  }, [hasMore, loading, pageNo, loadData])

  return { list, total, loading, hasMore, refresh, loadMore }
}
