import { clsx } from 'clsx'
import { MATERIALS } from '@/utils/constants'
import type { RawMaterial } from '@/types/analyze.types'

interface Props {
  value: RawMaterial
  onChange: (v: RawMaterial) => void
}

const DESCRIPTIONS: Record<RawMaterial, string> = {
  pomza: 'Hafif, gözenekli volkanik taş',
  perlit: 'Genleşebilir volkanik cam',
  kabak_cekirdegi: 'Yüksek proteinli çekirdek',
}

export default function MaterialPicker({ value, onChange }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      {MATERIALS.map((m) => (
        <button
          key={m.value}
          type="button"
          onClick={() => onChange(m.value)}
          className={clsx(
            'text-left p-4 rounded-xl border transition-all duration-300',
            value === m.value
              ? 'border-amber-500 bg-amber-50 shadow-sm'
              : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-slate-100',
          )}
        >
          <p className={clsx("font-body text-sm font-bold mb-1", value === m.value ? 'text-amber-800' : 'text-slate-800')}>{m.label}</p>
          <p className={clsx("font-body text-xs font-medium leading-snug", value === m.value ? 'text-amber-600/70' : 'text-slate-500')}>
            {DESCRIPTIONS[m.value]}
          </p>
        </button>
      ))}
    </div>
  )
}
