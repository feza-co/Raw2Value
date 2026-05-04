import { formatCO2 } from '@/utils/formatters'

interface Props { co2Kg: number }

export default function Co2Gauge({ co2Kg }: Props) {
  const max = 50000
  const pct = Math.min(co2Kg / max, 1)

  return (
    <div>
      <p className="font-body text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">CO₂ Ayak İzi</p>
      <p className="font-display font-bold text-3xl text-slate-900 mb-4">{formatCO2(co2Kg)}</p>
      <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden shadow-inner border border-slate-200/50">
        <div
          className="h-full bg-emerald-500 transition-all duration-1000 ease-out-expo relative"
          style={{ width: `${pct * 100}%` }}
        >
          <div className="absolute inset-0 bg-white/20 w-full h-full"></div>
        </div>
      </div>
    </div>
  )
}
