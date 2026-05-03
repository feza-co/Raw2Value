import api from './api'
import type { TokenResponse, UserOut, RegisterRequest } from '@/types/auth.types'

export const authService = {
  async login(email: string, password: string): Promise<TokenResponse> {
    const body = new URLSearchParams({ username: email, password })
    const res = await api.post<TokenResponse>('/api/auth/login', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return res.data
  },

  async register(payload: RegisterRequest): Promise<UserOut> {
    const res = await api.post<UserOut>('/api/auth/register', payload)
    return res.data
  },

  async me(): Promise<UserOut> {
    const res = await api.get<UserOut>('/api/auth/me')
    return res.data
  },

  async refresh(refreshToken: string): Promise<TokenResponse> {
    const res = await api.post<TokenResponse>('/api/auth/refresh', {
      refresh_token: refreshToken,
    })
    return res.data
  },
}
