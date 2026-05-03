import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { analyzeSchema, type AnalyzeFormValues } from '@/utils/validators'
import { useAnalyze } from '@/hooks/useAnalyze'
import MaterialPicker from '@/components/domain/MaterialPicker'
import { QUALITY_GRADES, TRANSPORT_MODES, TARGET_COUNTRIES, PRIORITIES } from '@/utils/constants'
import { clsx } from 'clsx'
import type { RawMaterial } from '@/types/analyze.types'

export default function AnalysisForm() {
  const [advanced, setAdvanced] = useState(false)
  const { mutate: analyze, isPending } = useAnalyze()

  const { register, handleSubmit, control, formState: { errors } } = useForm<AnalyzeFormValues>({
    resolver: zodResolver(analyzeSchema),
    defaultValues: {
      raw_material: 'pomza',
      quality: 'A',
      transport_mode: 'deniz',
      target_country: 'DE',
      priority: 'max_profit',
      input_mode: 'basic',
      fx_scenario_pct: 0,
      cost_scenario_pct: 0,
    },
  })

  const onSubmit = (values: AnalyzeFormValues) => {
    analyze({ ...values, input_mode: advanced ? 'advanced' : 'basic' })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-8 p-8 h-full overflow-y-auto">
      <div>
        <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-4">Hammadde</p>
        <Controller
          name="raw_material"
          control={control}
          render={({ field }) => (
            <MaterialPicker value={field.value as RawMaterial} onChange={field.onChange} />
          )}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">Tonaj</label>
          <input
            {...register('tonnage', { valueAsNumber: true })}
            type="number"
            min={0.1}
            max={100000}
            step={0.1}
            className="w-full border border-stone-100 bg-white px-4 py-3 font-body text-sm focus:outline-none focus:border-amber transition-colors duration-150"
            placeholder="1000"
          />
          {errors.tonnage && <p className="font-body text-xs text-danger mt-1">{errors.tonnage.message}</p>}
        </div>

        <div>
          <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">Kalite</label>
          <Controller
            name="quality"
            control={control}
            render={({ field }) => (
              <div className="flex gap-1">
                {QUALITY_GRADES.map((g) => (
                  <button
                    key={g.value}
                    type="button"
                    onClick={() => field.onChange(g.value)}
                    className={clsx(
                      'flex-1 py-3 font-body text-sm border transition-colors duration-150',
                      field.value === g.value
                        ? 'border-amber bg-amber text-white'
                        : 'border-stone-100 text-charcoal hover:border-stone-300',
                    )}
                  >
                    {g.label}
                  </button>
                ))}
              </div>
            )}
          />
        </div>
      </div>

      <div>
        <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">Çıkış Şehri</label>
        <input
          {...register('origin_city')}
          type="text"
          className="w-full border border-stone-100 bg-white px-4 py-3 font-body text-sm focus:outline-none focus:border-amber transition-colors duration-150"
          placeholder="Nevşehir"
        />
        {errors.origin_city && <p className="font-body text-xs text-danger mt-1">{errors.origin_city.message}</p>}
      </div>

      <div>
        <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">Hedef Ülke</label>
        <Controller
          name="target_country"
          control={control}
          render={({ field }) => (
            <div className="flex gap-1">
              {TARGET_COUNTRIES.map((c) => (
                <button
                  key={c.value}
                  type="button"
                  onClick={() => field.onChange(c.value)}
                  className={clsx(
                    'flex-1 py-3 font-body text-sm border transition-colors duration-150',
                    field.value === c.value
                      ? 'border-amber bg-amber text-white'
                      : 'border-stone-100 text-charcoal hover:border-stone-300',
                  )}
                >
                  {c.label}
                </button>
              ))}
            </div>
          )}
        />
      </div>

      <div>
        <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">Taşıma Modu</label>
        <Controller
          name="transport_mode"
          control={control}
          render={({ field }) => (
            <div className="grid grid-cols-2 gap-1">
              {TRANSPORT_MODES.map((m) => (
                <button
                  key={m.value}
                  type="button"
                  onClick={() => field.onChange(m.value)}
                  className={clsx(
                    'py-3 px-3 text-left font-body border transition-colors duration-150',
                    field.value === m.value
                      ? 'border-amber bg-amber/5'
                      : 'border-stone-100 hover:border-stone-300',
                  )}
                >
                  <p className="text-sm text-charcoal">{m.label}</p>
                  <p className="text-xs text-stone-300 mt-0.5">{m.co2Hint}</p>
                </button>
              ))}
            </div>
          )}
        />
      </div>

      <div>
        <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">Öncelik</label>
        <Controller
          name="priority"
          control={control}
          render={({ field }) => (
            <div className="flex gap-1">
              {PRIORITIES.map((p) => (
                <button
                  key={p.value}
                  type="button"
                  onClick={() => field.onChange(p.value)}
                  className={clsx(
                    'flex-1 py-3 font-body text-xs border transition-colors duration-150',
                    field.value === p.value
                      ? 'border-amber bg-amber text-white'
                      : 'border-stone-100 text-charcoal hover:border-stone-300',
                  )}
                >
                  {p.label}
                </button>
              ))}
            </div>
          )}
        />
      </div>

      <button
        type="button"
        onClick={() => setAdvanced((v) => !v)}
        className="font-body text-xs text-stone-300 uppercase tracking-widest text-left hover:text-amber transition-colors duration-150"
      >
        {advanced ? '− Gelişmiş' : '+ Gelişmiş'}
      </button>

      {advanced && (
        <div className="flex flex-col gap-4 border-t border-stone-100 pt-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">Nem (%)</label>
              <input
                {...register('moisture_pct', { valueAsNumber: true })}
                type="number"
                min={0}
                max={100}
                className="w-full border border-stone-100 bg-white px-4 py-3 font-body text-sm focus:outline-none focus:border-amber"
              />
            </div>
            <div>
              <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">Saflık (%)</label>
              <input
                {...register('purity_pct', { valueAsNumber: true })}
                type="number"
                min={0}
                max={100}
                className="w-full border border-stone-100 bg-white px-4 py-3 font-body text-sm focus:outline-none focus:border-amber"
              />
            </div>
          </div>
          <div>
            <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">
              Kur Senaryosu ({'{'}0{'}'}%)
            </label>
            <input
              {...register('fx_scenario_pct', { valueAsNumber: true })}
              type="range"
              min={-0.2}
              max={0.2}
              step={0.01}
              className="w-full accent-amber"
            />
          </div>
          <div>
            <label className="font-body text-xs text-stone-300 uppercase tracking-widest block mb-2">
              Maliyet Senaryosu ({'{'}0{'}'}%)
            </label>
            <input
              {...register('cost_scenario_pct', { valueAsNumber: true })}
              type="range"
              min={-0.2}
              max={0.2}
              step={0.01}
              className="w-full accent-amber"
            />
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={isPending}
        className="w-full py-5 bg-amber text-white font-body text-sm tracking-wide hover:bg-amber-dark transition-colors duration-150 disabled:opacity-50 mt-auto"
        style={{ cursor: isPending ? 'progress' : 'pointer' }}
      >
        {isPending ? 'Analiz ediliyor…' : 'Analiz Et'}
      </button>
    </form>
  )
}
