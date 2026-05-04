export interface CapabilityFlags {
  can_supply_raw_material: boolean
  can_process_material: boolean
  can_buy_material: boolean
  can_export: boolean
  has_storage: boolean
  has_transport_capacity: boolean
}

export type CapabilityFlagsInput = Partial<CapabilityFlags>

export interface ProducerProfile {
  raw_materials: string[]
  capacity_ton_year: number | null
  quality_grades: string[]
}

export interface ProcessorProfile {
  processing_routes: string[]
  capacity_ton_year: number | null
  certifications: string[]
  unit_cost_try_per_ton: number | null
}

export interface BuyerProfile {
  product_interests: string[]
  payment_terms_days: number | null
  credit_score: number | null
}

export interface OrgCreate {
  name: string
  organization_type?: string | null
  district?: string | null
  city?: string | null
  country?: string
  lat?: number | null
  lon?: number | null
  capabilities?: CapabilityFlagsInput
  producer_profile?: ProducerProfile | null
  processor_profile?: ProcessorProfile | null
  buyer_profile?: BuyerProfile | null
}

export interface OrgUpdate {
  name?: string | null
  organization_type?: string | null
  district?: string | null
  city?: string | null
  country?: string | null
  lat?: number | null
  lon?: number | null
  capabilities?: CapabilityFlagsInput | null
}

export interface OrgOut {
  id: string
  name: string
  organization_type: string | null
  district: string | null
  city: string | null
  country: string
  lat: number | null
  lon: number | null
  capabilities: CapabilityFlags
  producer_profile: ProducerProfile | null
  processor_profile: ProcessorProfile | null
  buyer_profile: BuyerProfile | null
  created_at: string
}

export interface PaginatedOrgs {
  items: OrgOut[]
  page: number
  page_size: number
  total: number
  total_pages: number
}
