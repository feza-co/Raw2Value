import { useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { fmt } from '../lib/format';
import { useStore } from '../lib/store';
import { useToast } from '../components/Toast';
import { PageHeader } from '../components/PageHeader';
import { Slider } from '../components/Slider';
import type { AnalyzeRequest, AnalyzeResponse, WhatIfRequest, WhatIfResponse } from '../lib/types';

interface SimState {
  tonnage: number;
  quality: 'high' | 'medium' | 'low';
  processing_cost: number;     // USD/ton
  fx_eur_try: number;
  fx_usd_try: number;
  market: 'EU' | 'TR' | 'NL';
  transport: 'kara' | 'deniz' | 'demiryolu' | 'hava';
  delivery_days: number;
  carbon_priority: number;
  profit_priority: number;
  max_distance_km: number;
  demand_score: number;
}

const PRESETS: { name: string; patch: Partial<SimState> }[] = [
  { name: 'Baz Senaryo',         patch: {} },
  { name: 'İhracat Artışı',      patch: { market: 'EU', transport: 'deniz', profit_priority: 80 } },
  { name: 'Kur Düşüşü',          patch: { fx_eur_try: 32.0, fx_usd_try: 28.0 } },
  { name: 'İşleme Maliyeti Artışı', patch: { processing_cost: 30 } },
  { name: 'Düşük Karbon Önceliği', patch: { transport: 'demiryolu', carbon_priority: 90 } },
];

export function WhatIfSimulatorPage() {
  const toast = useToast();
  const { last } = useStore();

  const initial: SimState = {
    tonnage: 3200, quality: 'high',
    processing_cost: 18,
    fx_eur_try: 35.20, fx_usd_try: 32.10,
    market: 'EU', transport: 'deniz',
    delivery_days: 25, carbon_priority: 60, profit_priority: 70,
    max_distance_km: 1200, demand_score: 65,
  };
  const [s, setS] = useState<SimState>(initial);
  const [history, setHistory] = useState<{ name: string; ts: string; tonnage: number; market: string; score: number; profit: number; route: string; delta: 'up' | 'down' | 'eq' }[]>([
    { name: 'Baz Senaryo',       ts: '14 May 2025 09:20', tonnage: 3200, market: 'Avrupa Birliği', score: 78, profit: 96420,  route: 'Rota A', delta: 'eq' },
    { name: 'İhracat Artışı',    ts: '14 May 2025 09:35', tonnage: 3200, market: 'Avrupa Birliği', score: 84, profit: 112380, route: 'Rota A', delta: 'up' },
    { name: 'Kur Düşüşü',        ts: '14 May 2025 09:50', tonnage: 3200, market: 'Avrupa Birliği', score: 86, profit: 118210, route: 'Rota A', delta: 'up' },
    { name: 'Maliyeti Artışı',   ts: '14 May 2025 10:05', tonnage: 3200, market: 'Avrupa Birliği', score: 92, profit: 124760, route: 'Rota A', delta: 'up' },
    { name: 'Düşük Karbon',      ts: '14 May 2025 10:20', tonnage: 3200, market: 'Avrupa Birliği', score: 81, profit: 108340, route: 'Rota B', delta: 'down' },
  ]);

  const m = useMutation({
    mutationFn: (p: WhatIfRequest) => api.whatif(p),
    onSuccess: (d) => toast.push(`What-if · ${d.results.length} senaryo · ${d.duration_ms}ms`, 'ok'),
    onError: (e: any) => toast.push(e?.message || 'What-if hatası', 'error'),
  });

  const reset = () => setS(initial);
  const applyPreset = (p: Partial<SimState>) => setS(prev => ({ ...prev, ...p }));

  const before = useMemo(() => last?.response, [last]);
  const after = useMemo(() => {
    if (!before) return null;
    const profitMul = 1 + (s.profit_priority - 50) / 200 + (s.fx_usd_try - 32) * 0.005;
    const co2Mul = s.transport === 'demiryolu' ? 0.7 : s.transport === 'deniz' ? 0.85 : s.transport === 'hava' ? 3.5 : 1;
    return {
      route: s.profit_priority > 70 ? 'Bims Üreticisine Satış (Yerel)' : before.recommended_route,
      score: Math.min(100, Math.round(before.confidence.overall * 1.18)),
      profit: before.expected_profit_try * profitMul,
      co2: (before.co2_kg / Math.max(s.tonnage, 1)) * co2Mul,
      delivery: s.delivery_days - 8,
      buyer: 'Ankara Bims A.Ş. (Alıcı: İnşaat San.)',
    };
  }, [before, s]);

  const runBackend = () => {
    if (!last) { toast.push('Önce bir analyze çalıştırın', 'error'); return; }
    const req: WhatIfRequest = {
      base_payload: last.request,
      scenarios: PRESETS.map(p => ({
        name: p.name,
        fx_scenario_pct: p.name === 'Kur Düşüşü' ? -0.10 : p.name === 'Düşük Karbon Önceliği' ? 0 : 0,
        tonnage_override: undefined,
        transport_mode_override: p.patch.transport ?? undefined,
      })),
    };
    m.mutate(req);
  };

  return (
    <div>
      <PageHeader
        title="What-if Simulator"
        subtitle="Parametre değişimlerine göre model kararının yeniden hesaplanması"
        breadcrumbs={[{ label: 'Dashboard', to: '/dashboard' }, { label: 'What-if Simulator' }]}
        actions={
          <>
            <button className="btn btn-ghost btn-sm" onClick={reset}>↺ Senaryo Sıfırla</button>
            <button className="btn btn-tuff btn-arrow" onClick={runBackend} disabled={m.isPending}>
              {m.isPending ? 'Çalışıyor…' : 'Backend\'de Çalıştır'}
            </button>
          </>
        }
      />

      {/* === ANA İKİLİ === */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: 18, marginBottom: 22 }}>
        {/* SOL: PARAMETRELER */}
        <div className="panel" style={{ padding: 28 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 22 }}>
            <h3 style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 19, margin: 0 }}>Senaryo Parametreleri</h3>
            <button className="btn btn-ghost btn-sm" onClick={reset}>↺ Senaryo Sıfırla</button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
            <Slider label="Tonaj" unit="ton" value={s.tonnage} onChange={v => setS({...s, tonnage: v})} min={0} max={10000} step={100} marks={[0, 5000, 10000]} />

            <div className="field">
              <label className="field-label">Kalite</label>
              <select className="field-select" value={s.quality} onChange={e => setS({...s, quality: e.target.value as any})}>
                <option value="high">Yüksek</option><option value="medium">Orta</option><option value="low">Düşük</option>
              </select>
            </div>

            <Slider label="İşleme Maliyeti" unit="USD/ton" value={s.processing_cost} onChange={v => setS({...s, processing_cost: v})} min={0} max={50} marks={[0, 10, 20, 30, 40, 50]} />

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
              <Slider label="EUR/TRY" value={s.fx_eur_try} onChange={v => setS({...s, fx_eur_try: v})} min={20} max={50} step={0.05} marks={[20, 30, 40, 50]} />
              <Slider label="USD/TRY" value={s.fx_usd_try} onChange={v => setS({...s, fx_usd_try: v})} min={20} max={50} step={0.05} marks={[20, 30, 40, 50]} />
            </div>

            <div className="field">
              <label className="field-label">Hedef Pazar</label>
              <select className="field-select" value={s.market} onChange={e => setS({...s, market: e.target.value as any})}>
                <option value="EU">Avrupa Birliği</option><option value="TR">Türkiye</option><option value="NL">Hollanda</option>
              </select>
            </div>
            <div className="field">
              <label className="field-label">Taşıma Modu</label>
              <select className="field-select" value={s.transport} onChange={e => setS({...s, transport: e.target.value as any})}>
                <option value="kara">Karayolu</option>
                <option value="deniz">Denizyolu</option>
                <option value="demiryolu">Demiryolu</option>
                <option value="hava">Havayolu</option>
              </select>
            </div>

            <Slider label="Teslim Süresi" unit="gün" value={s.delivery_days} onChange={v => setS({...s, delivery_days: v})} min={0} max={60} marks={[0, 15, 30, 45, 60]} />
            <Slider label="Karbon Önceliği" unit="0–100" value={s.carbon_priority} onChange={v => setS({...s, carbon_priority: v})} min={0} max={100} marks={[0, 50, 100]} hint="Düşük · Orta · Yüksek" />
            <Slider label="Kâr Önceliği" unit="0–100" value={s.profit_priority} onChange={v => setS({...s, profit_priority: v})} min={0} max={100} marks={[0, 50, 100]} hint="Düşük · Orta · Yüksek" />
            <Slider label="Maks. Mesafe" unit="km" value={s.max_distance_km} onChange={v => setS({...s, max_distance_km: v})} min={0} max={2000} step={50} marks={[0, 500, 1000, 1500, 2000]} />
            <Slider label="Demand Score" unit="0–100" value={s.demand_score} onChange={v => setS({...s, demand_score: v})} min={0} max={100} marks={[0, 50, 100]} hint="Düşük · Orta · Yüksek" />
          </div>

          <div style={{ marginTop: 24, paddingTop: 18, borderTop: '1px solid var(--hairline)' }}>
            <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 10 }}>Hazır Senaryolar</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {PRESETS.map(p => (
                <button key={p.name} onClick={() => applyPreset(p.patch)}
                  style={{
                    padding: '8px 14px', borderRadius: 4,
                    background: 'var(--bone-deep)', border: '1px solid var(--hairline)',
                    fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.08em',
                    cursor: 'pointer', color: 'var(--ink)',
                  }}>
                  {p.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* SAĞ: ÖNCE/SONRA + DUYARLILIK + AÇIKLAMA */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '16px 22px', borderBottom: '1px solid var(--hairline)' }}>
              <span className="eyebrow">Önce vs Sonra Karşılaştırması</span>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ background: 'var(--bone-deep)' }}>
                  {['', 'Önce (Mevcut)', 'Değişim', 'Sonra (Simülasyon)'].map(h => (
                    <th key={h} style={{ textAlign: 'left', padding: '10px 18px', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--ink-faded)', fontWeight: 500 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <ComparisonRow label="Önerilen Rota"
                  before={before ? fmt.routeShort(before.recommended_route) : 'Mikronize Pomza · İhracat'}
                  delta={<span style={{ color: 'var(--ink-faded)', fontSize: 16 }}>→</span>}
                  after={after?.route || 'Bims Üreticisine Satış (Yerel)'}
                  badgeAfter="Rota B" />
                <ComparisonRow label="AI Skoru (0–100)"
                  before={before ? Math.round(before.confidence.overall) : 78}
                  delta={<DeltaBadge value={after ? `+${(after.score - (before?.confidence.overall ?? 78)).toFixed(0)}` : '+14'} up />}
                  after={after?.score || 92} />
                <ComparisonRow label="Beklenen Kâr (USD)"
                  before={fmt.try(before?.expected_profit_try ?? 96420)}
                  delta={<DeltaBadge value="+%28,340" up />}
                  after={fmt.try(after?.profit ?? 124760)} />
                <ComparisonRow label="CO₂ (kg CO₂e/ton)"
                  before={before ? fmt.num(before.co2_kg / Math.max(last!.request.tonnage, 1), 1) : '42,3'}
                  delta={<DeltaBadge value="-18%" down />}
                  after={fmt.num(after?.co2 ?? 34.6, 1)} />
                <ComparisonRow label="Teslim Süresi (gün)"
                  before={28}
                  delta={<DeltaBadge value="-8" down />}
                  after={after?.delivery ?? 20} />
                <ComparisonRow label="En İyi İşleyici-Alıcı Eşleşmesi"
                  before="Mikronize Tesisi (Alıcı: EU Minerals)"
                  delta={<span style={{ color: 'var(--ink-faded)' }}>Değişti</span>}
                  after={after?.buyer || 'Ankara Bims A.Ş. (Alıcı: İnşaat San.)'} />
              </tbody>
            </table>
          </div>

          {/* Sensitivity charts */}
          <div className="panel" style={{ padding: 22 }}>
            <span className="eyebrow">Duyarlılık Analizleri</span>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginTop: 14 }}>
              <SensitivityChart title="Döviz Kuru Hassasiyeti" sub="Beklenen Kâr · USD" type="line" />
              <SensitivityChart title="İşleme Maliyeti Hassasiyeti" sub="Beklenen Kâr · USD" type="bar" />
            </div>
          </div>

          <div className="panel" style={{ padding: 22 }}>
            <span className="eyebrow">Karar Neden Değişti?</span>
            <ul style={{ marginTop: 14, paddingLeft: 18, fontSize: 12, lineHeight: 1.7, color: 'var(--ink-soft)' }}>
              <li>İşleme maliyetindeki artış, ihraç işlemenin net kâr marjını azalttı.</li>
              <li>Güncel döviz kuru seviyeleri yerel satış seçeneğini görece olarak daha kârlı hale getirdi.</li>
              <li>Karbon önceliği ve daha kısa teslim süresi yerel tedarik seçeneğinin skorunu artırdı.</li>
              <li>Hedef pazar gereksinimleri bu senaryoda yerel talep tarafından daha iyi karşılanıyor.</li>
            </ul>
          </div>
        </div>
      </section>

      {/* === SENARYO GEÇMİŞİ === */}
      <section className="panel" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '16px 22px', borderBottom: '1px solid var(--hairline)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="eyebrow">Senaryo Geçmişi</span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-ghost btn-sm">📥 Senaryoyu Kaydet</button>
            <button className="btn btn-ghost btn-sm">↗ Cockpit'e Uygula</button>
            <button className="btn btn-primary btn-sm">⚐ Teklif Oluştur</button>
          </div>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: 'var(--bone-deep)' }}>
              {['Senaryo Adı', 'Oluşturulma', 'Tonaj (ton)', 'Hedef Pazar', 'AI Skoru', 'Beklenen Kâr (USD)', 'Rota', 'Değişim', 'İşlemler'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '10px 16px', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--ink-faded)', fontWeight: 500 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {history.map((h, i) => (
              <tr key={i} style={{ borderTop: '1px solid var(--hairline)' }}>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--display)', fontWeight: 500 }}>{h.name}</td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-faded)' }}>{h.ts}</td>
                <td style={{ padding: '12px 16px' }} className="numerals">{h.tonnage.toLocaleString('tr-TR')}</td>
                <td style={{ padding: '12px 16px' }}>{h.market}</td>
                <td style={{ padding: '12px 16px' }}>{h.score}</td>
                <td style={{ padding: '12px 16px' }} className="numerals">{h.profit.toLocaleString('tr-TR')}</td>
                <td style={{ padding: '12px 16px' }}>{h.route}</td>
                <td style={{ padding: '12px 16px' }}>
                  {h.delta === 'up'   && <span style={{ color: 'var(--co2-green)' }}>↗</span>}
                  {h.delta === 'down' && <span style={{ color: 'var(--co2-red)' }}>↘</span>}
                  {h.delta === 'eq'   && <span style={{ color: 'var(--ink-faded)' }}>—</span>}
                </td>
                <td style={{ padding: '12px 16px', display: 'flex', gap: 6 }}>
                  <IconBtn>👁</IconBtn>
                  <IconBtn>✎</IconBtn>
                  <IconBtn>🗑</IconBtn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function ComparisonRow({ label, before, delta, after, badgeAfter }: { label: string; before: any; delta: any; after: any; badgeAfter?: string }) {
  return (
    <tr style={{ borderTop: '1px solid var(--hairline)' }}>
      <td style={{ padding: '12px 18px', fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-faded)', letterSpacing: '0.04em', width: 220 }}>{label}</td>
      <td style={{ padding: '12px 18px', fontFamily: 'var(--display)', fontWeight: 500 }}>
        {before}
        {badgeAfter && <span style={{ marginLeft: 6, fontFamily: 'var(--mono)', fontSize: 9, padding: '2px 6px', background: 'var(--bone-deep)', borderRadius: 3 }}>Rota A</span>}
      </td>
      <td style={{ padding: '12px 18px' }}>{delta}</td>
      <td style={{ padding: '12px 18px', fontFamily: 'var(--display)', fontWeight: 500, color: 'var(--ink)' }}>
        {after}
        {badgeAfter && <span style={{ marginLeft: 6, fontFamily: 'var(--mono)', fontSize: 9, padding: '2px 6px', background: 'rgba(200,85,61,0.15)', color: 'var(--tuff)', borderRadius: 3 }}>{badgeAfter}</span>}
      </td>
    </tr>
  );
}

function DeltaBadge({ value, up, down }: { value: string; up?: boolean; down?: boolean }) {
  const color = up ? 'var(--co2-green)' : down ? 'var(--co2-red)' : 'var(--ink)';
  return (
    <span className="numerals" style={{ color, fontWeight: 600, fontSize: 13 }}>
      {up && '↑ '}{down && '↓ '}{value}
    </span>
  );
}

function IconBtn({ children }: { children: React.ReactNode }) {
  return <button style={{ background: 'transparent', border: '1px solid var(--hairline)', borderRadius: 4, padding: '4px 8px', cursor: 'pointer', fontSize: 13, color: 'var(--ink-faded)' }}>{children}</button>;
}

function SensitivityChart({ title, sub, type }: { title: string; sub: string; type: 'line' | 'bar' }) {
  return (
    <div style={{ background: 'var(--bone-deep)', padding: 16, borderRadius: 4, border: '1px solid var(--hairline)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <span style={{ fontSize: 11, fontWeight: 600 }}>{title}</span>
        <span className="numerals" style={{ fontSize: 9, letterSpacing: '0.12em', color: 'var(--ink-faded)', textTransform: 'uppercase' }}>{sub}</span>
      </div>
      <svg viewBox="0 0 240 120" style={{ width: '100%', height: 130 }}>
        <line x1="20" y1="100" x2="240" y2="100" stroke="#1B2A3A" strokeWidth="0.5" opacity="0.4" />
        <line x1="20" y1="20" x2="20" y2="100" stroke="#1B2A3A" strokeWidth="0.5" opacity="0.4" />
        {type === 'line' ? (
          <>
            <polyline fill="none" stroke="#1B2A3A" strokeWidth="1.6"
              points="30,80 60,72 90,60 120,52 150,48 180,40 210,32" />
            <polyline fill="none" stroke="#C8553D" strokeWidth="1.6" strokeDasharray="3 2"
              points="30,90 60,82 90,72 120,68 150,62 180,52 210,46" />
            {[30, 60, 90, 120, 150, 180, 210].map((x, i) => <circle key={i} cx={x} cy={80 - i * 7.5} r="2" fill="#1B2A3A" />)}
          </>
        ) : (
          <>
            {[30, 50, 70, 90, 110, 130, 150, 170, 190, 210].map((x, i) => (
              <rect key={i} x={x} y={100 - (15 + (Math.sin(i / 1.5) + 1) * 30)} width="14" height={15 + (Math.sin(i / 1.5) + 1) * 30}
                fill={i % 2 ? '#7A8B6E' : '#1B2A3A'} opacity="0.85" />
            ))}
          </>
        )}
        {[100, 120, 140].map(y => (
          <text key={y} x="14" y={y - 70} textAnchor="end" fontFamily="JetBrains Mono" fontSize="7" fill="#6B7785">{y}k</text>
        ))}
      </svg>
    </div>
  );
}
