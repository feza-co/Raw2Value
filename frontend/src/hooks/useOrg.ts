import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { orgService } from '@/services/org.service'
import type { OrgCreate, OrgUpdate } from '@/types/org.types'

export const useOrgs = () =>
  useQuery({
    queryKey: ['orgs'],
    queryFn: () => orgService.list(),
  })

export const useOrg = (orgId: string) =>
  useQuery({
    queryKey: ['orgs', orgId],
    queryFn: () => orgService.get(orgId),
    enabled: !!orgId,
  })

export const useCreateOrg = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: OrgCreate) => orgService.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['orgs'] }),
  })
}

export const useUpdateOrg = (orgId: string) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: OrgUpdate) => orgService.update(orgId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['orgs'] }),
  })
}
