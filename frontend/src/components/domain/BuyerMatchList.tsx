import type { MatchResult } from '@/types/analyze.types'

interface Props { matches: MatchResult[] }

export default function BuyerMatchList({ matches }: Props) {
  return (
    <div className="flex flex-col gap-3">
      {matches.slice(0, 3).map((m, i) => (
        <div key={i} className="flex items-center gap-4 py-4 px-4 bg-slate-50 rounded-xl border border-slate-100">
          <div className="flex-1">
            <span className="font-body font-bold text-sm text-slate-800 block">{m.buyer_name}</span>
            <span className="font-body text-xs font-medium text-slate-500 mt-1 block">{m.processor_name}</span>
          </div>
          <div className="flex items-center justify-center px-3 py-1.5 bg-amber-50 border border-amber-100 rounded-lg">
            <span className="font-mono text-sm text-amber-700 font-bold">
              {Math.round(m.score * 100)}%
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
