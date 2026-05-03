import { useQuery } from '@tanstack/react-query'
import { routeService } from '@/services/route.service'
import type { RouteRequest } from '@/types/route.types'

export const useRoute = (payload: RouteRequest | null, enabled = true) =>
  useQuery({
    queryKey: [
      'route',
      payload?.transport_mode,
      payload?.points.map((p) => `${p.lat.toFixed(4)},${p.lon.toFixed(4)}`).join('|'),
    ],
    queryFn: () => routeService.build(payload as RouteRequest),
    enabled: enabled && Boolean(payload && payload.points.length >= 2),
    staleTime: 30 * 60_000,
  })
