import { useState } from 'react'
import { useHistory } from '@/hooks/useHistory'
import HistoryRow from '@/components/domain/HistoryRow'
import HistoryDrawer from './HistoryDrawer'

export default function History() {
  const [selected, setSelected] = useState<string | null>(null)
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useHistory()

  const records = data?.pages.flatMap((p) => p.items) ?? []

  return (
    <div className="max-w-5xl mx-auto px-8 py-12">
      <p className="font-body text-xs text-stone-300 uppercase tracking-widest mb-6">Analiz Geçmişi</p>
      <h1 className="font-display font-light text-ink text-4xl mb-12">Geçmiş Analizler</h1>

      {isLoading ? (
        <p className="font-body text-sm text-stone-300 animate-pulse">Yükleniyor…</p>
      ) : records.length === 0 ? (
        <p className="font-body text-sm text-stone-300">Henüz analiz yok.</p>
      ) : (
        <>
          <div className="border-t border-stone-100">
            {records.map((r) => (
              <HistoryRow key={r.id} record={r} onClick={() => setSelected(r.id)} />
            ))}
          </div>
          {hasNextPage && (
            <button
              onClick={() => fetchNextPage()}
              disabled={isFetchingNextPage}
              className="font-body text-sm text-stone-300 hover:text-amber transition-colors duration-150 mt-8"
            >
              {isFetchingNextPage ? 'Yükleniyor…' : 'Daha fazla yükle'}
            </button>
          )}
        </>
      )}

      <HistoryDrawer recordId={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
