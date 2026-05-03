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
      <div className="flex items-center justify-center h-64 p-8">
        <p className="font-display text-stone-300 text-xl italic">
          Önce Kokpit'ten bir analiz çalıştırın.
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
    <div className="p-8 flex flex-col gap-8">
      <p className="font-body text-xs text-stone-300 uppercase tracking-widest">What-If Simülatör</p>
      <div className="flex flex-col gap-3">
        {scenarios.map((s, i) => (
          <div key={i} className="flex items-center gap-4 border border-stone-100 p-4">
            <input
              value={s.name}
              onChange={(e) => {
                const next = [...scenarios]
                next[i] = { ...next[i], name: e.target.value }
                setScenarios(next)
              }}
              className="font-body text-sm flex-1 focus:outline-none bg-transparent"
              placeholder="Senaryo adı"
            />
            <div className="flex items-center gap-2">
              <label className="font-mono text-xs text-stone-300">Kur %</label>
              <input
                type="number"
                value={(s.fx_scenario_pct ?? 0) * 100}
                onChange={(e) => {
                  const next = [...scenarios]
                  next[i] = { ...next[i], fx_scenario_pct: Number(e.target.value) / 100 }
                  setScenarios(next)
                }}
                className="w-16 border border-stone-100 px-2 py-1 font-mono text-xs focus:outline-none focus:border-amber"
                min={-20}
                max={20}
              />
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={() => setScenarios((prev) => [...prev, { name: `Senaryo ${prev.length + 1}`, fx_scenario_pct: 0 }])}
          className="font-body text-xs text-stone-300 hover:text-amber transition-colors duration-150 text-left"
          disabled={scenarios.length >= 10}
        >
          + Senaryo Ekle
        </button>
      </div>

      <button
        type="button"
        onClick={run}
        disabled={isPending}
        className="py-4 bg-amber text-white font-body text-sm hover:bg-amber-dark transition-colors duration-150 disabled:opacity-50"
      >
        {isPending ? 'Çalışıyor…' : 'Simülasyonu Çalıştır'}
      </button>

      {data && <WhatIfChart results={data.results} />}
    </div>
  )
}
