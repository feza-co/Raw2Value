import { useMutation } from '@tanstack/react-query'
import { analyzeService } from '@/services/analyze.service'

export const useWhatIf = () =>
  useMutation({ mutationFn: analyzeService.whatIf })
