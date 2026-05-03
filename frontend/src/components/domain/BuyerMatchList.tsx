import type { MatchResult } from '@/types/analyze.types'

interface Props { matches: MatchResult[] }

export default function BuyerMatchList({ matches }: Props) {
  return (
    <div className="flex flex-col gap-2">
      {matches.slice(0, 3).map((m, i) => (
        <div key={i} className="flex items-center gap-4 py-2 border-b border-stone-100">
          <span className="font-body text-sm text-charcoal flex-1">{m.buyer_name}</span>
          <span className="font-body text-xs text-stone-300">{m.processor_name}</span>
          <span className="font-mono text-xs text-amber font-medium">
            {Math.round(m.score * 100)}%
          </span>
        </div>
      ))}
    </div>
  )
}
