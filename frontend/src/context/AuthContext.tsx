import { createContext, useContext, useEffect, type ReactNode } from 'react'
import { useAuthStore } from '@/store/auth.store'
import { getAccessToken } from '@/utils/token'

const AuthContext = createContext<null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const fetchMe = useAuthStore((s) => s.fetchMe)
  const tryRefreshToken = useAuthStore((s) => s.tryRefreshToken)

  useEffect(() => {
    const token = getAccessToken()
    if (token) {
      fetchMe().catch(async () => {
        const refreshed = await tryRefreshToken()
        if (refreshed) await fetchMe()
      })
    } else {
      useAuthStore.setState({ isLoading: false })
    }
  }, [fetchMe, tryRefreshToken])

  return <AuthContext.Provider value={null}>{children}</AuthContext.Provider>
}

export const useAuthContext = () => useContext(AuthContext)
