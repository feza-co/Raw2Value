import { formatTRY, formatPct } from '@/utils/formatters'

interface Props {
  profit: number
  upliftPct: number
}

export default function ProfitDisplay({ profit, upliftPct }: Props) {
  return (
    <div>
      <p className="font-display font-black text-[clamp(2.5rem,4vw,3.5rem)] text-slate-900 leading-none tracking-tight">
        {formatTRY(profit)}
      </p>
      <div className="mt-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border" style={{ 
        backgroundColor: upliftPct >= 0 ? '#F0FDF4' : '#FEF2F2',
        color: upliftPct >= 0 ? '#166534' : '#991B1B',
        borderColor: upliftPct >= 0 ? '#DCFCE7' : '#FEE2E2'
      }}>
        <span className="mr-1">{upliftPct >= 0 ? '↗' : '↘'}</span>
        {formatPct(upliftPct, true)} değer artışı
      </div>
    </div>
  )
}
