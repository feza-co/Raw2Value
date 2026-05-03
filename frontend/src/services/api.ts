import axios from 'axios'
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from '@/utils/token'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL as string,
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config as typeof error.config & { _retry?: boolean }
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refreshToken = getRefreshToken()
      if (refreshToken) {
        try {
          const res = await axios.post(
            `${import.meta.env.VITE_API_URL as string}/api/auth/refresh`,
            { refresh_token: refreshToken },
          )
          const { access_token, refresh_token } = res.data
          setTokens(access_token, refresh_token ?? refreshToken)
          original.headers.Authorization = `Bearer ${access_token}`
          return api(original)
        } catch {
          // refresh failed — fall through to clear + redirect
        }
      }
      clearTokens()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default api
