import { useDropzone } from 'react-dropzone'
import { clsx } from 'clsx'
import type { FileKind } from '@/types/file.types'

interface Props {
  kind: FileKind
  onUpload: (file: File) => void
  uploading?: boolean
  progress?: number
}

export default function FileUploadZone({ kind, onUpload, uploading, progress }: Props) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': [], 'image/jpeg': [], 'image/png': [] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
    onDropAccepted: ([file]) => onUpload(file),
  })

  return (
    <div
      {...getRootProps()}
      className={clsx(
        'border-2 border-dashed p-8 rounded-2xl text-center cursor-pointer transition-all duration-300',
        isDragActive ? 'border-amber-500 bg-amber-50/50 shadow-inner' : 'border-slate-200 bg-slate-50 hover:border-amber-400 hover:bg-amber-50/30',
      )}
    >
      <input {...getInputProps()} />
      {uploading ? (
        <div>
          <p className="font-body text-sm font-semibold text-slate-500 mb-3">Yükleniyor… {progress}%</p>
          <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
            <div className="h-full bg-amber-500 transition-all duration-150" style={{ width: `${progress}%` }} />
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-3">
          <div className={clsx("w-12 h-12 rounded-full flex items-center justify-center transition-colors duration-300", isDragActive ? 'bg-amber-100' : 'bg-white shadow-sm border border-slate-100')}>
            <span className="text-xl">📁</span>
          </div>
          <p className="font-body font-medium text-sm text-slate-600">
            {isDragActive
              ? 'Dosyayı bırakın'
              : `${kind === 'lab_report' ? 'Lab raporu' : 'Kalite sertifikası'} yükleyin`}
          </p>
          <p className="font-body text-xs text-slate-400">PDF, JPEG, PNG (max 10MB)</p>
        </div>
      )}
    </div>
  )
}
