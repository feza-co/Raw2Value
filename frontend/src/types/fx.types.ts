export interface FxResponse {
  usd_try: number
  eur_try: number
  last_updated: string
  source: 'TCMB_EVDS' | 'FALLBACK'
  is_stale: boolean
  fetched_at: string
}
