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
      className="w-full text-left flex items-center gap-6 py-5 px-6 hover:bg-slate-50 transition-colors duration-200 group border-l-4 border-transparent hover:border-amber-500"
    >
      <span className="font-mono text-xs font-medium text-slate-400 w-36 shrink-0">{formatDate(record.created_at)}</span>
      <span className="font-body text-sm font-semibold text-slate-800 flex-1">{record.raw_material} <span className="text-slate-400 font-normal mx-1">—</span> {record.origin_city}</span>
      <span className="font-body text-xs text-slate-500 hidden md:block w-48 truncate">{record.recommended_route}</span>
      <span className="font-display font-bold text-lg text-slate-900 group-hover:text-amber-700 transition-colors">{formatTRY(record.expected_profit_try)}</span>
      <span className="font-mono text-xs text-amber-500 opacity-0 group-hover:opacity-100 transition-opacity -translate-x-2 group-hover:translate-x-0 transform duration-200">→</span>
    </button>
  )
}
