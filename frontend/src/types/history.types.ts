export interface AnalysisRecordSummary {
  id: string
  raw_material: string
  tonnage: number
  origin_city: string
  target_country: string
  recommended_route: string
  expected_profit_try: number
  co2_kg: number
  confidence_overall: number
  created_at: string
  duration_ms: number
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
