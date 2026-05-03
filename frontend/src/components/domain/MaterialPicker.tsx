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
    <div className="grid grid-cols-3 gap-3">
      {MATERIALS.map((m) => (
        <button
          key={m.value}
          type="button"
          onClick={() => onChange(m.value)}
          className={clsx(
            'text-left p-4 border transition-all duration-150',
            value === m.value
              ? 'border-amber bg-amber/5'
              : 'border-stone-100 hover:border-stone-300',
          )}
        >
          <p className="font-body text-sm font-medium text-charcoal">{m.label}</p>
          <p className="font-body text-xs text-stone-300 mt-1 leading-snug">
            {DESCRIPTIONS[m.value]}
          </p>
        </button>
      ))}
    </div>
  )
}
