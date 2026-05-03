import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

/** Header'da görünür canlı TCMB FX widget'ı */
export function FxStrip({ compact = false }: { compact?: boolean }) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['fx', 'current'],
    queryFn: api.fxCurrent,
    refetchInterval: 60_000,    // 1 dk'da bir güncelle
    refetchOnWindowFocus: false,
    staleTime: 30_000,
  });

  if (isLoading) {
    return <div className="fx-strip"><span className="fx-pill"><span className="fx-pill-label">FX</span><span className="fx-pill-val">…</span></span></div>;
  }
  if (isError || !data) {
    return <div className="fx-strip"><span className="fx-pill fx-stale"><span className="fx-pill-label">FX</span><span className="fx-pill-val">offline</span></span></div>;
  }

  return (
    <div className="fx-strip">
      <span className="fx-pill"><span className="fx-pill-label">USD/₺</span><span className="fx-pill-val">{data.usd_try.toFixed(2)}</span></span>
      <span className="fx-pill"><span className="fx-pill-label">EUR/₺</span><span className="fx-pill-val">{data.eur_try.toFixed(2)}</span></span>
      {!compact && (
        <span className={`fx-pill ${data.is_stale ? 'fx-stale' : ''}`}>
          <span className="fx-pill-label">{data.source.replace('_', ' ')}</span>
          <span className="fx-pill-val">{data.last_updated}</span>
        </span>
      )}
    </div>
  );
}
