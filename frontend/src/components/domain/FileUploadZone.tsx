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
        'border-2 border-dashed p-8 text-center cursor-pointer transition-colors duration-150',
        isDragActive ? 'border-amber bg-amber/5' : 'border-stone-100 hover:border-stone-300',
      )}
    >
      <input {...getInputProps()} />
      {uploading ? (
        <div>
          <p className="font-body text-sm text-stone-300 mb-2">Yükleniyor… {progress}%</p>
          <div className="h-0.5 bg-stone-100">
            <div className="h-full bg-amber transition-all duration-150" style={{ width: `${progress}%` }} />
          </div>
        </div>
      ) : (
        <p className="font-body text-sm text-stone-300">
          {isDragActive
            ? 'Dosyayı bırakın'
            : `${kind === 'lab_report' ? 'Lab raporu' : 'Kalite sertifikası'} yükleyin — PDF, JPEG, PNG (max 10MB)`}
        </p>
      )}
    </div>
  )
}
