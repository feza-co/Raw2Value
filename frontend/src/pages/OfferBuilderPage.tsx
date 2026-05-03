import { useState } from 'react';
import { motion } from 'framer-motion';
import { useStore } from '../lib/store';
import { fmt } from '../lib/format';
import { useToast } from '../components/Toast';
import { PageHeader } from '../components/PageHeader';
import type { TransportMode } from '../lib/types';

type Tab = 'metin' | 'ticari' | 'lojistik' | 'ekler';

export function OfferBuilderPage() {
  const { last } = useStore();
  const toast = useToast();
  const [tab, setTab] = useState<Tab>('metin');

  const [offer, setOffer] = useState({
    unit_price: 96.50,
    total: 289500,
    processing_cost: 2.70,
    handling_cost: 8.40,
    currency: 'USD',
    incoterm: 'CIF İskenderun',
    payment_term: 'LC – Görüldüğünde',
    valid_until: '2025-05-30',
    delivery_plan: 'Haziran 2025 (Parti 1)',
    transport_mode: 'deniz' as TransportMode,
    package: 'Dökme yük (bulk)',
    notes: 'Piyasa fiyatı dalgalı. 96,50 USD/ton seviye 2 haftalık koruma sağlanmıştır.',
  });

  const totalEconomy = (offer.unit_price * 3000);
  const margin = totalEconomy * 0.0741;
  const co2Effect = 18750;
  const co2PerTon = 6.25;
  const fxRef = 32.45;

  const tonnage = last?.request.tonnage ?? 3000;
  const material = last ? fmt.matName(last.request.raw_material) : 'Bakır Cevheri';

  return (
    <div>
      <PageHeader
        title="Offer Builder"
        subtitle="Seçilen rota için teklif ve işlem özeti oluşturun"
        breadcrumbs={[{ label: 'Dashboard', to: '/dashboard' }, { label: 'AI Decision Cockpit', to: '/cockpit' }, { label: 'Offer Builder' }]}
        actions={
          <>
            <button className="btn btn-ghost btn-sm">📄 PDF Önizleme</button>
            <button className="btn btn-ghost btn-sm">💾 Kaydet</button>
            <button className="btn btn-ghost btn-sm">✉ E-posta Taslağı Üret</button>
            <button className="btn btn-ghost btn-sm">↗ CRM'e Aktar</button>
            <button className="btn btn-tuff btn-arrow" onClick={() => toast.push('Teklif gönderildi (demo)', 'ok')}>Gönder</button>
          </>
        }
      />

      {/* === ANA 3 PANEL === */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1.3fr 1fr', gap: 18, marginBottom: 22 }}>
        {/* 1. SEÇİM ÖZETİ */}
        <div className="panel" style={{ padding: 24 }}>
          <NumberHeader n="1" title="Seçim Özeti" />
          <div style={{ marginTop: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
            <Spec icon="◐" label="Malzeme" value={material} />
            <Spec icon="↗" label="Rota" value="Şili → Türkiye (Demir Çelik Tesisi)" />
            <Spec icon="◯" label="İşleyici (Tedarikçi)" value="Andes Minerals SpA" />
            <Spec icon="⌂" label="Alıcı" value="XYZ Demir Çelik A.Ş." />
            <Spec icon="⊟" label="Tonaj (ton)" value={fmt.num(tonnage)} />
            <Spec icon="◆" label="Kalite" value="%0,65 Cu, %0,03 As" />
            <Spec icon="€" label="Para Birimi" value={offer.currency} />
            <Spec icon="⏱" label="Teslim Süresi" value="45 gün" />
            <Spec icon="✦" label="AI Skoru" value="78 / 100" highlight />
          </div>
        </div>

        {/* 2. TEKLİF FORMU */}
        <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
          <NumberHeader n="2" title="Teklif Formu" inset />
          <div style={{ display: 'flex', borderBottom: '1px solid var(--hairline)' }}>
            {([
              ['metin', 'Teklif Metni'],
              ['ticari', 'Ticari Şartlar'],
              ['lojistik', 'Lojistik'],
              ['ekler', 'Ekler'],
            ] as [Tab, string][]).map(([k, label]) => (
              <button key={k} onClick={() => setTab(k)} style={{
                flex: 1, background: 'transparent', border: 'none', cursor: 'pointer',
                padding: '10px 14px', fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase',
                color: tab === k ? 'var(--ink)' : 'var(--ink-faded)',
                borderBottom: tab === k ? '2px solid var(--tuff)' : '2px solid transparent',
                fontWeight: tab === k ? 600 : 500,
              }}>
                {label}
              </button>
            ))}
          </div>
          <div style={{ padding: 22 }}>
            {tab === 'metin' && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
                <FormField label="Birim Fiyat (USD/ton)">
                  <input className="field-input numerals" type="number" step="0.01" value={offer.unit_price} onChange={e => setOffer({...offer, unit_price: Number(e.target.value)})} />
                </FormField>
                <FormField label="Toplam Fiyat (USD)">
                  <input className="field-input numerals" type="number" value={offer.total} onChange={e => setOffer({...offer, total: Number(e.target.value)})} />
                </FormField>
                <FormField label="İşleme Ücreti (USD/ton)">
                  <input className="field-input numerals" type="number" step="0.01" value={offer.processing_cost} onChange={e => setOffer({...offer, processing_cost: Number(e.target.value)})} />
                </FormField>
                <FormField label="Taşıma Maliyeti (USD/ton)">
                  <input className="field-input numerals" type="number" step="0.01" value={offer.handling_cost} onChange={e => setOffer({...offer, handling_cost: Number(e.target.value)})} />
                </FormField>
                <FormField label="Para Birimi">
                  <select className="field-select" value={offer.currency} onChange={e => setOffer({...offer, currency: e.target.value})}>
                    <option>USD</option><option>EUR</option><option>TRY</option>
                  </select>
                </FormField>
                <FormField label="Incoterm">
                  <select className="field-select" value={offer.incoterm} onChange={e => setOffer({...offer, incoterm: e.target.value})}>
                    <option>CIF İskenderun</option><option>FOB Mersin</option><option>EXW Şili</option><option>DAP Hamburg</option>
                  </select>
                </FormField>
                <FormField label="Ödeme Şartları">
                  <select className="field-select" value={offer.payment_term} onChange={e => setOffer({...offer, payment_term: e.target.value})}>
                    <option>LC – Görüldüğünde</option><option>LC – 30 gün</option><option>TT – Peşin</option>
                  </select>
                </FormField>
                <FormField label="Geçerlilik Tarihi">
                  <input className="field-input" type="date" value={offer.valid_until} onChange={e => setOffer({...offer, valid_until: e.target.value})} />
                </FormField>
                <FormField label="Teslim Planı">
                  <input className="field-input" value={offer.delivery_plan} onChange={e => setOffer({...offer, delivery_plan: e.target.value})} />
                </FormField>
                <div style={{ gridColumn: 'span 3' }}>
                  <FormField label="Ambalaj / Yükleme Notları">
                    <textarea className="field-input" rows={2} style={{ resize: 'vertical', fontFamily: 'var(--body)', padding: '6px 0', minHeight: 50 }}
                      value={offer.package} onChange={e => setOffer({...offer, package: e.target.value})} />
                  </FormField>
                </div>
                <div style={{ gridColumn: 'span 3' }}>
                  <FormField label="Notlar (İç Kullanım)">
                    <textarea className="field-input" rows={2} style={{ resize: 'vertical', fontFamily: 'var(--body)', padding: '6px 0', minHeight: 50 }}
                      value={offer.notes} onChange={e => setOffer({...offer, notes: e.target.value})} />
                  </FormField>
                </div>
              </div>
            )}
            {tab === 'ticari' && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14 }}>
                <FormField label="Cu Spesifikasyonu (%)"><input className="field-input numerals" defaultValue="0,60 — 0,70" /></FormField>
                <FormField label="As Spesifikasyonu (%)"><input className="field-input numerals" defaultValue="≤ 0,05" /></FormField>
                <FormField label="Nem (%)"><input className="field-input numerals" defaultValue="≤ 5" /></FormField>
                <FormField label="Diğer parametreler sözleşme şartlarına uygundur"><input className="field-input" defaultValue="—" /></FormField>
              </div>
            )}
            {tab === 'lojistik' && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14 }}>
                <FormField label="Taşıma Modu">
                  <select className="field-select" value={offer.transport_mode} onChange={e => setOffer({...offer, transport_mode: e.target.value as any})}>
                    <option value="deniz">Deniz</option><option value="kara">Kara</option><option value="demiryolu">Demir Yolu</option><option value="hava">Hava</option>
                  </select>
                </FormField>
                <FormField label="Yükleme Limanı"><input className="field-input" defaultValue="Mejillones / Antofagasta" /></FormField>
                <FormField label="Boşaltma Limanı"><input className="field-input" defaultValue="İskenderun" /></FormField>
                <FormField label="ETA"><input className="field-input" defaultValue="14 Haziran 2025" /></FormField>
              </div>
            )}
            {tab === 'ekler' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {['Piyasa_Analizi_Raporu.pdf (512 KB)', 'CO2_Sertifikasi.pdf (180 KB)', 'Kalite_Spec_Sheet.xlsx (45 KB)'].map(f => (
                  <div key={f} style={{ padding: '10px 14px', border: '1px solid var(--hairline)', borderRadius: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 11 }}>📎 {f}</span>
                    <button className="btn btn-ghost btn-sm">İndir</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 3. CANLI ÖZET */}
        <div className="panel" style={{ padding: 22 }}>
          <NumberHeader n="3" title="Canlı Özet" />
          <div style={{ marginTop: 18, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <SumLine label="Toplam Ekonomi (USD)" value={fmt.num(totalEconomy)} big />
            <SumLine label="Tahmini Brüt Marj (USD)" value={fmt.num(margin)} />
            <SumLine label="Marj Oranı" value="%7,41" tuff />
            <SumLine label="CO₂ Etkisi (kg CO₂e)" value={fmt.num(co2Effect)} />
            <SumLine label="CO₂ Yoğunluğu (kg CO₂e/ton)" value={fmt.num(co2PerTon, 2)} />
            <SumLine label="FX Referans (USD/TRY)" value={fxRef.toFixed(2)} />
          </div>

          <div style={{ marginTop: 22, padding: 18, background: 'var(--bone-deep)', borderRadius: 4, border: '1px solid var(--hairline)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <span style={{ fontSize: 16 }}>✦</span>
              <span style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 14 }}>AI Önerisi</span>
            </div>
            <p style={{ fontSize: 12, color: 'var(--ink-soft)', lineHeight: 1.5, margin: 0 }}>
              Birim fiyat <strong>+1,00 USD/ton</strong> artırılırsa marjınız <strong>%8,19</strong> seviyesine çıkabilir. Incoterm'de CPT alternatifi lojistik riskinizi azaltabilir.
            </p>
            <button className="btn btn-ghost btn-sm" style={{ marginTop: 10 }}>Detaylı Analiz Görüntüle</button>
          </div>
        </div>
      </section>

      {/* === TEKLİF ÖNİZLEME + AKTİVİTE === */}
      <section style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 18 }}>
        <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
          <NumberHeader n="4" title="Teklif Önizleme" inset right={
            <div style={{ display: 'flex', gap: 8 }}>
              <IconBtn>⊕</IconBtn><IconBtn>⊖</IconBtn><IconBtn>⤢</IconBtn>
            </div>
          } />
          <div style={{ padding: 32, background: 'var(--paper)' }}>
            {/* Document mockup */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--hairline-strong)', paddingBottom: 20 }}>
              <div>
                <div style={{ width: 80, height: 32, border: '1px solid var(--hairline)', display: 'grid', placeItems: 'center', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.1em', color: 'var(--ink-faded)', marginBottom: 8 }}>TEDARİKÇİ LOGO</div>
                <div style={{ fontSize: 11, color: 'var(--ink-soft)' }}>Andes Minerals SpA<br/>Av. Apoquindo 3000, Piso 7<br/>Las Condes, Santiago, Şili<br/>info@andesminerals.cl · +56 2 2334 5678</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <h2 style={{ fontFamily: 'var(--display)', fontSize: 32, fontWeight: 500, margin: 0, letterSpacing: '0.05em' }}>TEKLİF</h2>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-faded)', marginTop: 4 }}>Teklif No: OFF-2025-0514-001</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-faded)' }}>Tarih: 14 May 2025</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ width: 80, height: 32, border: '1px solid var(--hairline)', display: 'grid', placeItems: 'center', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.1em', color: 'var(--ink-faded)', marginBottom: 8 }}>ALICI LOGO</div>
                <div style={{ fontSize: 11, color: 'var(--ink-soft)' }}>XYZ Demir Çelik A.Ş.<br/>Organize Sanayi Bölgesi, 1. Cad. No: 15<br/>İskenderun, Hatay, Türkiye<br/>satinalma@xyzcelik.com · +90 326 123 4567</div>
              </div>
            </div>

            {/* Items table */}
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 22, fontSize: 13 }}>
              <thead>
                <tr style={{ background: 'var(--bone-deep)' }}>
                  {['#', 'Açıklama', 'Tonaj (ton)', 'Birim Fiyat (USD/ton)', 'Toplam Fiyat (USD)'].map(h => (
                    <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--ink-faded)', fontWeight: 500 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderTop: '1px solid var(--hairline)' }}>
                  <td style={{ padding: '12px 14px' }}>1</td>
                  <td style={{ padding: '12px 14px' }}>Bakır Cevheri (%0,60 – %0,70 Cu)</td>
                  <td style={{ padding: '12px 14px' }} className="numerals">{fmt.num(tonnage)}</td>
                  <td style={{ padding: '12px 14px' }} className="numerals">{offer.unit_price.toFixed(2)}</td>
                  <td style={{ padding: '12px 14px', fontFamily: 'var(--display)', fontWeight: 600 }} className="numerals">{fmt.num(offer.total)}</td>
                </tr>
              </tbody>
            </table>

            {/* Terms */}
            <div style={{ marginTop: 22, padding: 14, background: 'var(--bone-deep)', borderRadius: 4, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, fontSize: 11 }}>
              <Term label="Incoterm" v={offer.incoterm} />
              <Term label="Teslim Planı" v={offer.delivery_plan} />
              <Term label="Ödeme Şartları" v={offer.payment_term} />
              <Term label="Geçerlilik Tarihi" v={offer.valid_until} />
            </div>

            <p style={{ marginTop: 22, fontSize: 10, color: 'var(--ink-faded)', fontStyle: 'italic', textAlign: 'center' }}>
              Bu teklif {fmt.num(tonnage)} ton Bakır Cevheri için geçerlidir. Detaylı şartlar ve ekler teklif ekinde yer almaktadır.
            </p>
          </div>
          <div style={{ padding: '12px 22px', borderTop: '1px solid var(--hairline)', display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-faded)' }}>
            <span>1 / 2</span>
            <span>100% — ↻</span>
          </div>
        </div>

        {/* AKTIVITE & MUZAKERE */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
            <NumberHeader n="5" title="Aktivite & Yorumlar" inset />
            <div style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 12 }}>
              {COMMENTS.map((c, i) => (
                <motion.div key={i} initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}
                  style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 10, padding: 10, borderRadius: 4, background: c.self ? 'rgba(200,85,61,0.06)' : 'var(--bone-deep)' }}>
                  <div style={{ width: 30, height: 30, borderRadius: '50%', background: c.system ? 'var(--ink)' : 'var(--tuff)', color: 'var(--bone)', display: 'grid', placeItems: 'center', fontFamily: 'var(--display)', fontSize: 12, fontWeight: 500 }}>
                    {c.author[0]}
                  </div>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontWeight: 600, fontSize: 12 }}>{c.author} {c.self && <span style={{ fontSize: 9, opacity: 0.5, marginLeft: 4 }}>SİZ</span>} {c.system && <span style={{ fontSize: 9, padding: '2px 6px', background: 'var(--tuff)', color: 'var(--bone)', marginLeft: 4, borderRadius: 2 }}>AI</span>}</span>
                      <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-faded)' }}>{c.time}</span>
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--ink-soft)', lineHeight: 1.45 }}>{c.text}</div>
                  </div>
                </motion.div>
              ))}
              <textarea placeholder="Yorum ekleyin..." rows={2} style={{ width: '100%', padding: 10, border: '1px solid var(--hairline-strong)', borderRadius: 4, fontFamily: 'var(--body)', fontSize: 12, resize: 'vertical' }} />
            </div>
          </div>

          <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
            <NumberHeader n="6" title="Müzakere Geçmişi" inset />
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
              <thead>
                <tr style={{ background: 'var(--bone-deep)' }}>
                  {['Versiyon', 'Tarih', 'Birim Fiyat', 'Toplam Fiyat', 'Durum'].map(h => (
                    <th key={h} style={{ textAlign: 'left', padding: '8px 12px', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--ink-faded)', fontWeight: 500 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  ['v3', '14 May 2025 10:05', '96,50', '289.500,00', 'Mevcut',     'tuff'],
                  ['v2', '13 May 2025 16:42', '95,00', '285.000,00', 'Gönderildi', 'green'],
                  ['v1', '12 May 2025 11:20', '94,00', '282.000,00', 'Gönderildi', 'green'],
                ].map((r, i) => (
                  <tr key={i} style={{ borderTop: '1px solid var(--hairline)' }}>
                    <td style={{ padding: '10px 12px', fontFamily: 'var(--mono)' }}>{r[0]}</td>
                    <td style={{ padding: '10px 12px', fontFamily: 'var(--mono)', color: 'var(--ink-faded)' }}>{r[1]}</td>
                    <td style={{ padding: '10px 12px' }} className="numerals">{r[2]}</td>
                    <td style={{ padding: '10px 12px' }} className="numerals">{r[3]}</td>
                    <td style={{ padding: '10px 12px' }}>
                      <span style={{
                        fontFamily: 'var(--mono)', fontSize: 9, padding: '2px 8px', borderRadius: 999,
                        background: r[5] === 'tuff' ? 'rgba(200,85,61,0.18)' : 'rgba(107,142,90,0.15)',
                        color: r[5] === 'tuff' ? 'var(--tuff)' : 'var(--co2-green)',
                      }}>{r[4]}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ padding: '10px 18px', borderTop: '1px solid var(--hairline)', textAlign: 'right' }}>
              <button className="btn btn-ghost btn-sm">Geçmişi Karşılaştır</button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

const COMMENTS = [
  { author: 'Ahmet Yılmaz', self: true,  system: false, time: '14 May 2025 10:08', text: 'Birim fiyatı +1,00 güncel piyasa verisine göre 96,50 USD/ton olarak ayarladım. Lütfen onayınızı iletin.' },
  { author: 'Bora Kaya',    self: false, system: false, time: '14 May 2025 09:47', text: 'Teslim planını Haziran başı olarak revize ettik. Lütfen ödeme koşullarını netleştirin: LC 60 gün vadeli olarak revize edebilir miyiz?' },
  { author: 'Sistem',       self: false, system: true,  time: '14 May 2025 09:15', text: 'Piyasa analizi raporu eklendi. Piyasa_Analizi_Raporu.pdf (512 KB)' },
];

function NumberHeader({ n, title, inset, right }: { n: string; title: string; inset?: boolean; right?: React.ReactNode }) {
  const wrap: React.CSSProperties = inset
    ? { padding: '14px 22px', borderBottom: '1px solid var(--hairline)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }
    : { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 };
  return (
    <div style={wrap}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ width: 28, height: 28, borderRadius: '50%', border: '1px solid var(--ink)', background: 'var(--bone)', display: 'grid', placeItems: 'center', fontFamily: 'var(--display)', fontSize: 13, fontWeight: 500 }}>{n}</span>
        <span style={{ fontFamily: 'var(--display)', fontSize: 18, fontWeight: 500 }}>{title}</span>
      </div>
      {right}
    </div>
  );
}

function Spec({ icon, label, value, highlight }: { icon: string; label: string; value: string; highlight?: boolean }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, paddingBottom: 12, borderBottom: '1px dashed var(--hairline)' }}>
      <span style={{ fontSize: 14, color: 'var(--ink-faded)', width: 16, marginTop: 2 }}>{icon}</span>
      <div style={{ flex: 1 }}>
        <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>{label}</div>
        <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 13, marginTop: 2, color: highlight ? 'var(--tuff)' : 'var(--ink)', fontStyle: highlight ? 'italic' : 'normal' }}>{value}</div>
      </div>
    </div>
  );
}

function FormField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="field">
      <label className="field-label">{label}</label>
      {children}
    </div>
  );
}

function SumLine({ label, value, big, tuff }: { label: string; value: string; big?: boolean; tuff?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', paddingBottom: 10, borderBottom: '1px dashed var(--hairline)' }}>
      <span className="numerals" style={{ fontSize: 10, letterSpacing: '0.1em', color: 'var(--ink-faded)' }}>{label}</span>
      <span className="numerals" style={{
        fontFamily: 'var(--display)', fontWeight: big ? 600 : 500,
        fontSize: big ? 22 : 16, color: tuff ? 'var(--tuff)' : 'var(--ink)',
      }}>{value}</span>
    </div>
  );
}

function Term({ label, v }: { label: string; v: string }) {
  return (
    <div>
      <div className="numerals" style={{ fontSize: 8, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>{label}</div>
      <div style={{ fontWeight: 500, fontSize: 11, marginTop: 2 }}>{v}</div>
    </div>
  );
}

function IconBtn({ children }: { children: React.ReactNode }) {
  return <button style={{ background: 'transparent', border: '1px solid var(--hairline)', borderRadius: 3, padding: '4px 10px', cursor: 'pointer', fontSize: 13, color: 'var(--ink)' }}>{children}</button>;
}
