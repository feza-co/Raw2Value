import api from './api'
import type { RouteRequest, RouteResponse } from '@/types/route.types'

export const routeService = {
  async build(payload: RouteRequest): Promise<RouteResponse> {
    const res = await api.post<RouteResponse>('/api/route', payload)
    return res.data
  },
}
