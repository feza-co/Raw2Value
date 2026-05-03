import api from './api'
import type { FxResponse } from '@/types/fx.types'

export const fxService = {
  async getCurrentFx(): Promise<FxResponse> {
    const res = await api.get<FxResponse>('/api/fx/current')
    return res.data
  },
}
