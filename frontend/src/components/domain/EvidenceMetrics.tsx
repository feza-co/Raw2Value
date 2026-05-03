interface Props { evidence: Record<string, unknown> }

export default function EvidenceMetrics({ evidence }: Props) {
  const models = (evidence as Record<string, Record<string, Record<string, unknown>>>)?.metadata?.models ?? {}

  return (
    <div className="grid grid-cols-2 gap-12">
      <div>
        <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-6">Kâr Modeli (CatBoost)</p>
        <dl className="flex flex-col gap-4">
          {Object.entries(models?.profit ?? {}).map(([k, v]) => (
            <div key={k}>
              <dt className="font-body text-xs text-stone-300">{k}</dt>
              <dd className="font-display text-2xl text-ink">{String(v)}</dd>
            </div>
          ))}
        </dl>
      </div>
      <div>
        <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-6">Rota Modeli (CatBoost)</p>
        <dl className="flex flex-col gap-4">
          {Object.entries(models?.route ?? {}).map(([k, v]) => (
            <div key={k}>
              <dt className="font-body text-xs text-stone-300">{k}</dt>
              <dd className="font-display text-2xl text-ink">{String(v)}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  )
}
