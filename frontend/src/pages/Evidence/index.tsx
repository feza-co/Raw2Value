import { useEvidence } from '@/hooks/useEvidence'
import EvidenceMetrics from '@/components/domain/EvidenceMetrics'

export default function Evidence() {
  const { data, isLoading } = useEvidence()

  return (
    <div className="min-h-screen bg-slate-50 pt-32 pb-32">
      <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24">
        <div className="mb-16">
          <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-4">Model Şeffaflığı</p>
          <h1
            className="font-display font-black text-slate-900 leading-tight drop-shadow-sm"
            style={{ fontSize: 'clamp(3rem, 5vw, 5rem)' }}
          >
            Model Kanıtları
          </h1>
        </div>

        <div className="bg-white rounded-[2.5rem] shadow-2xl shadow-slate-200/50 border border-slate-100 p-8 md:p-12">
          {isLoading ? (
            <div className="flex justify-center items-center py-32">
              <p className="font-body text-lg font-medium text-slate-400 animate-pulse">Model verileri yükleniyor…</p>
            </div>
          ) : data ? (
            <EvidenceMetrics evidence={data} />
          ) : (
            <div className="flex flex-col justify-center items-center py-32 text-center">
              <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl text-red-400">!</span>
              </div>
              <p className="font-body text-lg font-medium text-slate-600">Veriler yüklenemedi.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
