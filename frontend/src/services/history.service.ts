import api from './api'
import type { PaginatedHistory, AnalysisRecordDetail, HistoryFilters } from '@/types/history.types'

export const historyService = {
  async listHistory(params: { page: number; page_size?: number } & HistoryFilters): Promise<PaginatedHistory> {
    const res = await api.get<PaginatedHistory>('/api/history', { params })
    return res.data
  },

  async getDetail(recordId: string): Promise<AnalysisRecordDetail> {
    const res = await api.get<AnalysisRecordDetail>(`/api/history/${recordId}`)
    return res.data
  },
}
