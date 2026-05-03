import type { NearbyProcessor } from '@/types/processor.types'

interface Props { processor: NearbyProcessor }

export default function ProcessorCard({ processor }: Props) {
  return (
    <div className="py-4 border-b border-stone-100">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-body text-sm font-medium text-charcoal">{processor.name}</p>
          <p className="font-body text-xs text-stone-300 mt-0.5">{processor.city}, {processor.district}</p>
        </div>
        <span className="font-mono text-xs text-amber">{processor.distance_km.toFixed(0)} km</span>
      </div>
      <div className="flex flex-wrap gap-1 mt-2">
        {processor.processing_routes.map((r) => (
          <span key={r} className="font-mono text-xs px-2 py-0.5 bg-stone-50 text-stone-300">{r}</span>
        ))}
      </div>
    </div>
  )
}
