import type { AnalysisRecordSummary } from '@/types/history.types'
import { formatTRY, formatDate } from '@/utils/formatters'

interface Props {
  record: AnalysisRecordSummary
  onClick: () => void
}

export default function HistoryRow({ record, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left flex items-center gap-6 py-4 border-b border-stone-100 hover:bg-stone-50 px-2 transition-colors duration-150 group"
    >
      <span className="font-body text-xs text-stone-300 w-36 shrink-0">{formatDate(record.created_at)}</span>
      <span className="font-body text-sm text-charcoal flex-1">{record.raw_material} — {record.origin_city}</span>
      <span className="font-body text-xs text-stone-300 hidden md:block">{record.recommended_route}</span>
      <span className="font-display text-base text-ink">{formatTRY(record.expected_profit_try)}</span>
      <span className="font-mono text-xs text-amber opacity-0 group-hover:opacity-100 transition-opacity">→</span>
    </button>
  )
}
