interface Props { evidence: Record<string, unknown> }

export default function EvidenceMetrics({ evidence }: Props) {
  const models = (evidence as Record<string, Record<string, Record<string, unknown>>>)?.metadata?.models ?? {}

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
      <div className="bg-slate-50 p-6 md:p-8 rounded-3xl border border-slate-100 overflow-hidden">
        <p className="font-body text-xs font-bold text-amber-600 uppercase tracking-widest mb-6 md:mb-8">Kâr Modeli (CatBoost)</p>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-6 md:gap-8">
          {Object.entries(models?.profit ?? {}).map(([k, v]) => (
            <div key={k} className="flex flex-col gap-1.5 md:gap-2">
              <dt className="font-body text-xs font-semibold text-slate-400 uppercase tracking-wider break-words">{k}</dt>
              <dd className="font-display font-bold text-xl md:text-2xl text-slate-900 break-words">{String(v)}</dd>
            </div>
          ))}
        </dl>
      </div>
      <div className="bg-slate-50 p-6 md:p-8 rounded-3xl border border-slate-100 overflow-hidden">
        <p className="font-body text-xs font-bold text-amber-600 uppercase tracking-widest mb-6 md:mb-8">Rota Modeli (CatBoost)</p>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-6 md:gap-8">
          {Object.entries(models?.route ?? {}).map(([k, v]) => (
            <div key={k} className="flex flex-col gap-1.5 md:gap-2">
              <dt className="font-body text-xs font-semibold text-slate-400 uppercase tracking-wider break-words">{k}</dt>
              <dd className="font-display font-bold text-xl md:text-2xl text-slate-900 break-words">{String(v)}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  )
}
