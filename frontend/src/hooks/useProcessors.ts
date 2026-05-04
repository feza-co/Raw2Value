import { useQuery } from '@tanstack/react-query'
import { processorsService } from '@/services/processors.service'
import type { ProcessorQuery } from '@/types/processor.types'
import { NEVŞEHIR_COORDS } from '@/utils/constants'

export const useProcessors = (query: Partial<ProcessorQuery> & { enabled?: boolean } = {}) => {
  const { enabled = true, ...params } = query
  const finalParams: ProcessorQuery = {
    lat: params.lat ?? NEVŞEHIR_COORDS.lat,
    lon: params.lon ?? NEVŞEHIR_COORDS.lon,
    radius_km: params.radius_km ?? 100,
    material: params.material,
    min_capacity: params.min_capacity,
  }

  return useQuery({
    queryKey: ['processors', finalParams.lat, finalParams.lon, finalParams.radius_km, finalParams.material],
    queryFn: () => processorsService.getNearby(finalParams),
    enabled,
    staleTime: 5 * 60_000,
  })
}
