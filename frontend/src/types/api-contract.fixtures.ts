import type { UserOut } from './auth.types'
import type { AnalysisRecordDetail, AnalysisRecordSummary } from './history.types'
import type { OrgOut } from './org.types'
import type { NearbyProcessor } from './processor.types'

export const backendUserOutFixture = {
  id: '3e3121fb-4ff6-4aa7-81f6-8eb758a15e0d',
  email: 'user@example.com',
  full_name: null,
  role: 'user',
  is_active: true,
  organization: {
    id: '645cbf71-bff7-4d4e-b0bf-433e15a6478b',
    name: 'Acme Processing',
    capabilities: {
      can_supply_raw_material: false,
      can_process_material: true,
      can_buy_material: false,
      can_export: false,
      has_storage: true,
      has_transport_capacity: false,
    },
  },
  created_at: '2026-05-03T07:00:00Z',
} satisfies UserOut

export const backendHistorySummaryFixture = {
  id: 42,
  request_id: 'req_abc123',
  created_at: '2026-05-03T07:00:00Z',
  raw_material: 'pomza',
  tonnage: 150,
  quality: 'A',
  origin_city: 'Nevsehir',
  target_country: 'DE',
  transport_mode: 'deniz',
  recommended_route: 'export_processed_DE',
  expected_profit_try: null,
  value_uplift_pct: null,
  co2_kg: null,
  confidence_overall: null,
  duration_ms: null,
} satisfies AnalysisRecordSummary

export const backendHistoryDetailFixture = {
  ...backendHistorySummaryFixture,
  payload_json: { raw_material: 'pomza' },
  response_json: { recommended_route: 'export_processed_DE' },
} satisfies AnalysisRecordDetail

export const backendProcessorFixture = {
  id: '645cbf71-bff7-4d4e-b0bf-433e15a6478b',
  name: 'Acme Processing',
  city: null,
  district: null,
  lat: 38.62,
  lon: 34.71,
  distance_km: 12.34,
  processing_routes: [],
  capacity_ton_year: null,
  certifications: [],
  unit_cost_try_per_ton: null,
  capabilities: {
    can_process_material: true,
    has_storage: true,
    has_transport_capacity: false,
  },
} satisfies NearbyProcessor

export const backendOrgFixture = {
  id: '645cbf71-bff7-4d4e-b0bf-433e15a6478b',
  name: 'Acme Processing',
  organization_type: null,
  district: null,
  city: null,
  country: 'TR',
  lat: null,
  lon: null,
  capabilities: {
    can_supply_raw_material: false,
    can_process_material: true,
    can_buy_material: false,
    can_export: false,
    has_storage: true,
    has_transport_capacity: false,
  },
  producer_profile: null,
  processor_profile: {
    processing_routes: ['pomza'],
    capacity_ton_year: null,
    certifications: [],
    unit_cost_try_per_ton: null,
  },
  buyer_profile: null,
  created_at: '2026-05-03T07:00:00Z',
} satisfies OrgOut
