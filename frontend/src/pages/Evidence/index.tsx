import { useEvidence } from '@/hooks/useEvidence'
import EvidenceMetrics from '@/components/domain/EvidenceMetrics'

export default function Evidence() {
  const { data, isLoading } = useEvidence()

  return (
    <div className="min-h-screen bg-parchment pt-24 pb-32">
      <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24">
        <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-8">Model Şeffaflığı</p>
        <h1
          className="font-display font-light text-ink leading-tight mb-16"
          style={{ fontSize: 'clamp(2.5rem, 5vw, 5rem)' }}
        >
          Model Kanıtları
        </h1>

        {isLoading ? (
          <p className="font-body text-sm text-stone-300">Yükleniyor…</p>
        ) : data ? (
          <EvidenceMetrics evidence={data} />
        ) : (
          <p className="font-body text-sm text-danger">Veriler yüklenemedi.</p>
        )}
      </div>
    </div>
  )
}
