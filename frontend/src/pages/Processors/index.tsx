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
      <div className="mb-12">
        <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-3">Yakın İşlemciler</p>
        <h1 className="font-display font-black text-slate-900 text-4xl">İşlemci Haritası</h1>
      </div>

      <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden mb-12">
        <ProcessorMap processors={processors} />
      </div>

      <div>
        <h2 className="font-display font-bold text-slate-800 text-2xl mb-6">Listelenen İşlemciler</h2>
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1,2].map(i => (
              <div key={i} className="bg-slate-100 animate-pulse h-48 rounded-3xl" />
            ))}
          </div>
        ) : processors.length === 0 ? (
          <div className="bg-white rounded-3xl p-12 text-center border border-slate-100">
            <p className="font-body text-slate-500 font-medium">Yakınınızda işlemci bulunamadı.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {processors.map((p) => <ProcessorCard key={p.id} processor={p} />)}
          </div>
        )}
      </div>
    </div>
  )
}
