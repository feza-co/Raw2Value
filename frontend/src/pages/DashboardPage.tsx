import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { fmt } from '../lib/format';
import { useStore } from '../lib/store';
import { useToast } from '../components/Toast';
import { PageHeader } from '../components/PageHeader';
import { KpiCard, KpiIcon } from '../components/KpiCard';
import { ProcessFlow } from '../components/ProcessFlow';
import { ConfidenceGauge } from '../components/Gauges';
import { RouteMap } from '../components/RouteMap';
import type { AnalyzeRequest } from '../lib/types';

export function DashboardPage() {
  const nav = useNavigate();
  const toast = useToast();
  const { last, setLast } = useStore();

  const ev = useQuery({ queryKey: ['evidence'], queryFn: api.modelEvidence, retry: 0 });

  const [quick, setQuick] = useState<AnalyzeRequest>({
    raw_material: 'pomza',
    tonnage: 150,
    quality: 'A',
    origin_city: 'Nevşehir',
    target_country: 'DE',
    target_city: 'Hamburg',
    transport_mode: 'kara',
    priority: 'max_profit',
    input_mode: 'basic',
    fx_scenario_pct: 0,
    cost_scenario_pct: 0,
  });

  const m = useMutation({
    mutationFn: (p: AnalyzeRequest) => api.analyze(p),
    onSuccess: (data) => {
      setLast({ request: quick, response: data, ts: Date.now() });
      toast.push(`Analiz tamam · skor ${Math.round(data.confidence.overall)}/100`, 'ok');
      nav('/cockpit');
    },
    onError: (e: any) => toast.push(e?.message || 'Analiz hatası', 'error'),
  });

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Raw2Value AI platform özet görünümü"
      />

      {/* === KPI ROW === */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18, marginBottom: 28 }}>
        <KpiCard icon={<KpiIcon.Doc />}    label="Toplam Analiz"   value="1.248" delta={{ value: '%12,5 bu ay', up: true }} delay={0.0} />
        <KpiCard icon={<KpiIcon.Bag />}    label="Aktif Teklifler" value="356"   delta={{ value: '%8,3 bu ay',  up: true }} delay={0.05} />
        <KpiCard icon={<KpiIcon.Factory/>} label="İşleyici Sayısı" value="87"    delta={{ value: '%5,1 bu ay',  up: true }} delay={0.10} />
        <KpiCard icon={<KpiIcon.Users />}  label="Alıcı Sayısı"    value="142"   delta={{ value: '%7,2 bu ay',  up: true }} delay={0.15} />
      </section>

      {/* === QUICK FORM + MAP === */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: 18, marginBottom: 28 }}>
        <div className="panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
            <span style={{ fontSize: 18 }}>⚡</span>
            <h3 style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 19, margin: 0 }}>Hızlı Analiz Başlat</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 14 }}>
            <Field label="Hammadde">
              <select className="field-select" value={quick.raw_material} onChange={e => setQuick({ ...quick, raw_material: e.target.value as any })}>
                <option value="pomza">Pomza</option>
                <option value="perlit">Perlit</option>
                <option value="kabak_cekirdegi">Kabak Çekirdeği</option>
              </select>
            </Field>
            <Field label="Lokasyon">
              <select className="field-select" value={quick.origin_city} onChange={e => setQuick({ ...quick, origin_city: e.target.value })}>
                <option>Nevşehir</option><option>İzmir</option><option>Acıgöl</option><option>Ürgüp</option><option>Kırşehir</option>
              </select>
            </Field>
            <Field label="Tonaj (ton)">
              <input className="field-input numerals" type="number" value={quick.tonnage}
                onChange={e => setQuick({ ...quick, tonnage: Number(e.target.value) })} />
            </Field>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 18 }}>
            <Field label="Kalite">
              <select className="field-select" value={quick.quality} onChange={e => setQuick({ ...quick, quality: e.target.value as any })}>
                <option value="A">A · Premium</option><option value="B">B · Standart</option><option value="C">C · Düşük</option><option value="unknown">Belirsiz</option>
              </select>
            </Field>
            <Field label="Hedef Pazar">
              <select className="field-select" value={quick.target_country}
                onChange={e => {
                  const c = e.target.value as any;
                  const def = ({ DE: 'Hamburg', NL: 'Rotterdam', TR: 'İstanbul' } as Record<string, string>)[c];
                  setQuick({ ...quick, target_country: c, target_city: def });
                }}>
                <option value="DE">Almanya · Hamburg</option><option value="NL">Hollanda · Rotterdam</option><option value="TR">Türkiye · İstanbul</option>
              </select>
            </Field>
            <Field label="Taşıma Modu">
              <select className="field-select" value={quick.transport_mode} onChange={e => setQuick({ ...quick, transport_mode: e.target.value as any })}>
                <option value="kara">Kara</option><option value="deniz">Deniz</option><option value="demiryolu">Demir Yolu</option><option value="hava">Hava</option>
              </select>
            </Field>
          </div>

          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
            <button className="btn btn-ghost" onClick={() => nav('/analyzer')}>Detaylı analiz →</button>
            <button className="btn btn-primary btn-arrow" onClick={() => m.mutate(quick)} disabled={m.isPending}>
              {m.isPending ? <><span className="atlas-loader" /><span>Çalışıyor</span></> : <span>Analizi Başlat</span>}
            </button>
          </div>
        </div>

        <div className="panel" style={{ padding: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <span className="eyebrow">Coğrafi Dağılım · Örnek</span>
            <button className="btn btn-ghost btn-sm" onClick={() => nav('/geo')}>Tam ekran ⤢</button>
          </div>
          <RouteMap
            originCity={quick.origin_city}
            targetCountry={quick.target_country}
            targetCity={quick.target_city || undefined}
            transportMode={quick.transport_mode}
            height={320}
          />
        </div>
      </section>

      {/* === SON ANALİZLER + ÖNERİ ÖZETİ + AKTİVİTE === */}
      <section style={{ display: 'grid', gridTemplateColumns: '1.4fr 0.9fr 1fr', gap: 18, marginBottom: 28 }}>
        <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '18px 22px', borderBottom: '1px solid var(--hairline)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="eyebrow">Son Analizler</span>
            <span className="numerals" style={{ fontSize: 10, color: 'var(--ink-faded)', cursor: 'pointer' }}>Tümünü Gör →</span>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ background: 'var(--bone-deep)' }}>
                {['ID', 'Hammadde', 'Lokasyon', 'Tonaj', 'Skor', 'Durum', 'Tarih'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '10px 16px', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--ink-faded)', fontWeight: 500 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {SAMPLE_ROWS.map((r, i) => (
                <tr key={r.id} style={{ borderTop: '1px solid var(--hairline)' }}>
                  <td style={{ padding: '12px 16px' }} className="numerals">{r.id}</td>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--display)', fontWeight: 500 }}>{r.material}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--ink-soft)' }}>{r.location}</td>
                  <td style={{ padding: '12px 16px' }} className="numerals">{r.tons.toLocaleString('tr-TR')}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      fontFamily: 'var(--display)', fontWeight: 600, fontSize: 13,
                      color: r.score >= 80 ? 'var(--co2-green)' : r.score >= 60 ? 'var(--co2-amber)' : 'var(--co2-red)'
                    }}>{r.score}</span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.1em', textTransform: 'uppercase',
                      padding: '3px 8px', borderRadius: 999,
                      background: r.status === 'Tamamlandı' ? 'rgba(107,142,90,0.16)' : 'rgba(198,132,66,0.16)',
                      color: r.status === 'Tamamlandı' ? 'var(--co2-green)' : 'var(--co2-amber)',
                    }}>{r.status}</span>
                  </td>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-faded)' }}>{r.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="panel" style={{ padding: 24, textAlign: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center', marginBottom: 12 }}>
            <span style={{ fontSize: 16 }}>✦</span>
            <span className="eyebrow">AI Öneri Özeti</span>
          </div>
          <ConfidenceGauge value={last?.response.confidence.overall ?? 78} size={150} label="Genel Skor" />
          <div style={{ marginTop: 18, display: 'grid', gridTemplateColumns: '1fr', gap: 10, textAlign: 'left' }}>
            <Mini label="En Uygun Pazar" value={last ? fmt.countryName(last.request.target_country) : 'Avrupa Birliği'} />
            <Mini label="Önerilen Taşıma" value={last ? fmt.transportLabel(last.request.transport_mode) : 'Denizyolu'} />
            <Mini label="Tahmini Karbon" value={last ? `${fmt.num(last.response.co2_kg / Math.max(last.request.tonnage, 1), 0)} kg/ton` : '42 kg/ton'} />
            <Mini label="Tahmini Marj" value={last ? fmt.pct(last.response.value_uplift_pct, 0) : '+18%'} highlight />
          </div>
          <button className="btn btn-primary btn-arrow" style={{ marginTop: 16, width: '100%' }} onClick={() => nav('/cockpit')}>
            Detaylı Önerilere Git
          </button>
        </div>

        <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '18px 22px', borderBottom: '1px solid var(--hairline)' }}>
            <span className="eyebrow">Son Aktiviteler</span>
          </div>
          <div style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
            {ACTIVITIES.map((a, i) => (
              <motion.div key={i}
                initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                style={{ display: 'grid', gridTemplateColumns: 'auto 1fr auto', gap: 12, alignItems: 'flex-start' }}
              >
                <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--bone-deep)', display: 'grid', placeItems: 'center', flexShrink: 0, color: 'var(--ink-soft)', fontSize: 12 }}>
                  {a.icon}
                </div>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 500 }}>{a.title}</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.06em', color: 'var(--ink-faded)', marginTop: 2 }}>{a.actor}</div>
                </div>
                <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.1em', color: 'var(--ink-faded)', whiteSpace: 'nowrap' }}>{a.time}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* === PLATFORM AKIŞI === */}
      <section className="panel" style={{ padding: '24px 0' }}>
        <div style={{ padding: '0 28px 18px', borderBottom: '1px solid var(--hairline)', marginBottom: 4 }}>
          <h3 style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 19, margin: 0 }}>Platform Akışı</h3>
          <div style={{ fontSize: 11, color: 'var(--ink-faded)', marginTop: 4, fontFamily: 'var(--mono)', letterSpacing: '0.04em' }}>
            Uçtan uca süreç adımları 6 aşamada
          </div>
        </div>
        <ProcessFlow steps={[
          { num: '1', title: 'Hammadde Girişi',  desc: 'Hammadde türü, lokasyon, tonaj ve kalite bilgileri girilir.' },
          { num: '2', title: 'Veri Toplama',     desc: 'İç ve dış kaynaklardan veriler toplanır ve normalize edilir.' },
          { num: '3', title: 'Model Skorlama',   desc: 'AI modelleri ile teknik, ekonomik ve çevresel skorlar hesaplanır.' },
          { num: '4', title: 'Karar Paneli',     desc: 'Karar alternatifleri ve öneriler karar panelinde sunulur.' },
          { num: '5', title: 'Teklif Oluşturma', desc: 'Seçilen senaryoya göre teklifler oluşturulur ve paylaşılır.' },
          { num: '6', title: 'Pasaport / Çıktı', desc: 'Raw Material Passport oluşturulur ve çıktıları ihraç edilir.' },
        ]} />
      </section>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="field">
      <label className="field-label">{label}</label>
      {children}
    </div>
  );
}

function Mini({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '6px 0', borderBottom: '1px dashed var(--hairline)' }}>
      <span className="numerals" style={{ fontSize: 9, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>{label}</span>
      <span style={{
        fontFamily: 'var(--display)', fontWeight: 500, fontSize: 14,
        color: highlight ? 'var(--tuff)' : 'var(--ink)',
        fontStyle: highlight ? 'italic' : 'normal',
      }}>{value}</span>
    </div>
  );
}

const SAMPLE_ROWS = [
  { id: 'ANL-1248', material: 'Bakır Cevheri',     location: 'Erzincan, TR', tons: 5000,  score: 82, status: 'Tamamlandı', date: '14 May 2025' },
  { id: 'ANL-1247', material: 'Alüminyum Cevheri', location: 'Giresun, TR',  tons: 3200,  score: 76, status: 'Tamamlandı', date: '13 May 2025' },
  { id: 'ANL-1246', material: 'Demir Cevheri',     location: 'Sivas, TR',    tons: 10000, score: 69, status: 'İşleniyor',  date: '12 May 2025' },
  { id: 'ANL-1245', material: 'Krom Cevheri',      location: 'Elazığ, TR',   tons: 2500,  score: 71, status: 'Tamamlandı', date: '11 May 2025' },
  { id: 'ANL-1244', material: 'Nikel Cevheri',     location: 'Şırnak, TR',   tons: 1800,  score: 64, status: 'İşleniyor',  date: '10 May 2025' },
];

const ACTIVITIES = [
  { icon: '✓', title: 'ANL-1248 analizi tamamlandı.',     actor: 'Ahmet Y. tarafından', time: '14 May · 10:32' },
  { icon: '◇', title: 'Yeni teklif oluşturuldu. (OFF-3567)', actor: 'Sistem',              time: '14 May · 09:15' },
  { icon: '◎', title: 'Pasaport oluşturuldu. (RMP-2231)',  actor: 'Sistem',              time: '13 May · 17:42' },
  { icon: '↻', title: 'Veri seti güncellendi. (MTA)',      actor: 'Sistem',              time: '13 May · 15:10' },
  { icon: '✓', title: 'ANL-1247 analizi tamamlandı.',     actor: 'Ahmet Y. tarafından', time: '13 May · 11:05' },
];
