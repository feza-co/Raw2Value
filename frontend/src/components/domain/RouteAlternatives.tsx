import type { RouteAlternative } from '@/types/analyze.types'
import { formatTRY } from '@/utils/formatters'

interface Props { alternatives: RouteAlternative[] }

export default function RouteAlternatives({ alternatives }: Props) {
  return (
    <div className="flex flex-col gap-3">
      {alternatives.map((alt, i) => (
        <div key={alt.route} className="flex items-center gap-4 py-3 border-b border-stone-100 relative">
          <div
            className="absolute left-0 top-0 bottom-0 bg-amber/20"
            style={{ width: `${alt.route_probability * 100}%` }}
          />
          <span className="font-mono text-xs text-stone-300 w-4 z-10">{i + 1}</span>
          <span className="font-body text-sm text-charcoal flex-1 z-10">{alt.route}</span>
          <span className="font-display text-base text-ink z-10">{formatTRY(alt.predicted_profit_try)}</span>
          <span className="font-mono text-xs text-stone-300 z-10">
            {Math.round(alt.route_probability * 100)}%
          </span>
        </div>
      ))}
    </div>
  )
}
