import { useQuery } from '@tanstack/react-query'
import { fxService } from '@/services/fx.service'

export const useFx = () =>
  useQuery({
    queryKey: ['fx'],
    queryFn: fxService.getCurrentFx,
    refetchInterval: 60_000,
    staleTime: 55_000,
  })
