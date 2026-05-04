import { useState } from 'react'
import { useHistory } from '@/hooks/useHistory'
import HistoryRow from '@/components/domain/HistoryRow'
import HistoryDrawer from './HistoryDrawer'

export default function History() {
  const [selected, setSelected] = useState<number | null>(null)
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useHistory()

  const records = data?.pages.flatMap((p) => p.items) ?? []

  return (
    <div className="max-w-5xl mx-auto px-8 py-12">
      <div className="mb-12">
        <p className="font-body text-sm font-semibold text-amber-600 uppercase tracking-widest mb-3">Analiz Geçmişi</p>
        <h1 className="font-display font-black text-slate-900 text-4xl">Geçmiş Analizler</h1>
      </div>

      <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/50 border border-slate-100 p-8">
        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <p className="font-body text-sm font-medium text-slate-400 animate-pulse">Kayıtlar yükleniyor…</p>
          </div>
        ) : records.length === 0 ? (
          <div className="flex justify-center items-center py-20 text-center">
            <div>
              <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl text-slate-300">○</span>
              </div>
              <p className="font-body text-lg font-medium text-slate-600">Henüz analiz bulunmuyor</p>
              <p className="font-body text-sm text-slate-400 mt-2">Yeni bir analiz başlattığınızda burada görünecektir.</p>
            </div>
          </div>
        ) : (
          <>
            <div className="divide-y divide-slate-100">
              {records.map((r) => (
                <HistoryRow key={r.id} record={r} onClick={() => setSelected(r.id)} />
              ))}
            </div>
            {hasNextPage && (
              <div className="mt-8 text-center pt-8 border-t border-slate-100">
                <button
                  onClick={() => fetchNextPage()}
                  disabled={isFetchingNextPage}
                  className="font-body font-semibold text-sm px-6 py-3 rounded-full bg-slate-50 text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-all duration-200"
                >
                  {isFetchingNextPage ? 'Yükleniyor…' : 'Daha fazla yükle'}
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <HistoryDrawer recordId={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
