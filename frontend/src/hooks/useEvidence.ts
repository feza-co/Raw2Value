import { useQuery } from '@tanstack/react-query'
import { evidenceService } from '@/services/evidence.service'

export const useEvidence = () =>
  useQuery({
    queryKey: ['evidence'],
    queryFn: evidenceService.getModelEvidence,
    staleTime: Infinity,
  })
