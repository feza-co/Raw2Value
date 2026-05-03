import { AnimatePresence, motion } from 'framer-motion'
import { useCockpitStore } from '@/store/cockpit.store'
import ProfitDisplay from '@/components/domain/ProfitDisplay'
import ConfidenceRing from '@/components/domain/ConfidenceRing'
import Co2Gauge from '@/components/domain/Co2Gauge'
import RouteAlternatives from '@/components/domain/RouteAlternatives'
import BuyerMatchList from '@/components/domain/BuyerMatchList'

export default function ResultPanel() {
  const result = useCockpitStore((s) => s.lastResult)

  return (
    <div className="h-full overflow-y-auto p-8 bg-parchment">
      <AnimatePresence mode="wait">
        {!result ? (
          <motion.div
            key="empty"
            className="flex items-center justify-center h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <p className="font-display text-stone-300 text-2xl italic">
              İlk analizinizi çalıştırın →
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
            <div className="flex items-start gap-8 pb-8 border-b border-stone-100">
              <div className="flex-1">
                <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-3">Beklenen Kâr</p>
                <ProfitDisplay profit={result.expected_profit_try} upliftPct={result.value_uplift_pct} />
              </div>
              <div className="text-center">
                <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-3">Güven</p>
                <ConfidenceRing value={result.confidence.overall} />
              </div>
              <div className="flex-1">
                <Co2Gauge co2Kg={result.co2_kg} />
              </div>
            </div>

            <div>
              <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-4">Rota Alternatifleri</p>
              <RouteAlternatives alternatives={result.route_alternatives} />
            </div>

            <div>
              <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-4">Alıcı Eşleşmeleri</p>
              <BuyerMatchList matches={result.match_results} />
            </div>

            <div>
              <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-4">Açıklamalar</p>
              <div className="flex flex-col gap-3">
                {result.reason_codes.map((r, i) => (
                  <p key={i} className="font-display text-base text-charcoal italic leading-snug">
                    "{r.text}"
                  </p>
                ))}
              </div>
            </div>

            {result.warnings.length > 0 && (
              <div className="border-t border-stone-100 pt-6">
                {result.warnings.map((w, i) => (
                  <p key={i} className="font-body text-xs text-warning">{w}</p>
                ))}
              </div>
            )}

            <p className="font-mono text-xs text-stone-300">
              {result.request_id} · {result.duration_ms}ms · {result.model_version}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
