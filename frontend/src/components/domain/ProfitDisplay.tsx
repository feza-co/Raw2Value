import { formatTRY, formatPct } from '@/utils/formatters'

interface Props {
  profit: number
  upliftPct: number
}

export default function ProfitDisplay({ profit, upliftPct }: Props) {
  return (
    <div>
      <p className="font-display text-[clamp(2.5rem,5vw,4rem)] text-ink leading-none tracking-tight">
        {formatTRY(profit)}
      </p>
      <p className="font-body text-sm mt-1" style={{ color: upliftPct >= 0 ? '#3D7A4E' : '#8B3A3A' }}>
        {formatPct(upliftPct, true)} değer artışı
      </p>
    </div>
  )
}
