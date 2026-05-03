import { useState } from 'react'
import { useWhatIf } from '@/hooks/useWhatIf'
import { useCockpitStore } from '@/store/cockpit.store'
import WhatIfChart from '@/components/domain/WhatIfChart'
import type { WhatIfScenario } from '@/types/analyze.types'
import { toast } from 'react-hot-toast'

export default function WhatIfPanel() {
  const lastResult = useCockpitStore((s) => s.lastResult)
  const { mutate: runWhatIf, isPending, data } = useWhatIf()
  const [scenarios, setScenarios] = useState<WhatIfScenario[]>([
    { name: 'Baz', fx_scenario_pct: 0 },
    { name: '+10% Kur', fx_scenario_pct: 0.1 },
    { name: '-10% Kur', fx_scenario_pct: -0.1 },
  ])

  if (!lastResult) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8 bg-slate-50">
        <div className="w-20 h-20 bg-white shadow-sm border border-slate-100 rounded-full flex items-center justify-center mb-6">
          <span className="text-3xl text-slate-300 font-light">⇌</span>
        </div>
        <p className="font-display font-semibold text-slate-400 text-2xl">
          Önce Kokpit'ten bir analiz çalıştırın
        </p>
        <p className="font-body text-slate-400 text-sm mt-2">
          What-If analizleri, son çalıştırılan analiz üzerinde yapılır.
        </p>
      </div>
    )
  }

  const run = () => {
    runWhatIf(
      { base_payload: lastResult as never, scenarios },
      { onError: () => toast.error('What-If analizi başarısız.') },
    )
  }

  return (
    <div className="p-8 h-full overflow-y-auto bg-slate-50">
      <div className="mb-10">
        <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-3">What-If Simülatör</p>
        <h2 className="font-display font-black text-slate-900 text-3xl">Senaryo Analizi</h2>
      </div>

      <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 mb-8">
        <div className="flex flex-col gap-4">
          {scenarios.map((s, i) => (
            <div key={i} className="flex items-center gap-6 bg-slate-50 border border-slate-100 p-4 rounded-2xl hover:border-slate-300 transition-colors duration-200">
              <div className="flex-1">
                <input
                  value={s.name}
                  onChange={(e) => {
                    const next = [...scenarios]
                    next[i] = { ...next[i], name: e.target.value }
                    setScenarios(next)
                  }}
                  className="w-full font-display font-bold text-lg text-slate-800 focus:outline-none bg-transparent placeholder-slate-300"
                  placeholder="Senaryo adı"
                />
              </div>
              <div className="w-px h-8 bg-slate-200"></div>
              <div className="flex items-center gap-3">
                <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest">Kur %</label>
                <div className="relative">
                  <input
                    type="number"
                    value={(s.fx_scenario_pct ?? 0) * 100}
                    onChange={(e) => {
                      const next = [...scenarios]
                      next[i] = { ...next[i], fx_scenario_pct: Number(e.target.value) / 100 }
                      setScenarios(next)
                    }}
                    className="w-20 border border-slate-200 px-3 py-2 rounded-lg font-mono text-sm focus:outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 bg-white"
                    min={-20}
                    max={20}
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm font-mono">%</span>
                </div>
              </div>
            </div>
          ))}
          <button
            type="button"
            onClick={() => setScenarios((prev) => [...prev, { name: `Senaryo ${prev.length + 1}`, fx_scenario_pct: 0 }])}
            className="font-body font-semibold text-sm px-6 py-3 rounded-xl border border-dashed border-slate-300 text-slate-500 hover:text-amber-600 hover:border-amber-600 hover:bg-amber-50 transition-all duration-200 text-center"
            disabled={scenarios.length >= 10}
          >
            + Yeni Senaryo Ekle
          </button>
        </div>

        <button
          type="button"
          onClick={run}
          disabled={isPending}
          className="w-full mt-8 py-4 rounded-xl bg-slate-900 text-white font-body font-semibold text-lg hover:bg-slate-800 shadow-xl shadow-slate-900/20 hover:-translate-y-1 transition-all duration-300 disabled:opacity-50 disabled:hover:translate-y-0"
        >
          {isPending ? 'Simülasyon Çalışıyor…' : 'Simülasyonu Çalıştır'}
        </button>
      </div>

      {data && (
        <div className="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <h3 className="font-display font-bold text-slate-800 text-xl mb-6">Sonuçlar</h3>
          <WhatIfChart results={data.results} />
        </div>
      )}
    </div>
  )
}
