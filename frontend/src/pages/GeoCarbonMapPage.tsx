import { useState } from 'react';
import { motion } from 'framer-motion';
import { useStore } from '../lib/store';
import { fmt } from '../lib/format';
import { PageHeader } from '../components/PageHeader';
import { KpiCard, KpiIcon } from '../components/KpiCard';

type Tab = 'rota' | 'karbon' | 'isleyiciler' | 'alici';

export function GeoCarbonMapPage() {
  const { last } = useStore();
  const [tab, setTab] = useState<Tab>('rota');
  const [filters, setFilters] = useState({
    raw_material: '', tonnage: 250, max_radius: 250, processor_type: '', buyer_region: '', transport_mode: '', carbon_threshold: 0.15,
  });

  const totalKm = 4352;
  const totalCo2 = 812.4;

  return (
    <div>
      <PageHeader
        title="GeoCarbon Map"
        subtitle="Üretici, işleyici ve alıcı rotalarının coğrafi ve karbon analizi"
        breadcrumbs={[{ label: 'Dashboard', to: '/dashboard' }, { label: 'GeoCarbon Map' }]}
      />

      {/* === KPI === */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18, marginBottom: 22 }}>
        <KpiCard icon={<KpiIcon.Pin />}    label="Toplam Rota Mesafesi" value={`${fmt.num(totalKm)} km`} foot="Tüm uygun rotalar" />
        <KpiCard icon={<KpiIcon.Cloud />}  label="Toplam CO₂ (Tahmini)" value={`${fmt.num(totalCo2, 1)} tCO₂e`} foot="Tüm rotalar toplam" />
        <KpiCard icon={<KpiIcon.Pin />}    label="En Yakın İşleyici"    value="Kayseri" foot="112 km" />
        <KpiCard icon={<KpiIcon.Users />}  label="Uygun İşleyici Sayısı" value="8" foot="≤ 250 km içinde" highlight />
      </section>

      {/* === MAP + FILTERS === */}
      <section style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 18, marginBottom: 22 }}>
        <div className="panel" style={{ padding: 22 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 18 }}>
            <span className="eyebrow">Filtreler</span>
            <button style={{ background: 'transparent', border: 'none', cursor: 'pointer', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.16em', color: 'var(--ink-faded)', textTransform: 'uppercase' }}>Temizle</button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <Field label="Hammadde">
              <select className="field-select" value={filters.raw_material} onChange={e => setFilters({...filters, raw_material: e.target.value})}>
                <option value="">Seçiniz</option>
                <option value="pomza">Pomza</option><option value="perlit">Perlit</option><option value="kabak_cekirdegi">Kabak Çekirdeği</option>
              </select>
            </Field>
            <Field label="Tonaj (ton)">
              <input className="field-input numerals" type="number" value={filters.tonnage} onChange={e => setFilters({...filters, tonnage: Number(e.target.value)})} />
            </Field>
            <Field label="Maks. Mesafe Radyusu">
              <select className="field-select" value={filters.max_radius} onChange={e => setFilters({...filters, max_radius: Number(e.target.value)})}>
                <option value={100}>100 km</option><option value={250}>250 km</option><option value={500}>500 km</option><option value={1000}>1.000 km</option>
              </select>
            </Field>
            <Field label="İşleyici Türü">
              <select className="field-select" value={filters.processor_type} onChange={e => setFilters({...filters, processor_type: e.target.value})}>
                <option value="">Seçiniz</option>
                <option>Mikronizasyon</option><option>Filtrasyon</option><option>Bims Üretim</option>
              </select>
            </Field>
            <Field label="Alıcı Bölge">
              <select className="field-select" value={filters.buyer_region} onChange={e => setFilters({...filters, buyer_region: e.target.value})}>
                <option value="">Seçiniz</option>
                <option>Avrupa Birliği</option><option>İç Anadolu</option><option>Batı Türkiye</option>
              </select>
            </Field>
            <Field label="Taşıma Modu">
              <select className="field-select" value={filters.transport_mode} onChange={e => setFilters({...filters, transport_mode: e.target.value})}>
                <option value="">Seçiniz</option>
                <option value="kara">Kara</option><option value="deniz">Deniz</option><option value="demiryolu">Demir Yolu</option><option value="hava">Hava</option>
              </select>
            </Field>
            <Field label="Karbon Eşiği (tCO₂e/ton)">
              <input className="field-input numerals" type="number" step="0.01" value={filters.carbon_threshold} onChange={e => setFilters({...filters, carbon_threshold: Number(e.target.value)})} />
            </Field>
          </div>
          <button className="btn btn-primary btn-arrow" style={{ width: '100%', marginTop: 22, justifyContent: 'center' }}>↗ Uygula</button>
        </div>

        <div className="panel" style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '12px 18px', borderBottom: '1px solid var(--hairline)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: 8 }}>
              <span className="chip active" style={{ padding: '6px 14px' }}>Harita</span>
              <span className="chip" style={{ padding: '6px 14px' }}>Uydu</span>
            </div>
            <div style={{ display: 'flex', gap: 14, alignItems: 'center', fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-faded)' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input type="checkbox" defaultChecked /> <span>Rota Etiketlerini Göster</span>
              </label>
              <span className="chip" style={{ padding: '6px 12px' }}>≡ Katmanlar ▾</span>
            </div>
          </div>

          <div style={{ flex: 1, position: 'relative', minHeight: 480, background: 'linear-gradient(180deg, #F0EBDD 0%, #E5DFCE 100%)', overflow: 'hidden' }}>
            <BigMap last={last} />
          </div>
        </div>
      </section>

      {/* === DETAIL TABS === */}
      <section className="panel" style={{ marginBottom: 22, overflow: 'hidden' }}>
        <div style={{ display: 'flex', borderBottom: '1px solid var(--hairline)' }}>
          {([
            ['rota', 'Rota Özeti'],
            ['karbon', 'Karbon Hesabı'],
            ['isleyiciler', 'Yakındaki İşleyiciler'],
            ['alici', 'Alıcı Kümeleri'],
          ] as [Tab, string][]).map(([k, label]) => (
            <button key={k} onClick={() => setTab(k)}
              style={{
                background: 'transparent', border: 'none', cursor: 'pointer',
                padding: '14px 22px', fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase',
                color: tab === k ? 'var(--ink)' : 'var(--ink-faded)',
                borderBottom: tab === k ? '2px solid var(--tuff)' : '2px solid transparent',
                marginBottom: -1, fontWeight: tab === k ? 600 : 500,
              }}>
              {label}
            </button>
          ))}
        </div>
        <div style={{ padding: 28 }}>
          {tab === 'rota' && <RotaOzet />}
          {tab === 'karbon' && <KarbonHesabi />}
          {tab === 'isleyiciler' && <YakinIsleyiciler />}
          {tab === 'alici' && <AliciKumeleri />}
        </div>
      </section>

      {/* === COMPARISON TABLE === */}
      <section className="panel" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '18px 22px', borderBottom: '1px solid var(--hairline)' }}>
          <span className="eyebrow">Rota Karşılaştırma · A vs B vs C</span>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: 'var(--bone-deep)' }}>
              {['Rota', 'Rota Türü', 'Mesafe (km)', 'CO₂ (tCO₂e)', 'CO₂ (tCO₂e/ton)', 'Tahmini Süre', 'Maliyet İndeksi', 'Uygunluk (Kural 1)', 'Uygunluk (Kural 3)', 'İşlem'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '12px 16px', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--ink-faded)', fontWeight: 500 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROUTES.map((r, i) => (
              <tr key={r.code} style={{ borderTop: '1px solid var(--hairline)' }}>
                <td style={{ padding: '14px 16px', fontFamily: 'var(--display)', fontWeight: 500 }}>{r.label}</td>
                <td style={{ padding: '14px 16px' }}>{r.type}</td>
                <td style={{ padding: '14px 16px' }} className="numerals">{r.km.toLocaleString('tr-TR')}</td>
                <td style={{ padding: '14px 16px' }} className="numerals">{r.co2}</td>
                <td style={{ padding: '14px 16px' }} className="numerals">{r.co2pt}</td>
                <td style={{ padding: '14px 16px' }}>{r.duration}</td>
                <td style={{ padding: '14px 16px', fontFamily: 'var(--mono)' }}>{r.cost}</td>
                <td style={{ padding: '14px 16px' }}>
                  <Pill ok={r.k1}>{r.k1 ? 'Uygun (Kural 1)' : 'Uygun Değil'}</Pill>
                </td>
                <td style={{ padding: '14px 16px' }}>
                  <Pill ok={r.k3}>{r.k3 ? 'Uygun (Kural 3)' : 'Uygun Değil'}</Pill>
                </td>
                <td style={{ padding: '14px 16px' }}>
                  <button className="btn btn-ghost btn-sm">Seç</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="field"><label className="field-label">{label}</label>{children}</div>;
}

function Pill({ ok, children }: { ok: boolean; children: React.ReactNode }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.06em',
      padding: '4px 10px', borderRadius: 999,
      background: ok ? 'rgba(107,142,90,0.16)' : 'rgba(168,57,46,0.16)',
      color: ok ? 'var(--co2-green)' : 'var(--co2-red)',
    }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor' }} />
      {children}
    </span>
  );
}

const ROUTES = [
  { code: 'A', label: 'Rota A · Nevşehir → Kayseri → Ankara', type: 'Kara', km: 1185, co2: 146,  co2pt: '0,146', duration: '18 saat', cost: '$ $ $',     k1: true,  k3: true  },
  { code: 'B', label: 'Rota B · Nevşehir → Mersin → Berlin',   type: 'Kara+Deniz', km: 2830, co2: 492,  co2pt: '0,492', duration: '5 gün',  cost: '$ $ $ $',   k1: true,  k3: true  },
  { code: 'C', label: 'Rota C · Nevşehir → Ankara → Berlin',   type: 'Hava',  km: 3725, co2: 1980, co2pt: '1,980', duration: '1 gün',  cost: '$ $ $ $ $', k1: false, k3: false },
];

function BigMap({ last }: { last: any }) {
  // Stilize harita; backend distances.parquet'tan beslenebilir, demo'da görsel.
  return (
    <svg viewBox="0 0 900 500" style={{ width: '100%', height: '100%', display: 'block' }}>
      <defs>
        <pattern id="bm-grid" width="50" height="50" patternUnits="userSpaceOnUse">
          <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#1B2A3A" strokeWidth="0.3" opacity="0.06" />
        </pattern>
        <radialGradient id="bm-glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#C8553D" stopOpacity="0.4" />
          <stop offset="60%" stopColor="#C8553D" stopOpacity="0" />
        </radialGradient>
      </defs>

      <rect width="900" height="500" fill="url(#bm-grid)" />

      {/* Avrupa */}
      <path d="M 100 80 C 150 70, 220 100, 280 110 C 340 120, 380 140, 420 150 C 410 170, 380 200, 360 230 C 340 270, 360 300, 370 330 C 350 340, 320 340, 300 350 L 290 380 C 270 390, 230 360, 200 330 C 170 300, 130 280, 100 250 L 90 200 C 85 160, 90 110, 100 80 Z"
        fill="#E5DFCE" stroke="#1B2A3A" strokeWidth="0.5" opacity="0.5" />

      {/* Türkiye */}
      <path d="M 400 290 C 450 275, 540 285, 620 290 C 700 295, 780 300, 840 310 C 855 325, 840 350, 820 360 C 760 375, 660 385, 580 380 C 500 378, 420 380, 380 370 C 360 355, 360 320, 400 290 Z"
        fill="#E5DFCE" stroke="#1B2A3A" strokeWidth="0.5" opacity="0.6" />

      {/* Latitude lines */}
      {[120, 200, 280, 360, 440].map(y => (
        <g key={y}>
          <line x1="0" y1={y} x2="900" y2={y} stroke="#1B2A3A" strokeWidth="0.4" strokeDasharray="3 5" opacity="0.18" />
          <text x="8" y={y - 4} fontFamily="JetBrains Mono" fontSize="9" letterSpacing="2" fill="#6B7785">{60 - (y / 500) * 30 | 0}° N</text>
        </g>
      ))}

      {/* Routes */}
      <path d="M 600 320 C 540 280, 520 230, 320 130" fill="none" stroke="#C8553D" strokeWidth="1.6" strokeDasharray="6 4">
        <animate attributeName="stroke-dashoffset" values="0;-20" dur="1s" repeatCount="indefinite" />
      </path>
      <path d="M 600 320 C 580 280, 570 220, 560 165" fill="none" stroke="#1B2A3A" strokeWidth="1.2" strokeDasharray="3 5" opacity="0.6" />
      <path d="M 600 320 Q 560 260, 510 200" fill="none" stroke="#7A8B6E" strokeWidth="1.2" strokeDasharray="3 5" opacity="0.7" />

      {/* Cities */}
      {[
        { x: 600, y: 320, label: 'Nevşehir',  role: 'ÜRETİCİ',   color: '#1B2A3A', desc: '174 km · 22 tCO₂e' },
        { x: 660, y: 308, label: 'Kayseri',   role: 'İŞLEYİCİ',  color: '#1B2A3A', desc: '112 km · 14 tCO₂e' },
        { x: 540, y: 295, label: 'Konya',     role: 'İŞLEYİCİ',  color: '#1B2A3A' },
        { x: 510, y: 200, label: 'Ankara',    role: 'ALICI',     color: '#C8553D', desc: '1.185 km · 146 tCO₂e' },
        { x: 320, y: 130, label: 'Berlin',    role: 'ALICI',     color: '#C8553D', desc: '2.830 km · 492 tCO₂e' },
        { x: 560, y: 165, label: 'Kayseri',   role: 'ALICI',     color: '#C8553D' },
      ].map((p, i) => (
        <motion.g key={i} initial={{ opacity: 0, scale: 0.6 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 + i * 0.08 }}>
          <circle cx={p.x} cy={p.y} r="35" fill="url(#bm-glow)" />
          <circle cx={p.x} cy={p.y} r="6" fill={p.color} />
          <circle cx={p.x} cy={p.y} r="11" fill="none" stroke={p.color} strokeWidth="0.8" />
          <text x={p.x + 14} y={p.y - 8} fontFamily="JetBrains Mono" fontSize="9" letterSpacing="1.5" fill={p.color}>{p.role}</text>
          <text x={p.x + 14} y={p.y + 6} fontFamily="Fraunces" fontStyle="italic" fontSize="14" fill="#1B2A3A">{p.label}</text>
          {p.desc && <text x={p.x + 14} y={p.y + 22} fontFamily="JetBrains Mono" fontSize="9" fill="#6B7785" letterSpacing="0.5">{p.desc}</text>}
        </motion.g>
      ))}

      {/* Lejant */}
      <g transform="translate(520, 380)">
        <rect x="0" y="0" width="170" height="100" fill="#FFFDF7" stroke="#1B2A3A" strokeWidth="0.5" opacity="0.92" rx="2" />
        <text x="14" y="20" fontFamily="JetBrains Mono" fontSize="9" letterSpacing="2" fill="#1B2A3A">LEJANT</text>
        {[
          ['◆', 'Üretici', '#1B2A3A'],
          ['◉', 'İşleyici', '#1B2A3A'],
          ['◯', 'Alıcı', '#C8553D'],
          ['——', 'Rota A (Kara)', '#1B2A3A'],
          ['––', 'Rota B (Kara+Deniz)', '#7A8B6E'],
          ['··', 'Rota C (Hava)', '#C8553D'],
        ].map((row, i) => (
          <g key={i} transform={`translate(14, ${36 + i * 11})`}>
            <text x="0" y="0" fontFamily="JetBrains Mono" fontSize="10" fill={row[2] || '#1B2A3A'}>{row[0]}</text>
            <text x="20" y="0" fontFamily="JetBrains Mono" fontSize="8" letterSpacing="0.5" fill="#1B2A3A">{row[1]}</text>
          </g>
        ))}
      </g>
    </svg>
  );
}

function RotaOzet() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32 }}>
      <div>
        <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 12 }}>Seçili Rota · Rota A · Nevşehir → Kayseri → Ankara</div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <tbody>
            {[
              ['Rota Türü', 'Kara'],
              ['Toplam Mesafe', '1.185 km'],
              ['Tahmini CO₂', '146 tCO₂e'],
              ['Taşıma Modu', 'Kamyon'],
              ['Tahmini Süre', '18 saat'],
              ['Uygunluk Durumu', 'Uygun (Kural 1 ve Kural 3)'],
            ].map(([k, v]) => (
              <tr key={k} style={{ borderBottom: '1px dashed var(--hairline)' }}>
                <td style={{ padding: '8px 0', color: 'var(--ink-faded)', fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.06em' }}>{k}</td>
                <td style={{ padding: '8px 0', textAlign: 'right', fontFamily: 'var(--display)', fontWeight: 500 }}>{v}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 12 }}>Karbon Hesaplama Formülü</div>
        <div style={{ padding: 14, background: 'var(--bone-deep)', borderRadius: 4, fontFamily: 'var(--mono)', fontSize: 12, marginBottom: 16, lineHeight: 1.6 }}>
          CO₂ (tCO₂e) = Tonaj (ton) × Mesafe (km) × Emisyon Faktörü (kg CO₂/ton-km)
        </div>
        <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 8 }}>Rota A Karbon Hesap Özeti</div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <tbody>
            {[
              ['Tonaj (ton)', '1.000'],
              ['Mesafe (km)', '1.185'],
              ['Emisyon Faktörü (kg CO₂/ton-km)', '0,123'],
              ['Toplam CO₂ (tCO₂e)', '146'],
            ].map(([k, v]) => (
              <tr key={k} style={{ borderBottom: '1px dashed var(--hairline)' }}>
                <td style={{ padding: '8px 0', color: 'var(--ink-faded)' }}>{k}</td>
                <td style={{ padding: '8px 0', textAlign: 'right', fontFamily: 'var(--mono)', fontWeight: 500 }}>{v}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function KarbonHesabi() {
  return <RotaOzet />;
}

function YakinIsleyiciler() {
  const list = [
    ['Kayseri',          112, 5000, 92],
    ['Ürgüp (Nevşehir OSB)', 28,  2500, 88],
    ['Aksaray',          148, 3000, 84],
    ['Niğde',            168, 4200, 82],
    ['Kırşehir',         186, 2200, 76],
  ] as const;
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
        <span className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>Nevşehir'e Yakın İşleyiciler · Radius: 100 km</span>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead>
          <tr style={{ background: 'var(--bone-deep)' }}>
            {['İşleyici', 'Mesafe (km)', 'Kapasite (ton/yıl)', 'Uygunluk Skoru'].map(h => (
              <th key={h} style={{ textAlign: 'left', padding: '10px 14px', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--ink-faded)', fontWeight: 500 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {list.map((r, i) => (
            <tr key={i} style={{ borderTop: '1px solid var(--hairline)' }}>
              <td style={{ padding: '12px 14px', fontFamily: 'var(--display)', fontWeight: 500 }}>{r[0]}</td>
              <td style={{ padding: '12px 14px' }} className="numerals">{r[1]}</td>
              <td style={{ padding: '12px 14px' }} className="numerals">{r[2].toLocaleString('tr-TR')}</td>
              <td style={{ padding: '12px 14px' }}><strong>{r[3]}</strong></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AliciKumeleri() {
  const list = [
    ['Küme 1', 'İç Anadolu',     '2.100 ton/yıl'],
    ['Küme 2', 'Batı Türkiye',   '3.600 ton/yıl'],
    ['Küme 3', 'Avrupa (Yakın)', '1.800 ton/yıl'],
    ['Küme 4', 'Avrupa (Uzak)',  '2.400 ton/yıl'],
  ];
  return (
    <div>
      <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 12 }}>Alıcı Bölge Kümeleri</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
        {list.map((c, i) => (
          <div key={i} style={{ padding: 18, border: '1px solid var(--hairline)', borderRadius: 4 }}>
            <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--tuff)' }}>{c[0]}</div>
            <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 18, marginTop: 6 }}>{c[1]}</div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-faded)', marginTop: 4 }}>Tahmini Talep · {c[2]}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
