import type { NearbyProcessor } from '@/types/processor.types'

interface Props { processors: NearbyProcessor[] }

export default function ProcessorMap({ processors }: Props) {
  return (
    <div className="bg-stone-50 border border-stone-100 flex items-center justify-center h-80">
      <p className="font-body text-sm text-stone-300">
        Harita: {processors.length} işlemci · MapLibre entegrasyonu
      </p>
    </div>
  )
}
