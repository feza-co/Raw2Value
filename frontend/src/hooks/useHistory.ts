import { useInfiniteQuery, useQuery } from '@tanstack/react-query'
import { historyService } from '@/services/history.service'
import type { HistoryFilters } from '@/types/history.types'

export const useHistory = (filters: HistoryFilters = {}) =>
  useInfiniteQuery({
    queryKey: ['history', filters],
    queryFn: ({ pageParam = 1 }) =>
      historyService.listHistory({ page: pageParam as number, ...filters }),
    getNextPageParam: (last) =>
      last.page < last.total_pages ? last.page + 1 : undefined,
    initialPageParam: 1,
  })

export const useHistoryDetail = (recordId: number | null) =>
  useQuery({
    queryKey: ['history', 'detail', recordId],
    queryFn: () => historyService.getDetail(recordId as number),
    enabled: recordId !== null,
  })
