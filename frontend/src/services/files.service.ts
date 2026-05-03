import api from './api'
import type { UploadResponse, FileKind } from '@/types/file.types'

export const filesService = {
  async upload(
    file: File,
    kind: FileKind,
    organizationId?: string,
    onProgress?: (pct: number) => void,
  ): Promise<UploadResponse> {
    const form = new FormData()
    form.append('file', file)
    form.append('kind', kind)
    if (organizationId) form.append('organization_id', organizationId)

    const res = await api.post<UploadResponse>('/api/files/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total))
      },
    })
    return res.data
  },

  async get(fileId: string): Promise<UploadResponse> {
    const res = await api.get<UploadResponse>(`/api/files/${fileId}`)
    return res.data
  },
}
