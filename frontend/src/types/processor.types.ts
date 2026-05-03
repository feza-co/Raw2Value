export interface NearbyProcessor {
  id: string
  name: string
  city: string
  district: string
  lat: number
  lon: number
  distance_km: number
  processing_routes: string[]
  capacity_ton_year: number
  certifications: string[]
  unit_cost_try_per_ton: number
  capabilities: {
    can_process_material: boolean
    has_storage: boolean
    has_transport_capacity: boolean
  }
}

export interface NearbyProcessorsResponse {
  results: NearbyProcessor[]
  count: number
  radius_km: number
  method: 'haversine_bbox' | 'postgis_geography'
}

export interface ProcessorQuery {
  lat: number
  lon: number
  radius_km?: number
  material?: string
  min_capacity?: number
}
