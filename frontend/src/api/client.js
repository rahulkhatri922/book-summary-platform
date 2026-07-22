import axios from 'axios'

// Empty/relative => same-origin (nginx proxies /api in production).
export const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

const api = axios.create({ baseURL: API_BASE })

// DRF TokenAuthentication expects "Authorization: Token <key>".
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})

// On 401, drop the stale token and let the app redirect to login.
api.interceptors.response.use(
  (resp) => resp,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.dispatchEvent(new Event('auth:logout'))
    }
    return Promise.reject(error)
  }
)

export default api
