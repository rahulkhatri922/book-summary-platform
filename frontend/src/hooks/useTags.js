import { useEffect, useState } from 'react'
import api from '../api/client'

/** Fetch all tags (with published-summary counts). */
export function useTags() {
  const [tags, setTags] = useState([])

  useEffect(() => {
    let active = true
    api
      .get('/tags')
      .then((r) => active && setTags(r.data))
      .catch(() => active && setTags([]))
    return () => {
      active = false
    }
  }, [])

  return tags
}
