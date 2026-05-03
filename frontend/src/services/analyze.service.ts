import api from './api'
import type { AnalyzeRequest, AnalyzeResponseOut, WhatIfRequest, WhatIfResponse } from '@/types/analyze.types'

export const analyzeService = {
  async analyze(payload: AnalyzeRequest): Promise<AnalyzeResponseOut> {
    const res = await api.post<AnalyzeResponseOut>('/api/analyze', payload)
    return res.data
  },

  async whatIf(payload: WhatIfRequest): Promise<WhatIfResponse> {
    const res = await api.post<WhatIfResponse>('/api/what-if', payload)
    return res.data
  },
}
