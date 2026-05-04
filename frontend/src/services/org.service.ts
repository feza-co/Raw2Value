import api from './api'
import type { OrgCreate, OrgUpdate, OrgOut, PaginatedOrgs } from '@/types/org.types'

export const orgService = {
  async create(payload: OrgCreate): Promise<OrgOut> {
    const res = await api.post<OrgOut>('/api/orgs', payload)
    return res.data
  },

  async list(params?: { page?: number; page_size?: number; city?: string; country?: string }): Promise<PaginatedOrgs> {
    const res = await api.get<PaginatedOrgs>('/api/orgs', { params })
    return res.data
  },

  async get(orgId: string): Promise<OrgOut> {
    const res = await api.get<OrgOut>(`/api/orgs/${orgId}`)
    return res.data
  },

  async update(orgId: string, payload: OrgUpdate): Promise<OrgOut> {
    const res = await api.patch<OrgOut>(`/api/orgs/${orgId}`, payload)
    return res.data
  },
}
