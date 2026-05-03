export interface CapabilityFlags {
  can_supply_raw_material: boolean
  can_process_material: boolean
  can_buy_material: boolean
  can_export: boolean
  has_storage: boolean
  has_transport_capacity: boolean
}

export interface OrganizationOut {
  id: string
  name: string
  capabilities: CapabilityFlags
}

export interface UserOut {
  id: string
  email: string
  full_name: string | null
  role: string
  is_active: boolean
  organization: OrganizationOut | null
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
