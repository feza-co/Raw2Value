import type { NearbyProcessor } from '@/types/processor.types'

interface Props { processors: NearbyProcessor[] }

export default function ProcessorMap({ processors }: Props) {
  return (
    <div className="bg-slate-50 border-b border-slate-100 flex flex-col items-center justify-center h-96 relative overflow-hidden">
      <div className="absolute inset-0 opacity-[0.03] bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] mix-blend-multiply"></div>
      <div className="w-16 h-16 bg-white shadow-md rounded-2xl flex items-center justify-center mb-4 z-10">
        <span className="text-2xl text-slate-400">🗺️</span>
      </div>
      <p className="font-body font-semibold text-slate-700 z-10">
        Harita Görünümü
      </p>
      <p className="font-body text-sm text-slate-400 mt-2 z-10">
        {processors.length} işlemci konumlandırıldı · MapLibre
      </p>
    </div>
  )
}
