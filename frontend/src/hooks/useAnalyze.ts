import { useMutation, useQueryClient } from '@tanstack/react-query'
import { analyzeService } from '@/services/analyze.service'
import { useCockpitStore } from '@/store/cockpit.store'

export const useAnalyze = () => {
  const queryClient = useQueryClient()
  const setLastResult = useCockpitStore((s) => s.setLastResult)

  return useMutation({
    mutationFn: analyzeService.analyze,
    onSuccess: (data) => {
      setLastResult(data)
      queryClient.invalidateQueries({ queryKey: ['history'] })
    },
  })
}
