import type { RouteAlternative } from '@/types/analyze.types'
import { formatTRY } from '@/utils/formatters'

interface Props { alternatives: RouteAlternative[] }

export default function RouteAlternatives({ alternatives }: Props) {
  return (
    <div className="flex flex-col gap-3">
      {alternatives.map((alt, i) => (
        <div key={alt.route} className="flex items-center gap-4 py-4 px-4 rounded-xl border border-slate-100 relative overflow-hidden bg-slate-50">
          <div
            className="absolute left-0 top-0 bottom-0 bg-amber-500/10"
            style={{ width: `${alt.route_probability * 100}%` }}
          />
          <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center border border-slate-200 z-10 shadow-sm shrink-0">
            <span className="font-mono text-[10px] font-bold text-slate-500">{i + 1}</span>
          </div>
          <span className="font-body font-semibold text-sm text-slate-800 flex-1 z-10">{alt.route}</span>
          <span className="font-display font-bold text-lg text-slate-900 z-10">{formatTRY(alt.predicted_profit_try)}</span>
          <span className="font-mono font-bold text-xs text-amber-600 bg-white px-2 py-1 rounded border border-amber-100 z-10">
            {Math.round(alt.route_probability * 100)}%
          </span>
        </div>
      ))}
    </div>
  )
}
