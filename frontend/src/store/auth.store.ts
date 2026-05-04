import { create } from 'zustand'
import type { UserOut } from '@/types/auth.types'
import { authService } from '@/services/auth.service'
import { setTokens, clearTokens, getRefreshToken } from '@/utils/token'

interface AuthState {
  user: UserOut | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchMe: () => Promise<void>
  tryRefreshToken: () => Promise<boolean>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  async login(email, password) {
    const tokens = await authService.login(email, password)
    setTokens(tokens.access_token, tokens.refresh_token ?? '')
    const user = await authService.me()
    set({ user, isAuthenticated: true })
  },

  logout() {
    clearTokens()
    set({ user: null, isAuthenticated: false })
  },

  async fetchMe() {
    try {
      set({ isLoading: true })
      const user = await authService.me()
      set({ user, isAuthenticated: true })
    } catch {
      set({ user: null, isAuthenticated: false })
    } finally {
      set({ isLoading: false })
    }
  },

  async tryRefreshToken() {
    const refreshToken = getRefreshToken()
    if (!refreshToken) return false
    try {
      const tokens = await authService.refresh(refreshToken)
      setTokens(tokens.access_token, tokens.refresh_token ?? refreshToken)
      return true
    } catch {
      clearTokens()
      set({ user: null, isAuthenticated: false })
      return false
    }
  },
}))
