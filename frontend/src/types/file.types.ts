export interface UploadResponse {
  id: string
  url: string
  kind: string
  filename: string
  size_bytes: number
  content_type: string
  organization_id: string | null
  user_id: string
  storage_backend: string
  uploaded_at: string
}

export type FileKind = 'lab_report' | 'quality_cert'
