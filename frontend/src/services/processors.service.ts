import api from './api'
import type { NearbyProcessorsResponse, ProcessorQuery } from '@/types/processor.types'

export const processorsService = {
  async getNearby(query: ProcessorQuery): Promise<NearbyProcessorsResponse> {
    const res = await api.get<NearbyProcessorsResponse>('/api/processors/nearby', { params: query })
    return res.data
  },
}
