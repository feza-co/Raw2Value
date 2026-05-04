export interface AnalysisRecordSummary {
  id: number
  request_id: string
  raw_material: string
  tonnage: number
  quality: string
  origin_city: string
  target_country: string
  transport_mode: string
  recommended_route: string
  expected_profit_try: number | null
  value_uplift_pct: number | null
  co2_kg: number | null
  confidence_overall: number | null
  created_at: string
  duration_ms: number | null
}

export interface AnalysisRecordDetail extends AnalysisRecordSummary {
  payload_json: Record<string, unknown>
  response_json: Record<string, unknown>
}

export interface PaginatedHistory {
  items: AnalysisRecordSummary[]
  page: number
  page_size: number
  total: number
  total_pages: number
}

export interface HistoryFilters {
  material?: string
  from?: string
  to?: string
}
