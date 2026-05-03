export interface UserOut {
  id: string
  email: string
  full_name: string | null
  role: string
  is_active: boolean
  organization: string | null
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string | null
  token_type: string
  expires_in: number
}

export interface RegisterRequest {
  email: string
  password: string
  full_name?: string
}
