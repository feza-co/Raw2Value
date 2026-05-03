import { useOrgs } from '@/hooks/useOrg'

export default function Org() {
  const { data, isLoading } = useOrgs()
  const orgs = data?.items ?? []

  return (
    <div className="max-w-3xl mx-auto px-8 py-12">
      <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-6">Organizasyon</p>
      <h1 className="font-display font-light text-ink text-4xl mb-12">Organizasyonlarım</h1>

      {isLoading ? (
        <p className="font-body text-sm text-stone-300 animate-pulse">Yükleniyor…</p>
      ) : orgs.length === 0 ? (
        <p className="font-body text-sm text-stone-300">Henüz organizasyon yok.</p>
      ) : (
        <div className="border-t border-stone-100">
          {orgs.map((o) => (
            <div key={o.id} className="py-4 border-b border-stone-100">
              <p className="font-body text-sm text-charcoal">{o.name}</p>
              <p className="font-body text-xs text-stone-300">{o.city}, {o.country}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
