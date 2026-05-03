import { motion, AnimatePresence } from 'framer-motion'
import { useHistoryDetail } from '@/hooks/useHistory'
import { formatTRY, formatDate, formatCO2 } from '@/utils/formatters'

interface Props {
  recordId: number | null
  onClose: () => void
}

export default function HistoryDrawer({ recordId, onClose }: Props) {
  const { data } = useHistoryDetail(recordId)

  return (
    <AnimatePresence>
      {recordId && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-40"
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="fixed top-0 right-0 bottom-0 w-full max-w-md bg-white border-l border-slate-200 shadow-2xl z-50 overflow-y-auto"
          >
            <div className="sticky top-0 bg-white/80 backdrop-blur-md px-8 py-6 border-b border-slate-100 flex items-center justify-between z-10">
              <h2 className="font-display font-bold text-slate-900 text-xl">Analiz Detayı</h2>
              <button
                onClick={onClose}
                className="w-10 h-10 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
              >
                ✕
              </button>
            </div>
            
            <div className="p-8">
              {data ? (
                <div className="flex flex-col gap-8">
                  <div className="inline-block px-4 py-2 rounded-lg bg-slate-50 border border-slate-100 self-start">
                    <p className="font-mono text-xs font-medium text-slate-500">{formatDate(data.created_at)}</p>
                  </div>
                  
                  <div className="bg-amber-50 p-6 rounded-2xl border border-amber-100">
                    <p className="font-body text-xs font-bold text-amber-600/70 uppercase tracking-widest mb-2">Kâr</p>
                    <p className="font-display font-black text-4xl text-amber-900">{formatTRY(data.expected_profit_try)}</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                      <p className="font-body text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Hammadde</p>
                      <p className="font-body font-semibold text-slate-900 capitalize">{data.raw_material}</p>
                    </div>
                    <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                      <p className="font-body text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">CO₂</p>
                      <p className="font-body font-semibold text-slate-900">{formatCO2(data.co2_kg)}</p>
                    </div>
                  </div>

                  <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                    <p className="font-body text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Güzergah</p>
                    <div className="flex items-center gap-4">
                      <div className="flex-1">
                        <p className="font-body text-sm font-semibold text-slate-800">{data.origin_city}</p>
                      </div>
                      <div className="w-8 h-px bg-slate-300 relative">
                        <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 border-t border-r border-slate-300 rotate-45"></div>
                      </div>
                      <div className="flex-1">
                        <p className="font-body text-sm font-semibold text-slate-800">{data.target_country}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                    <p className="font-body text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Tavsiye Edilen Rota</p>
                    <p className="font-body font-medium text-slate-700 leading-relaxed">{data.recommended_route}</p>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-20 text-center gap-4">
                  <div className="w-12 h-12 border-4 border-slate-100 border-t-amber-500 rounded-full animate-spin"></div>
                  <p className="font-body text-sm font-medium text-slate-400">Detaylar yükleniyor…</p>
                </div>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}
