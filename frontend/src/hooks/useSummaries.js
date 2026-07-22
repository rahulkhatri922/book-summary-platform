import { useCallback, useEffect, useState } from 'react'
import api from '../api/client'

/**
 * Fetch the paginated summaries list. Re-fetches whenever the params change.
 */
export function useSummaries({ search = '', tag = '', page = 1, mine = false } = {}) {
  const [data, setData] = useState({ results: [], count: 0, next: null, previous: null })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = useCallback(() => {
    setLoading(true)
    const params = { page }
    if (search) params.search = search
    if (tag) params.tag = tag
    if (mine) params.mine = 'true'
    return api
      .get('/summaries', { params })
      .then((r) => {
        setData(r.data)
        setError('')
      })
      .catch((e) => setError(e.response?.data?.detail || 'Failed to load summaries'))
      .finally(() => setLoading(false))
  }, [search, tag, page, mine])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { ...data, loading, error, refetch: fetchData }
}
