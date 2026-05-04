import api from './api'

export const evidenceService = {
  async getModelEvidence(): Promise<Record<string, unknown>> {
    const res = await api.get<Record<string, unknown>>('/api/model-evidence')
    return res.data
  },
}
