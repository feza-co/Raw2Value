import { AnimatePresence, motion } from 'framer-motion'
import { useMemo } from 'react'
import { useCockpitStore } from '@/store/cockpit.store'
import { useAuth } from '@/hooks/useAuth'
import { useProcessors } from '@/hooks/useProcessors'
import ProfitDisplay from '@/components/domain/ProfitDisplay'
import ConfidenceRing from '@/components/domain/ConfidenceRing'
import Co2Gauge from '@/components/domain/Co2Gauge'
import RouteAlternatives from '@/components/domain/RouteAlternatives'
import BuyerMatchList from '@/components/domain/BuyerMatchList'
import RouteMap from '@/components/domain/RouteMap'
import ProcessorCard from '@/components/domain/ProcessorCard'
import { lookupCityCoords, COUNTRY_DEFAULT_CITY } from '@/utils/constants'

export default function ResultPanel() {
  const result = useCockpitStore((s) => s.lastResult)
  const lastPayload = useCockpitStore((s) => s.lastPayload)
  const { user } = useAuth()

  // Origin: org koordinatı varsa onu, yoksa şehir lookup
  const origin = useMemo(() => {
    const org = user?.organization
    if (org?.lat != null && org?.lon != null) {
      return { lat: org.lat, lon: org.lon, label: org.city ?? org.name }
    }
    if (lastPayload?.origin_city) {
      const c = lookupCityCoords(lastPayload.origin_city)
      if (c) return { lat: c.lat, lon: c.lon, label: lastPayload.origin_city }
    }
    return null
  }, [user, lastPayload])

  // Destination: target_city → ülke default şehri lookup
  const destination = useMemo(() => {
    if (!lastPayload) return null
    const city = lastPayload.target_city
      || COUNTRY_DEFAULT_CITY[lastPayload.target_country]
    const c = lookupCityCoords(city)
    if (!c) return null
    return { lat: c.lat, lon: c.lon, label: city }
  }, [lastPayload])

  const { data: nearby } = useProcessors({
    lat: origin?.lat,
    lon: origin?.lon,
    radius_km: 100,
    material: lastPayload?.raw_material,
    enabled: Boolean(result && origin),
  })

  const processors = nearby?.results ?? []
  const topProcessor = processors[0] ?? null

  return (
    <div className="h-full overflow-y-auto p-8 bg-slate-50">
      <AnimatePresence mode="wait">
        {!result ? (
          <motion.div
            key="empty"
            className="flex flex-col items-center justify-center h-full text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="w-20 h-20 bg-white shadow-sm border border-slate-100 rounded-full flex items-center justify-center mb-6">
              <span className="text-3xl text-slate-300 font-light">⬡</span>
            </div>
            <p className="font-display font-semibold text-slate-400 text-2xl">
              İlk analizinizi çalıştırın
            </p>
            <p className="font-body text-slate-400 text-sm mt-2">
              Sol taraftaki formu doldurarak başlayabilirsiniz
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col gap-10"
          >
            <div className="flex items-start gap-8 pb-8 border-b border-slate-200">
              <div className="flex-1 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p className="font-body text-xs font-bold text-amber-600 uppercase tracking-widest mb-3">Beklenen Kâr</p>
                <ProfitDisplay profit={result.expected_profit_try} upliftPct={result.value_uplift_pct} />
              </div>
              <div className="text-center bg-white p-6 rounded-2xl shadow-sm border border-slate-100 min-w-[140px]">
                <p className="font-body text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Güven</p>
                <ConfidenceRing value={result.confidence.overall} />
              </div>
              <div className="flex-1 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <Co2Gauge co2Kg={result.co2_kg} />
              </div>
            </div>

            <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
              <div className="flex items-center justify-between mb-5">
                <p className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest">
                  Rota Haritası
                </p>
                <p className="font-mono text-[11px] text-slate-400">
                  {origin?.label ?? '—'} → {topProcessor?.name ?? 'işleyici aranıyor'} → {destination?.label ?? '—'}
                </p>
              </div>
              <RouteMap
                origin={origin}
                destination={destination}
                processors={processors}
                selectedProcessor={topProcessor}
              />
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100">
              <div className="flex items-center justify-between mb-6">
                <p className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest">
                  Yakındaki İşleyiciler (100 km)
                </p>
                <p className="font-mono text-[11px] text-slate-400">
                  {processors.length} tesis · K3 (Haversine + bbox)
                </p>
              </div>
              {processors.length === 0 ? (
                <p className="font-body text-sm text-slate-400">
                  Bu materyal için 100 km içinde işleyici bulunamadı.
                </p>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {processors.slice(0, 4).map((p) => (
                    <ProcessorCard key={p.id} processor={p} />
                  ))}
                </div>
              )}
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100">
              <p className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest mb-6">Rota Alternatifleri</p>
              <RouteAlternatives alternatives={result.route_alternatives} />
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100">
              <p className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest mb-6">Alıcı Eşleşmeleri</p>
              <BuyerMatchList matches={result.match_results} />
            </div>

            <div className="bg-amber-50 p-8 rounded-3xl border border-amber-100">
              <p className="font-body text-xs font-bold text-amber-600/70 uppercase tracking-widest mb-4">Açıklamalar</p>
              <div className="flex flex-col gap-4">
                {result.reason_codes.map((r, i) => (
                  <div key={i} className="flex gap-3 items-start">
                    <span className="flex h-2 w-2 rounded-full bg-amber-500 mt-2 flex-shrink-0"></span>
                    <p className="font-body text-lg text-amber-900 font-medium leading-relaxed">
                      {r.text}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {result.warnings.length > 0 && (
              <div className="bg-red-50 p-6 rounded-2xl border border-red-100">
                {result.warnings.map((w, i) => (
                  <p key={i} className="font-body text-sm font-medium text-red-600 flex items-center gap-2 mb-2 last:mb-0">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                    {w}
                  </p>
                ))}
              </div>
            )}

            <div className="flex justify-between items-center border-t border-slate-200 pt-6">
              <p className="font-mono text-xs font-medium text-slate-400">
                ID: {result.request_id}
              </p>
              <p className="font-mono text-xs font-medium text-slate-400">
                {result.duration_ms}ms · v{result.model_version}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
