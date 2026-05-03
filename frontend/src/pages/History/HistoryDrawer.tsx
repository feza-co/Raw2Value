import { motion, AnimatePresence } from 'framer-motion'
import { useHistoryDetail } from '@/hooks/useHistory'
import { formatTRY, formatDate, formatCO2 } from '@/utils/formatters'

interface Props {
  recordId: string | null
  onClose: () => void
}

export default function HistoryDrawer({ recordId, onClose }: Props) {
  const { data } = useHistoryDetail(recordId ?? '')

  return (
    <AnimatePresence>
      {recordId && (
        <motion.aside
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="fixed top-14 right-0 bottom-0 w-full max-w-md bg-white border-l border-stone-100 z-50 overflow-y-auto p-8"
        >
          <button
            onClick={onClose}
            className="font-body text-xs text-stone-300 hover:text-charcoal transition-colors mb-8 block"
          >
            ← Kapat
          </button>
          {data ? (
            <div className="flex flex-col gap-6">
              <p className="font-body text-xs text-stone-300">{formatDate(data.created_at)}</p>
              <div>
                <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-1">Hammadde</p>
                <p className="font-body text-sm text-charcoal">{data.raw_material} — {data.origin_city} → {data.target_country}</p>
              </div>
              <div>
                <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-1">Kâr</p>
                <p className="font-display text-3xl text-ink">{formatTRY(data.expected_profit_try)}</p>
              </div>
              <div>
                <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-1">CO₂</p>
                <p className="font-body text-sm text-charcoal">{formatCO2(data.co2_kg)}</p>
              </div>
              <div>
                <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-1">Rota</p>
                <p className="font-body text-sm text-charcoal">{data.recommended_route}</p>
              </div>
            </div>
          ) : (
            <p className="font-body text-sm text-stone-300 animate-pulse">Yükleniyor…</p>
          )}
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
