import { formatCO2 } from '@/utils/formatters'

interface Props { co2Kg: number }

export default function Co2Gauge({ co2Kg }: Props) {
  const max = 50000
  const pct = Math.min(co2Kg / max, 1)

  return (
    <div>
      <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-2">CO₂ Ayak İzi</p>
      <p className="font-display text-2xl text-ink">{formatCO2(co2Kg)}</p>
      <div className="mt-2 h-1 bg-stone-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-success transition-all duration-700 ease-out-expo"
          style={{ width: `${pct * 100}%` }}
        />
      </div>
    </div>
  )
}
