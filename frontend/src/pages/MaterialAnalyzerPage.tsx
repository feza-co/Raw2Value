import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../lib/api';
import { fmt } from '../lib/format';
import { useStore } from '../lib/store';
import { useToast } from '../components/Toast';
import { PageHeader } from '../components/PageHeader';
import { Stepper } from '../components/Stepper';
import { Slider } from '../components/Slider';
import type { AnalyzeRequest, RawMaterial, Quality, TargetCountry, TransportMode, InputMode } from '../lib/types';

interface State {
  raw_material: RawMaterial | null;
  origin_city: string;
  district: string;
  origin_type: string;
  facility_scale: string;
  tonnage: number;
  quality: Quality;
  purity_pct: number;
  moisture_pct: number;
  particle_size_class: string;
  market_orientation: 'yurtici' | 'ihracat';
  target_country: TargetCountry;
  transport_mode: TransportMode;
  delivery_days: number;
  currency: string;
  // priorities (0-100)
  pr_profit: number;
  pr_carbon: number;
  pr_speed: number;
  pr_local: number;
  pr_export: number;
  input_mode: InputMode;
}

const INITIAL: State = {
  raw_material: null,
  origin_city: '',
  district: '',
  origin_type: '',
  facility_scale: '',
  tonnage: 250,
  quality: 'A',
  purity_pct: 92,
  moisture_pct: 5,
  particle_size_class: 'medium',
  market_orientation: 'ihracat',
  target_country: 'DE',
  transport_mode: 'kara',
  delivery_days: 30,
  currency: 'USD',
  pr_profit: 70, pr_carbon: 50, pr_speed: 60, pr_local: 40, pr_export: 80,
  input_mode: 'basic',
};

const MATERIAL_CARDS: { v: RawMaterial; title: string; sub: string; }[] = [
  { v: 'pomza',           title: 'Pomza',           sub: 'Hafif, gözenekli volkanik kaya. İnşaat, tarım ve endüstride kullanılır.' },
  { v: 'perlit',          title: 'Perlit',          sub: 'Genleşebilen volkanik mineral. Yalıtım, tarım ve filtrasyon uygulamaları.' },
  { v: 'kabak_cekirdegi', title: 'Kabak Çekirdeği', sub: 'Tarım yan ürünü; yağ, yem ve biyokömür için değerlendirilebilir.' },
];

export function MaterialAnalyzerPage() {
  const nav = useNavigate();
  const toast = useToast();
  const { setLast } = useStore();
  const [step, setStep] = useState(1);
  const [s, setS] = useState<State>(INITIAL);

  const update = (patch: Partial<State>) => setS(prev => ({ ...prev, ...patch }));

  const m = useMutation({
    mutationFn: (p: AnalyzeRequest) => api.analyze(p),
    onSuccess: (data, vars) => {
      setLast({ request: vars, response: data, ts: Date.now() });
      toast.push('Analiz tamam · Cockpit\'e geçiliyor', 'ok');
      nav('/cockpit');
    },
    onError: (e: any) => toast.push(e?.message || 'Analiz hatası', 'error'),
  });

  const submit = () => {
    if (!s.raw_material) { toast.push('Hammadde seçin', 'error'); setStep(1); return; }
    if (!s.origin_city)  { toast.push('Köken şehri girin', 'error'); setStep(2); return; }
    const priority = s.pr_carbon >= s.pr_profit && s.pr_carbon >= s.pr_speed ? 'low_carbon'
      : s.pr_speed >= s.pr_profit ? 'fast_delivery' : 'max_profit';
    const payload: AnalyzeRequest = {
      raw_material: s.raw_material,
      tonnage: s.tonnage,
      quality: s.quality,
      origin_city: s.origin_city,
      target_country: s.target_country,
      target_city: undefined,
      transport_mode: s.transport_mode,
      priority: priority as any,
      input_mode: s.input_mode,
      moisture_pct: s.input_mode === 'advanced' ? s.moisture_pct : undefined,
      purity_pct: s.input_mode === 'advanced' ? s.purity_pct : undefined,
      particle_size_class: s.input_mode === 'advanced' ? s.particle_size_class : undefined,
      fx_scenario_pct: 0,
      cost_scenario_pct: 0,
    };
    m.mutate(payload);
  };

  return (
    <div>
      <PageHeader
        title="Material Analyzer"
        subtitle="Hammadde analizi için giriş ekranı"
        breadcrumbs={[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Material Analyzer' }]}
      />

      <div className="panel" style={{ padding: '32px 36px', marginBottom: 28 }}>
        <Stepper
          current={step}
          onSelect={(i) => setStep(i)}
          steps={[
            { label: 'Hammadde' },
            { label: 'Kaynak & Lokasyon' },
            { label: 'Kalite & Tonaj' },
            { label: 'Pazar & Lojistik' },
            { label: 'Öncelikler' },
          ]}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 0.8fr', gap: 24 }}>
        <div className="panel" style={{ padding: 32, minHeight: 520 }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -12 }}
              transition={{ duration: 0.28, ease: [0.2, 0.7, 0.3, 1] }}
            >
              {step === 1 && <Step1 selected={s.raw_material} onSelect={v => update({ raw_material: v })} />}
              {step === 2 && <Step2 s={s} update={update} />}
              {step === 3 && <Step3 s={s} update={update} />}
              {step === 4 && <Step4 s={s} update={update} />}
              {step === 5 && <Step5 s={s} update={update} />}
            </motion.div>
          </AnimatePresence>

          <div style={{ marginTop: 36, paddingTop: 22, borderTop: '1px solid var(--ink)', display: 'flex', justifyContent: 'space-between' }}>
            <button className="btn btn-ghost" onClick={() => setStep(Math.max(1, step - 1))} disabled={step === 1}>← Geri</button>
            {step < 5
              ? <button className="btn btn-primary btn-arrow" onClick={() => setStep(step + 1)}>İleri</button>
              : <button className="btn btn-primary btn-arrow" onClick={submit} disabled={m.isPending}>
                  {m.isPending ? <><span className="atlas-loader" /><span>Analiz Çalışıyor</span></> : <span>Analizi Başlat</span>}
                </button>
            }
          </div>
        </div>

        {/* === SAĞ YAPIŞKAN ÖZET === */}
        <aside style={{ display: 'flex', flexDirection: 'column', gap: 18, position: 'sticky', top: 100, alignSelf: 'flex-start' }}>
          <div className="panel" style={{ padding: 22 }}>
            <span className="eyebrow">Analiz Özeti</span>
            <h4 style={{ fontFamily: 'var(--display)', fontSize: 16, fontWeight: 500, marginTop: 8, marginBottom: 18 }}>Seçimleriniz</h4>

            <Group label="Hammadde" v={s.raw_material ? fmt.matName(s.raw_material) : '—'} />
            <Group label="Kaynak & Lokasyon" rows={[
              ['Konum', s.origin_city || '—'],
              ['İl / İlçe', `${s.origin_city || '—'} / ${s.district || '—'}`],
              ['Koordinat', s.origin_city ? '~ enlem/boylam parquet\'tan' : '—'],
            ]} />
            <Group label="Ürün Özellikleri" rows={[
              ['Tonaj', `${fmt.num(s.tonnage)} t`],
              ['Kalite Grade', fmt.qualityLabel(s.quality)],
              ['Saflık', `${s.purity_pct}%`],
              ['Nem', `${s.moisture_pct}%`],
              ['Parçacık Boyutu', s.particle_size_class],
            ]} />
            <Group label="Pazar & Lojistik" rows={[
              ['Pazar', s.market_orientation === 'ihracat' ? 'İhracat' : 'Yurtiçi'],
              ['Hedef Bölge / Ülke', fmt.countryName(s.target_country)],
              ['Taşıma Modu', fmt.transportLabel(s.transport_mode)],
              ['Teslim Süresi', `${s.delivery_days} gün`],
              ['Para Birimi', s.currency],
            ]} />
            <Group label="Karar Öncelikleri" rows={[
              ['Maks. Kar', `${s.pr_profit}/100`],
              ['Düşük Karbon', `${s.pr_carbon}/100`],
              ['Hızlı Teslimat', `${s.pr_speed}/100`],
              ['Yerel İşleme', `${s.pr_local}/100`],
              ['İhracat Odaklılık', `${s.pr_export}/100`],
            ]} last />
          </div>

          <div className="panel" style={{ padding: 22 }}>
            <span className="eyebrow">Yakın İşleyici Tahmini</span>
            <div style={{ marginTop: 12, display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 12, alignItems: 'center' }}>
              <span className="numerals" style={{ fontFamily: 'var(--display)', fontSize: 38, fontWeight: 500, color: 'var(--tuff)' }}>
                {s.origin_city ? '~12' : '—'}
              </span>
              <span style={{ fontSize: 12, color: 'var(--ink-soft)', lineHeight: 1.4 }}>
                {s.origin_city
                  ? `${s.origin_city} 250 km radyusunda eşleşen işleyici sayısı (parquet referans).`
                  : 'Konum girince yakın işleyici sayısı tahmin edilir.'}
              </span>
            </div>
          </div>

          <button className="btn btn-tuff btn-arrow" style={{ width: '100%', justifyContent: 'center' }} onClick={submit} disabled={m.isPending || !s.raw_material || !s.origin_city}>
            {m.isPending ? <><span className="atlas-loader" /><span>Analiz Çalışıyor</span></> : <span>Analizi Başlat</span>}
          </button>
          <button className="btn btn-ghost" style={{ width: '100%', justifyContent: 'center' }}>Taslak Kaydet</button>
        </aside>
      </div>
    </div>
  );
}

/* === STEPS === */

function Step1({ selected, onSelect }: { selected: RawMaterial | null; onSelect: (v: RawMaterial) => void }) {
  return (
    <div>
      <h3 style={{ fontFamily: 'var(--display)', fontSize: 24, fontWeight: 500, margin: 0 }}>1. Hammadde Bilgisi</h3>
      <p style={{ fontFamily: 'var(--display)', fontStyle: 'italic', color: 'var(--ink-soft)', marginTop: 6, marginBottom: 24 }}>Analiz etmek istediğiniz maddeyi seçin.</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        {MATERIAL_CARDS.map(c => (
          <button key={c.v}
            type="button"
            onClick={() => onSelect(c.v)}
            style={{
              padding: 22, textAlign: 'left', cursor: 'pointer',
              background: selected === c.v ? 'var(--ink)' : 'var(--paper)',
              color: selected === c.v ? 'var(--bone)' : 'var(--ink)',
              border: `1px solid ${selected === c.v ? 'var(--ink)' : 'var(--hairline)'}`,
              borderRadius: 4, transition: 'all 200ms ease',
              boxShadow: selected === c.v ? '0 12px 30px -16px rgba(27,42,58,0.5)' : 'none',
            }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <span style={{
                width: 38, height: 38, borderRadius: '50%',
                border: `1px solid ${selected === c.v ? 'var(--bone)' : 'var(--hairline-strong)'}`,
                display: 'grid', placeItems: 'center',
                fontFamily: 'var(--display)', fontStyle: 'italic',
                color: selected === c.v ? 'var(--tuff)' : 'var(--ink-soft)',
              }}>{c.v[0]?.toUpperCase()}</span>
              {selected === c.v && <span style={{ fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.2em', color: 'var(--tuff)' }}>SEÇİLİ</span>}
            </div>
            <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 19, letterSpacing: '-0.01em' }}>{c.title}</div>
            <div style={{ fontSize: 12, marginTop: 8, lineHeight: 1.45, opacity: 0.78 }}>{c.sub}</div>
          </button>
        ))}
        <button type="button" disabled style={{
          padding: 22, textAlign: 'left', cursor: 'not-allowed', opacity: 0.55,
          background: 'var(--paper)', border: '1px dashed var(--hairline-strong)', borderRadius: 4,
        }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.2em', color: 'var(--ink-faded)' }}>YAKINDA</span>
          <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 19, marginTop: 12 }}>Özel Hammadde</div>
          <div style={{ fontSize: 12, marginTop: 8, color: 'var(--ink-faded)' }}>Listede yoksa kendi hammadde tanımınızı ekleyin.</div>
        </button>
      </div>
    </div>
  );
}

function Step2({ s, update }: { s: State; update: (p: Partial<State>) => void }) {
  return (
    <div>
      <h3 style={{ fontFamily: 'var(--display)', fontSize: 24, fontWeight: 500, margin: 0 }}>2. Kaynak Bilgisi</h3>
      <p style={{ fontFamily: 'var(--display)', fontStyle: 'italic', color: 'var(--ink-soft)', marginTop: 6, marginBottom: 24 }}>Hammadde kaynağının konum ve tedarik bilgilerini girin.</p>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 18, marginBottom: 18 }}>
        <FieldBox label="Konum Arama">
          <input className="field-input" placeholder="Adres, ilçe, köy veya koordinat ara…" value={s.origin_city} onChange={e => update({ origin_city: e.target.value })} />
        </FieldBox>
        <FieldBox label="İl">
          <select className="field-select" value={s.origin_city} onChange={e => update({ origin_city: e.target.value })}>
            <option value="">Seçiniz</option>
            <option>Nevşehir</option><option>İzmir</option><option>Acıgöl</option><option>Ürgüp</option><option>Kırşehir</option>
          </select>
        </FieldBox>
        <FieldBox label="İlçe">
          <input className="field-input" placeholder="Seçiniz" value={s.district} onChange={e => update({ district: e.target.value })} />
        </FieldBox>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 18 }}>
        <FieldBox label="Üretici / Kaynak Türü">
          <select className="field-select" value={s.origin_type} onChange={e => update({ origin_type: e.target.value })}>
            <option value="">Seçiniz</option>
            <option>Maden Ocağı</option><option>İşletme</option><option>Tarım Üreticisi</option>
          </select>
        </FieldBox>
        <FieldBox label="Tesis Ölçeği">
          <select className="field-select" value={s.facility_scale} onChange={e => update({ facility_scale: e.target.value })}>
            <option value="">Seçiniz</option>
            <option>Küçük (&lt; 10K t/yıl)</option><option>Orta (10K–50K t/yıl)</option><option>Büyük (&gt; 50K t/yıl)</option>
          </select>
        </FieldBox>
        <FieldBox label="Koordinat (Opsiyonel)">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            <input className="field-input numerals" placeholder="Enlem 39.92" />
            <input className="field-input numerals" placeholder="Boylam 32.85" />
          </div>
        </FieldBox>
      </div>
      <p style={{ fontSize: 11, color: 'var(--ink-faded)', marginTop: 18, fontStyle: 'italic' }}>
        Konum bilgisi, yakın işleyiciler ve lojistik fizibilite için kritiktir.
      </p>
    </div>
  );
}

function Step3({ s, update }: { s: State; update: (p: Partial<State>) => void }) {
  return (
    <div>
      <h3 style={{ fontFamily: 'var(--display)', fontSize: 24, fontWeight: 500, margin: 0 }}>3. Ürün Özellikleri</h3>
      <p style={{ fontFamily: 'var(--display)', fontStyle: 'italic', color: 'var(--ink-soft)', marginTop: 6, marginBottom: 24 }}>Mevcut ürününüzün temel özelliklerini girin.</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18, marginBottom: 18 }}>
        <FieldBox label="Tonaj (ton)">
          <input className="field-input numerals" type="number" value={s.tonnage} onChange={e => update({ tonnage: Number(e.target.value) })} placeholder="Örn. 250" />
        </FieldBox>
        <FieldBox label="Kalite Grade">
          <select className="field-select" value={s.quality} onChange={e => update({ quality: e.target.value as Quality })}>
            <option value="A">A · Premium</option><option value="B">B · Standart</option><option value="C">C · Düşük</option><option value="unknown">Belirsiz</option>
          </select>
        </FieldBox>
        <FieldBox label="Saflık (%)">
          <input className="field-input numerals" type="number" value={s.purity_pct} onChange={e => update({ purity_pct: Number(e.target.value), input_mode: 'advanced' })} placeholder="Örn. 92" />
        </FieldBox>
        <FieldBox label="Nem (%)">
          <input className="field-input numerals" type="number" value={s.moisture_pct} onChange={e => update({ moisture_pct: Number(e.target.value), input_mode: 'advanced' })} placeholder="Örn. 8" />
        </FieldBox>
      </div>
      <FieldBox label="Parçacık Boyutu">
        <select className="field-select" value={s.particle_size_class} onChange={e => update({ particle_size_class: e.target.value, input_mode: 'advanced' })}>
          <option value="fine">İnce</option><option value="medium">Orta</option><option value="coarse">İri</option>
        </select>
      </FieldBox>

      <div style={{ marginTop: 22, padding: 18, background: 'var(--bone-deep)', borderRadius: 4, display: 'flex', alignItems: 'center', gap: 14 }}>
        <span style={{ fontSize: 20 }}>↑</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, fontSize: 13 }}>Teknik Doküman / Spec Sheet (Opsiyonel)</div>
          <div style={{ fontSize: 11, color: 'var(--ink-faded)', marginTop: 2 }}>CSV, PDF veya XLSX dosyası yükleyin (Maks. 10 MB).</div>
        </div>
        <button className="btn btn-ghost btn-sm">Dosya Yükle</button>
      </div>
    </div>
  );
}

function Step4({ s, update }: { s: State; update: (p: Partial<State>) => void }) {
  return (
    <div>
      <h3 style={{ fontFamily: 'var(--display)', fontSize: 24, fontWeight: 500, margin: 0 }}>4. Hedef Pazar & Lojistik</h3>
      <p style={{ fontFamily: 'var(--display)', fontStyle: 'italic', color: 'var(--ink-soft)', marginTop: 6, marginBottom: 24 }}>Ürününüzü nereye ve nasıl ulaştırmak istediğinizi belirtin.</p>

      <FieldBox label="Pazar Yönelimi">
        <div style={{ display: 'flex', gap: 0, border: '1px solid var(--hairline-strong)', borderRadius: 4, overflow: 'hidden', maxWidth: 320 }}>
          {(['yurtici', 'ihracat'] as const).map(v => (
            <button key={v}
              type="button"
              onClick={() => update({ market_orientation: v })}
              style={{
                flex: 1, padding: '10px 16px',
                background: s.market_orientation === v ? 'var(--ink)' : 'var(--paper)',
                color: s.market_orientation === v ? 'var(--bone)' : 'var(--ink)',
                border: 'none', cursor: 'pointer',
                fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase',
              }}>
              {v === 'yurtici' ? 'Yurtiçi' : 'İhracat'}
            </button>
          ))}
        </div>
      </FieldBox>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18, marginTop: 18 }}>
        <FieldBox label="Hedef Bölge / Ülke">
          <select className="field-select" value={s.target_country} onChange={e => update({ target_country: e.target.value as TargetCountry })}>
            <option value="DE">🇩🇪 Almanya</option><option value="NL">🇳🇱 Hollanda</option><option value="TR">🇹🇷 Türkiye</option>
          </select>
        </FieldBox>
        <FieldBox label="Taşıma Modu">
          <select className="field-select" value={s.transport_mode} onChange={e => update({ transport_mode: e.target.value as TransportMode })}>
            <option value="kara">Kara · 0.100 kg/t·km</option>
            <option value="deniz">Deniz · 0.015 kg/t·km</option>
            <option value="demiryolu">Demir Yolu · 0.030 kg/t·km</option>
            <option value="hava">Hava · 0.500 kg/t·km</option>
          </select>
        </FieldBox>
        <FieldBox label="Teslim Süresi">
          <input className="field-input numerals" type="number" value={s.delivery_days} onChange={e => update({ delivery_days: Number(e.target.value) })} />
        </FieldBox>
        <FieldBox label="Para Birimi">
          <select className="field-select" value={s.currency} onChange={e => update({ currency: e.target.value })}>
            <option>USD</option><option>EUR</option><option>TRY</option>
          </select>
        </FieldBox>
      </div>
    </div>
  );
}

function Step5({ s, update }: { s: State; update: (p: Partial<State>) => void }) {
  return (
    <div>
      <h3 style={{ fontFamily: 'var(--display)', fontSize: 24, fontWeight: 500, margin: 0 }}>5. Karar Öncelikleri</h3>
      <p style={{ fontFamily: 'var(--display)', fontStyle: 'italic', color: 'var(--ink-soft)', marginTop: 6, marginBottom: 28 }}>Karar algoritmasını yönlendirmek için önceliklerinizi belirtin.</p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
        <Slider label="Maksimum Kâr" unit="0–100" value={s.pr_profit} onChange={v => update({ pr_profit: v })} min={0} max={100} hint="profit ağırlığı" />
        <Slider label="Düşük Karbon" unit="0–100" value={s.pr_carbon} onChange={v => update({ pr_carbon: v })} min={0} max={100} hint="emisyon minimizasyonu" />
        <Slider label="Hızlı Teslimat" unit="0–100" value={s.pr_speed} onChange={v => update({ pr_speed: v })} min={0} max={100} hint="lead-time önemi" />
        <Slider label="Yerel İşleme" unit="0–100" value={s.pr_local} onChange={v => update({ pr_local: v })} min={0} max={100} hint="yakın işleyici tercihi" />
        <Slider label="İhracat Odaklılık" unit="0–100" value={s.pr_export} onChange={v => update({ pr_export: v })} min={0} max={100} hint="DE/NL pazarı" />
      </div>

      <p style={{ fontSize: 11, color: 'var(--ink-faded)', marginTop: 24, fontStyle: 'italic' }}>
        Sürgüyü sağa kaydırdıkça ilgili önceliğin ağırlığı artar. 0 = Önemsiz, 100 = En yüksek öncelik.
      </p>
    </div>
  );
}

/* === Helpers === */

function FieldBox({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="field" style={{ flex: 1, minWidth: 0 }}>
      <label className="field-label">{label}</label>
      {children}
    </div>
  );
}

function Group({ label, v, rows, last }: { label: string; v?: string; rows?: [string, string][]; last?: boolean }) {
  return (
    <div style={{ marginBottom: last ? 0 : 18, paddingBottom: last ? 0 : 14, borderBottom: last ? 'none' : '1px solid var(--hairline)' }}>
      <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 8 }}>{label}</div>
      {v && <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 14 }}>{v}</div>}
      {rows && rows.map(([k, val]) => (
        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--ink-soft)', marginTop: 4 }}>
          <span style={{ color: 'var(--ink-faded)' }}>{k}</span>
          <span style={{ fontWeight: 500, color: 'var(--ink)' }}>{val}</span>
        </div>
      ))}
    </div>
  );
}
