export type RawMaterial = 'pomza' | 'perlit' | 'kabak_cekirdegi'
export type Quality = 'A' | 'B' | 'C' | 'unknown'
export type TransportMode = 'kara' | 'deniz' | 'demiryolu' | 'hava'
export type Priority = 'max_profit' | 'low_carbon' | 'fast_delivery'
export type TargetCountry = 'TR' | 'DE' | 'NL'

export interface AnalyzeRequest {
  raw_material: RawMaterial
  tonnage: number
  quality: Quality
  origin_city: string
  target_country: TargetCountry
  target_city?: string | null
  transport_mode: TransportMode
  priority: Priority
  input_mode: 'basic' | 'advanced'
  moisture_pct?: number | null
  purity_pct?: number | null
  particle_size_class?: string | null
  fx_scenario_pct: number
  cost_scenario_pct: number
}

export interface RouteAlternative {
  route: string
  predicted_profit_try: number
  value_uplift_pct: number
  co2_kg: number
  route_probability: number
}

export interface MatchResult {
  processor_name: string
  buyer_name: string
  score: number
  components: Record<string, number>
}

export interface ReasonCode {
  feature: string
  importance: number
  value: unknown
  text: string
}

export interface ConfidenceResult {
  data_confidence: number
  model_confidence: number
  overall: number
  warnings: string[]
}

export interface FeatureImportance {
  feature: string
  importance: number
}

export interface FxUsed {
  usd_try: number
  eur_try: number
  last_updated: string
}

export interface AnalyzeResponseOut {
  recommended_route: string
  route_alternatives: RouteAlternative[]
  expected_profit_try: number
  value_uplift_pct: number
  co2_kg: number
  co2_tonnes: number
  match_results: MatchResult[]
  reason_codes: ReasonCode[]
  confidence: ConfidenceResult
  feature_importance: FeatureImportance[]
  warnings: string[]
  request_id: string
  fx_used: FxUsed
  duration_ms: number
  model_version: string
}

export interface WhatIfScenario {
  name: string
  fx_scenario_pct?: number
  tonnage_override?: number
  transport_mode_override?: TransportMode
}

export interface WhatIfRequest {
  base_payload: AnalyzeRequest
  scenarios: WhatIfScenario[]
}

export interface WhatIfResultItem {
  scenario: string
  expected_profit_try: number
  value_uplift_pct: number
  co2_kg: number
  recommended_route: string
  confidence_overall: number
}

export interface WhatIfResponse {
  results: WhatIfResultItem[]
  base_fx: FxUsed
  duration_ms: number
}
