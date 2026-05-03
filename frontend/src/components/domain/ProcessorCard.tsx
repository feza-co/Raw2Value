import type { NearbyProcessor } from '@/types/processor.types'

interface Props { processor: NearbyProcessor }

export default function ProcessorCard({ processor }: Props) {
  const location = [processor.city, processor.district].filter(Boolean).join(', ') || 'Konum girilmedi'

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow duration-300">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="font-display font-bold text-lg text-slate-900">{processor.name}</p>
          <p className="font-body text-sm font-medium text-slate-500 mt-1">{location}</p>
        </div>
        <div className="bg-amber-50 px-3 py-1 rounded-full border border-amber-100">
          <span className="font-mono font-bold text-xs text-amber-700">{processor.distance_km.toFixed(0)} km</span>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {processor.processing_routes.map((r) => (
          <span key={r} className="font-body font-semibold text-xs px-3 py-1.5 rounded-lg bg-slate-50 text-slate-600 border border-slate-200">{r}</span>
        ))}
      </div>
    </div>
  )
}
