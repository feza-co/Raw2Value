import { useForm, Controller, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useState } from 'react'
import { analyzeSchema, type AnalyzeFormValues } from '@/utils/validators'
import { useAnalyze } from '@/hooks/useAnalyze'
import { useAuth } from '@/hooks/useAuth'
import MaterialPicker from '@/components/domain/MaterialPicker'
import { QUALITY_GRADES, TRANSPORT_MODES, TARGET_COUNTRIES, PRIORITIES } from '@/utils/constants'
import { clsx } from 'clsx'
import type { RawMaterial } from '@/types/analyze.types'

export default function AnalysisForm() {
  const [advanced, setAdvanced] = useState(false)
  const { mutate: analyze, isPending } = useAnalyze()
  const { user } = useAuth()
  const orgCity = user?.organization?.city ?? ''

  const { register, handleSubmit, control, setValue, formState: { errors } } = useForm<AnalyzeFormValues>({
    resolver: zodResolver(analyzeSchema),
    defaultValues: {
      raw_material: 'pomza',
      tonnage: 150,
      quality: 'A',
      origin_city: orgCity,
      target_country: 'DE',
      target_city: 'Duisburg',
      transport_mode: 'kara',
      priority: 'max_profit',
      input_mode: 'basic',
      fx_scenario_pct: 0,
      cost_scenario_pct: 0,
    },
  })

  // Org bilgisi geç gelirse origin_city'yi auto-fill et (kullanıcı doldurmadıysa).
  useEffect(() => {
    if (orgCity) setValue('origin_city', orgCity, { shouldDirty: false })
  }, [orgCity, setValue])

  // Senaryo slider'larının canlı değerleri — rozet için.
  const fxPct = useWatch({ control, name: 'fx_scenario_pct' }) ?? 0
  const costPct = useWatch({ control, name: 'cost_scenario_pct' }) ?? 0
  const fmtPct = (v: number) => {
    const p = Math.round(v * 100)
    return p > 0 ? `+%${p}` : p < 0 ? `%${p}` : '%0'
  }

  const onSubmit = (values: AnalyzeFormValues) => {
    analyze({
      ...values,
      input_mode: advanced ? 'advanced' : 'basic',
      target_city: values.target_city || undefined,
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-8 p-8 h-full overflow-y-auto bg-white border-r border-slate-200 shadow-sm">
      <div className="flex flex-col gap-2">
        <h2 className="font-display font-black text-slate-900 text-2xl">Yeni Analiz</h2>
        <p className="font-body text-sm text-slate-500 font-medium">Değerleme parametrelerini belirleyin</p>
      </div>

      <div>
        <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-3">Hammadde</label>
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
          <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-3">Tonaj</label>
          <input
            {...register('tonnage', { valueAsNumber: true })}
            type="number"
            min={0.1}
            max={100000}
            step={0.1}
            className="w-full border border-slate-200 bg-slate-50 px-4 py-3.5 rounded-xl font-body text-sm focus:outline-none focus:border-amber-500 focus:ring-4 focus:ring-amber-500/10 transition-all duration-300"
            placeholder="1000"
          />
          {errors.tonnage && <p className="font-body text-xs text-red-500 font-medium mt-1">{errors.tonnage.message}</p>}
        </div>

        <div>
          <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-3">Kalite</label>
          <Controller
            name="quality"
            control={control}
            render={({ field }) => (
              <div className="flex gap-2">
                {QUALITY_GRADES.map((g) => (
                  <button
                    key={g.value}
                    type="button"
                    onClick={() => field.onChange(g.value)}
                    className={clsx(
                      'flex-1 py-3.5 font-body font-semibold text-sm rounded-xl border transition-all duration-300',
                      field.value === g.value
                        ? 'border-amber-500 bg-amber-50 text-amber-700 shadow-sm'
                        : 'border-slate-200 bg-slate-50 text-slate-600 hover:border-slate-300 hover:bg-slate-100',
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
        <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-3">Çıkış Şehri</label>
        <input
          {...register('origin_city')}
          type="text"
          className="w-full border border-slate-200 bg-slate-50 px-4 py-3.5 rounded-xl font-body text-sm focus:outline-none focus:border-amber-500 focus:ring-4 focus:ring-amber-500/10 transition-all duration-300"
          placeholder="Nevşehir"
        />
        {errors.origin_city && <p className="font-body text-xs text-red-500 font-medium mt-1">{errors.origin_city.message}</p>}
      </div>

      <div>
        <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-3">Hedef Ülke</label>
        <Controller
          name="target_country"
          control={control}
          render={({ field }) => (
            <div className="flex gap-2">
              {TARGET_COUNTRIES.map((c) => (
                <button
                  key={c.value}
                  type="button"
                  onClick={() => field.onChange(c.value)}
                  className={clsx(
                    'flex-1 py-3.5 font-body font-semibold text-sm rounded-xl border transition-all duration-300',
                    field.value === c.value
                      ? 'border-amber-500 bg-amber-50 text-amber-700 shadow-sm'
                      : 'border-slate-200 bg-slate-50 text-slate-600 hover:border-slate-300 hover:bg-slate-100',
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
        <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-3">Taşıma Modu</label>
        <Controller
          name="transport_mode"
          control={control}
          render={({ field }) => (
            <div className="grid grid-cols-1 gap-3">
              {TRANSPORT_MODES.map((m) => (
                <button
                  key={m.value}
                  type="button"
                  onClick={() => field.onChange(m.value)}
                  className={clsx(
                    'py-4 px-4 text-left rounded-xl font-body border transition-all duration-300',
                    field.value === m.value
                      ? 'border-amber-500 bg-amber-50 shadow-sm'
                      : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-slate-100',
                  )}
                >
                  <p className={clsx("text-sm font-semibold mb-1", field.value === m.value ? 'text-amber-800' : 'text-slate-800')}>{m.label}</p>
                  <p className={clsx("text-xs font-medium", field.value === m.value ? 'text-amber-600/70' : 'text-slate-500')}>{m.co2Hint}</p>
                </button>
              ))}
            </div>
          )}
        />
      </div>

      <div>
        <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-3">Öncelik</label>
        <Controller
          name="priority"
          control={control}
          render={({ field }) => (
            <div className="flex gap-2">
              {PRIORITIES.map((p) => (
                <button
                  key={p.value}
                  type="button"
                  onClick={() => field.onChange(p.value)}
                  className={clsx(
                    'flex-1 py-3.5 font-body font-semibold text-xs rounded-xl border transition-all duration-300',
                    field.value === p.value
                      ? 'border-amber-500 bg-amber-50 text-amber-700 shadow-sm'
                      : 'border-slate-200 bg-slate-50 text-slate-600 hover:border-slate-300 hover:bg-slate-100',
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
        className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest text-left hover:text-amber-600 transition-colors duration-200 flex items-center gap-2"
      >
        <span className="w-4 h-4 flex items-center justify-center rounded-full bg-slate-100 text-slate-400">{advanced ? '−' : '+'}</span>
        Gelişmiş Parametreler
      </button>

      {advanced && (
        <div className="flex flex-col gap-5 border-t border-slate-100 pt-6 animate-in slide-in-from-top-4 fade-in duration-300">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-2">Nem (%)</label>
              <input
                {...register('moisture_pct', { valueAsNumber: true })}
                type="number"
                min={0}
                max={100}
                className="w-full border border-slate-200 bg-slate-50 px-4 py-3 rounded-xl font-body text-sm focus:outline-none focus:border-amber-500"
              />
            </div>
            <div>
              <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest block mb-2">Saflık (%)</label>
              <input
                {...register('purity_pct', { valueAsNumber: true })}
                type="number"
                min={0}
                max={100}
                className="w-full border border-slate-200 bg-slate-50 px-4 py-3 rounded-xl font-body text-sm focus:outline-none focus:border-amber-500"
              />
            </div>
          </div>
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
            <div className="flex items-center justify-between mb-3">
              <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest">
                Kur Senaryosu
              </label>
              <span
                className={clsx(
                  'font-mono font-bold text-xs px-2.5 py-1 rounded-md border',
                  fxPct === 0
                    ? 'bg-white text-slate-500 border-slate-200'
                    : fxPct > 0
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : 'bg-rose-50 text-rose-700 border-rose-200',
                )}
              >
                {fmtPct(fxPct)}
              </span>
            </div>
            <input
              {...register('fx_scenario_pct', { valueAsNumber: true })}
              type="range"
              min={-0.2}
              max={0.2}
              step={0.01}
              className="w-full accent-amber-500"
            />
            <div className="flex justify-between text-xs font-medium text-slate-400 mt-2">
              <span>-%20</span>
              <span>%0</span>
              <span>+%20</span>
            </div>
            <p className="font-body text-[11px] text-slate-400 mt-2">
              USD/TRY canlı kura uygulanan göreli sapma. +%10 → kâr beklentisi
              TL bazında artar.
            </p>
          </div>
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
            <div className="flex items-center justify-between mb-3">
              <label className="font-body text-xs font-bold text-slate-500 uppercase tracking-widest">
                Maliyet Senaryosu
              </label>
              <span
                className={clsx(
                  'font-mono font-bold text-xs px-2.5 py-1 rounded-md border',
                  costPct === 0
                    ? 'bg-white text-slate-500 border-slate-200'
                    : costPct > 0
                      ? 'bg-rose-50 text-rose-700 border-rose-200'
                      : 'bg-emerald-50 text-emerald-700 border-emerald-200',
                )}
              >
                {fmtPct(costPct)}
              </span>
            </div>
            <input
              {...register('cost_scenario_pct', { valueAsNumber: true })}
              type="range"
              min={-0.2}
              max={0.2}
              step={0.01}
              className="w-full accent-amber-500"
            />
            <div className="flex justify-between text-xs font-medium text-slate-400 mt-2">
              <span>-%20</span>
              <span>%0</span>
              <span>+%20</span>
            </div>
            <p className="font-body text-[11px] text-slate-400 mt-2">
              İşleme + lojistik maliyetlerine uygulanan sapma. +%10 → birim
              maliyet artar, kâr azalır.
            </p>
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={isPending}
        className="w-full py-4 rounded-xl bg-slate-900 text-white font-body font-semibold text-lg hover:bg-slate-800 shadow-xl shadow-slate-900/20 hover:-translate-y-1 transition-all duration-300 disabled:opacity-50 disabled:hover:translate-y-0 mt-auto"
        style={{ cursor: isPending ? 'progress' : 'pointer' }}
      >
        {isPending ? 'Analiz ediliyor…' : 'Analiz Et'}
      </button>
    </form>
  )
}
