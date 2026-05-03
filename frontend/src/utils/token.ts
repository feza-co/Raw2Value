const ACCESS_KEY = 'r2v_access'
const REFRESH_KEY = 'r2v_refresh'

export const setTokens = (access: string, refresh: string) => {
  sessionStorage.setItem(ACCESS_KEY, access)
  sessionStorage.setItem(REFRESH_KEY, refresh)
}

export const getAccessToken = (): string | null =>
  sessionStorage.getItem(ACCESS_KEY)

export const getRefreshToken = (): string | null =>
  sessionStorage.getItem(REFRESH_KEY)

export const clearTokens = () => {
  sessionStorage.removeItem(ACCESS_KEY)
  sessionStorage.removeItem(REFRESH_KEY)
}
