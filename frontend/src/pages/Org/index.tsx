import { useOrgs } from '@/hooks/useOrg'

export default function Org() {
  const { data, isLoading } = useOrgs()
  const orgs = data?.items ?? []

  return (
    <div className="max-w-4xl mx-auto px-8 py-12">
      <div className="mb-12">
        <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-3">Organizasyon</p>
        <h1 className="font-display font-black text-slate-900 text-4xl">Organizasyonlarım</h1>
      </div>

      <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/50 border border-slate-100 p-8">
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <p className="font-body text-sm font-medium text-slate-400 animate-pulse">Organizasyonlar yükleniyor…</p>
          </div>
        ) : orgs.length === 0 ? (
          <div className="flex flex-col justify-center items-center py-12 text-center">
            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl text-slate-300">▣</span>
            </div>
            <p className="font-body text-lg font-medium text-slate-600">Henüz organizasyon yok</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {orgs.map((o) => (
              <div key={o.id} className="p-6 rounded-2xl bg-slate-50 border border-slate-100 hover:shadow-md hover:-translate-y-1 transition-all duration-300 group">
                <div className="w-10 h-1 bg-amber-500 rounded-full mb-4 group-hover:w-16 transition-all duration-300" />
                <h3 className="font-display font-bold text-slate-900 text-xl mb-2">{o.name}</h3>
                <p className="font-body font-medium text-slate-500">{[o.city, o.country].filter(Boolean).join(', ')}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
