import axios from 'axios'
import Cookies from 'js-cookie'

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '/api'

const api = axios.create({
  baseURL: apiBaseUrl,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      Cookies.remove('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
