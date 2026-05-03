import { useFx } from '@/hooks/useFx'
import { clsx } from 'clsx'

interface Props {
  compact?: boolean
  dark?: boolean
}

export default function FxTicker({ compact, dark }: Props) {
  const { data, isFetching } = useFx()

  const textColor = dark ? 'text-stone-300' : 'text-stone-300'
  const valueColor = dark ? 'text-parchment' : 'text-charcoal'

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
            data.is_stale ? 'bg-warning' : 'bg-success',
            !isFetching && !data.is_stale && 'animate-pulse',
          )}
        />
        {data.is_stale ? 'Güncelleniyor…' : null}
      </span>
      <span>
        <span className={textColor}>$1 = </span>
        <span className={clsx('font-medium', valueColor)}>
          ₺{data.usd_try.toFixed(2)}
        </span>
      </span>
      <span>
        <span className={textColor}>€1 = </span>
        <span className={clsx('font-medium', valueColor)}>
          ₺{data.eur_try.toFixed(2)}
        </span>
      </span>
    </div>
  )
}
