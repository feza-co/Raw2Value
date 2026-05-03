export interface CapabilityFlags {
  can_supply_raw_material?: boolean
  can_process_material?: boolean
  can_buy_material?: boolean
  can_export?: boolean
  has_storage?: boolean
  has_transport_capacity?: boolean
}

export interface OrgCreate {
  name: string
  organization_type?: string
  district?: string
  city?: string
  country?: string
  lat?: number
  lon?: number
  capabilities?: CapabilityFlags
}

export type OrgUpdate = Partial<OrgCreate>

export interface OrgOut extends OrgCreate {
  id: string
  created_at: string
}

export interface PaginatedOrgs {
  items: OrgOut[]
  page: number
  page_size: number
  total: number
  total_pages: number
}
