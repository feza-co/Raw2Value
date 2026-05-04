import { useFx } from '@/hooks/useFx'
import { clsx } from 'clsx'

interface Props {
  compact?: boolean
  dark?: boolean // Deprecated, kept for API compatibility
}

export default function FxTicker({ compact }: Props) {
  const { data, isFetching } = useFx()

  const textColor = 'text-slate-400'
  const valueColor = 'text-slate-700'

  if (!data) {
    return (
      <div className={clsx('flex items-center gap-2 font-mono text-xs', textColor)}>
        <span className="animate-pulse">Kur yükleniyor…</span>
      </div>
    )
  }

  return (
    <div className={clsx('flex items-center gap-4 font-mono text-xs', compact ? '' : 'text-sm')}>
      <span className={clsx('flex items-center gap-1.5', textColor)}>
        <span
          className={clsx(
            'w-1.5 h-1.5 rounded-full',
            data.is_stale ? 'bg-amber-500' : 'bg-emerald-500',
            !isFetching && !data.is_stale && 'animate-pulse',
          )}
        />
        {data.is_stale ? 'Güncelleniyor…' : null}
      </span>
      <span>
        <span className={textColor}>$1 = </span>
        <span className={clsx('font-bold', valueColor)}>
          ₺{data.usd_try.toFixed(2)}
        </span>
      </span>
      <span>
        <span className={textColor}>€1 = </span>
        <span className={clsx('font-bold', valueColor)}>
          ₺{data.eur_try.toFixed(2)}
        </span>
      </span>
    </div>
  )
}
