import { useState, useEffect } from 'react'
import { useProcessors } from '@/hooks/useProcessors'
import ProcessorCard from '@/components/domain/ProcessorCard'
import ProcessorMap from './ProcessorMap'
import { NEVŞEHIR_COORDS } from '@/utils/constants'

export default function Processors() {
  const [coords, setCoords] = useState(NEVŞEHIR_COORDS)

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (pos) => setCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      () => {},
    )
  }, [])

  const { data, isLoading } = useProcessors({ lat: coords.lat, lon: coords.lon })
  const processors = data?.results ?? []

  return (
    <div className="max-w-5xl mx-auto px-8 py-12">
      <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-6">Yakın İşlemciler</p>
      <h1 className="font-display font-light text-ink text-4xl mb-8">İşlemci Haritası</h1>

      <ProcessorMap processors={processors} />

      <div className="mt-8 border-t border-stone-100">
        {isLoading ? (
          <p className="font-body text-sm text-stone-300 animate-pulse mt-4">Yükleniyor…</p>
        ) : (
          processors.map((p) => <ProcessorCard key={p.id} processor={p} />)
        )}
      </div>
    </div>
  )
}
