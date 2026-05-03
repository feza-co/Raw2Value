import { useState } from 'react';
import { motion } from 'framer-motion';
import { useStore } from '../lib/store';
import { fmt } from '../lib/format';
import { useToast } from '../components/Toast';
import { PageHeader } from '../components/PageHeader';
import { ConfidenceGauge } from '../components/Gauges';

type Tab = 'preview' | 'pdf' | 'shares' | 'versions';

export function RawMaterialPassportPage() {
  const { last } = useStore();
  const toast = useToast();
  const [tab, setTab] = useState<Tab>('preview');

  const passportId = 'RMP-2025-000124';
  const created = '14 May 2025 10:45';
  const score = last ? Math.round(last.response.confidence.overall) : 78;
  const profitTry = last?.response.expected_profit_try ?? 5_460_000;
  const valid = last?.response.value_uplift_pct ?? 0.186;
  const co2PerTon = last ? last.response.co2_kg / Math.max(last.request.tonnage, 1) : 125;

  return (
    <div>
      <PageHeader
        title="Raw Material Passport"
        subtitle="Hammadde ve önerilen tedarik zinciri çıktısının dijital pasaportu"
        breadcrumbs={[{ label: 'Dashboard', to: '/dashboard' }, { label: 'AI Decision Cockpit', to: '/cockpit' }, { label: 'Raw Material Passport' }]}
        actions={
          <>
            <button className="btn btn-ghost btn-sm">📥 PDF İndir</button>
            <button className="btn btn-ghost btn-sm">↗ Paylaş</button>
            <button className="btn btn-ghost btn-sm">🔗 Doğrulama Linki Oluştur</button>
            <button className="btn btn-tuff btn-arrow" onClick={() => toast.push('Teklife bağlandı (demo)', 'ok')}>⚐ Teklife Bağla</button>
          </>
        }
      />

      {/* === HEADER STRIP: ID + QR === */}
      <section className="panel" style={{ padding: 22, marginBottom: 22 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'auto auto auto auto auto', gap: 32, alignItems: 'center' }}>
          <div>
            <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>Pasaport ID</div>
            <div className="numerals" style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 22, marginTop: 4, letterSpacing: '0.02em' }}>
              {passportId}
              <button onClick={() => { navigator.clipboard.writeText(passportId); toast.push('Pasaport ID kopyalandı', 'ok', 1500); }}
                style={{ marginLeft: 10, background: 'transparent', border: '1px solid var(--hairline)', padding: '2px 8px', cursor: 'pointer', borderRadius: 3, fontSize: 12, color: 'var(--ink-faded)' }}>⧉</button>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>Durum</div>
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              fontFamily: 'var(--mono)', fontSize: 11, padding: '4px 12px', borderRadius: 999,
              background: 'rgba(107,142,90,0.16)', color: 'var(--co2-green)',
            }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--co2-green)' }} /> Geçerli
            </span>
          </div>

          <div>
            <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>Oluşturulma Tarihi</div>
            <div style={{ fontSize: 13, fontWeight: 500, marginTop: 4, fontFamily: 'var(--mono)' }}>📅 {created}</div>
          </div>
          <div>
            <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>Son Güncelleme</div>
            <div style={{ fontSize: 13, fontWeight: 500, marginTop: 4, fontFamily: 'var(--mono)' }}>📅 {created}</div>
          </div>

          {/* QR + Doğrulama */}
          <div style={{ display: 'flex', gap: 18, alignItems: 'center', justifySelf: 'end' }}>
            <div>
              <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 4 }}>QR Kod</div>
              <FakeQR size={60} />
            </div>
            <div>
              <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 6 }}>Doğrulama</div>
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: 6,
                padding: '8px 12px', border: '1px solid var(--co2-green)', borderRadius: 4,
                fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--co2-green)',
              }}>
                <span style={{ width: 24, height: 24, borderRadius: '50%', background: 'rgba(107,142,90,0.16)', display: 'grid', placeItems: 'center' }}>🛡</span>
                Raw2Value AI<br/>Doğrulanmış
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* === 8 KART GRID === */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18, marginBottom: 22 }}>
        {/* 1. Hammadde Kaynağı */}
        <Card num="1" title="Hammadde Kaynağı" footer="Kaynak Detayları →">
          <Mini icon="◐" label="Hammadde" v={last ? fmt.matName(last.request.raw_material) : 'Bakır Cevheri'} />
          <Mini icon="🌐" label="Kaynak Ülke" v="Şili" />
          <Mini icon="◉" label="Kaynak Bölge" v="Antofagasta" />
          <Mini icon="⚒" label="Maden Tipi" v="Açık Ocak" />
          <Mini icon="✓" label="Sertifika" v="ISO 14001" />
          <FakeMap small />
        </Card>

        {/* 2. İşleme Rotası */}
        <Card num="2" title="İşleme Rotası" footer="Rota Detayları →">
          <div style={{ padding: 12, background: 'var(--bone-deep)', borderRadius: 4, marginBottom: 14 }}>
            <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>Seçilen Rota</div>
            <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 14, marginTop: 4 }}>{last ? fmt.routeShort(last.response.recommended_route) : 'Rota-3 (Düşük Karbon)'}</div>
          </div>
          <RouteSteps />
          <ul style={{ padding: 0, margin: '12px 0 0', listStyle: 'none', fontSize: 11, lineHeight: 1.7, color: 'var(--ink-soft)' }}>
            <li>· Düşük karbon yoğunluğu</li>
            <li>· Bölgesel işleme avantajı</li>
            <li>· Daha kısa lojistik mesafe</li>
          </ul>
        </Card>

        {/* 3. İşleyici Bilgisi */}
        <Card num="3" title="İşleyici Bilgisi" footer="İşleyici Profili →">
          <Mini icon="🏭" label="İşleyici Adı" v="GreenMet Processing Ltd." />
          <Mini icon="◉" label="Tesis Lokasyonu" v="İzmir, Türkiye" />
          <Mini icon="⊟" label="Kapasite" v="250.000 ton/yıl" />
          <Mini icon="✓" label="Sertifikalar" v="ISO 14001, ISO 45001" />
        </Card>

        {/* 4. Alıcı Pazarı */}
        <Card num="4" title="Alıcı Pazarı" footer="Alıcı Profili →">
          <Mini icon="🏬" label="Alıcı Adı" v="Global Metals Trading Inc." />
          <Mini icon="🌐" label="Hedef Pazar" v={last ? fmt.countryName(last.request.target_country) : 'Avrupa Birliği'} />
          <Mini icon="◉" label="Teslimat Noktası" v="Rotterdam, Hollanda" />
          <Mini icon="📋" label="Sözleşme Türü" v="Spot" />
        </Card>
      </section>

      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18, marginBottom: 22 }}>
        {/* 5. Karbon ve Rota Özeti */}
        <Card num="5" title="Karbon ve Rota Özeti" footer="Sürdürülebilirlik Raporu →">
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
            <span className="numerals" style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 36, color: 'var(--ink)' }}>
              {fmt.num(co2PerTon, 0)}
            </span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-faded)', letterSpacing: '0.1em' }}>kg CO₂e / ton</span>
          </div>
          <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 8 }}>
            <Mini label="Rota Karbon Yoğunluğu" v="Düşük" />
            <Mini label="Karbon Tasarrufu" v="%28" />
            <Mini icon="A" label="Sürdürülebilirlik Sınıfı" v="" />
          </div>
        </Card>

        {/* 6. Finansal Özet */}
        <Card num="6" title="Finansal Özet" footer="Finansal Detaylar →">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <Mini label="Canlı FX Kuru (USD/TRY)" v="32,45" />
            <Mini label="Beklenen Brüt Kâr (USD/ton)" v="74,20" />
            <Mini label="Değer Artışı (Value Uplift)" v={fmt.pct(valid, 1)} highlight />
            <Mini label="Tahmini Kâr Aralığı (USD/ton)" v="65,00 – 85,00" />
          </div>
        </Card>

        {/* 7. AI Recommendation Reasons */}
        <Card num="7" title="AI Recommendation Reasons" footer="Neden Detayları →">
          <div style={{ textAlign: 'center' }}>
            <ConfidenceGauge value={score} size={130} label="AI Skoru (0–100)" />
          </div>
          <div style={{ marginTop: 12, textAlign: 'center', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.16em', color: 'var(--ink-faded)', textTransform: 'uppercase' }}>
            Öneri Güven Seviyesi · <strong style={{ color: 'var(--co2-green)' }}>Yüksek</strong>
          </div>
          <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px dashed var(--hairline)' }}>
            <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.16em', color: 'var(--ink-faded)', textTransform: 'uppercase', marginBottom: 6 }}>Neden Kodları</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {['RC-01', 'RC-04', 'RC-07', 'RC-12'].map(c => (
                <span key={c} style={{ fontFamily: 'var(--mono)', fontSize: 10, padding: '3px 8px', borderRadius: 999, background: 'var(--bone-deep)' }}>{c}</span>
              ))}
            </div>
          </div>
        </Card>

        {/* 8. İzlenebilirlik Zaman Çizelgesi */}
        <Card num="8" title="İzlenebilirlik Zaman Çizelgesi" footer="Tüm Zaman Çizelgesi →">
          <div style={{ position: 'relative', paddingLeft: 18 }}>
            <div style={{ position: 'absolute', left: 6, top: 6, bottom: 6, width: 1, background: 'var(--hairline-strong)' }} />
            {[
              ['14 May 2025 10:00', 'Pasaport oluşturuldu.'],
              ['14 May 2025 10:15', 'Rota hesaplandı.'],
              ['14 May 2025 10:30', 'Finansal analiz tamamlandı.'],
              ['14 May 2025 10:45', 'Pasaport doğrulandı.'],
            ].map((row, i) => (
              <motion.div key={i}
                initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}
                style={{ position: 'relative', marginBottom: 12, paddingLeft: 8 }}>
                <span style={{ position: 'absolute', left: -16, top: 4, width: 9, height: 9, borderRadius: '50%', background: i === 3 ? 'var(--tuff)' : 'var(--ink)', border: '2px solid var(--bone)' }} />
                <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.1em', color: 'var(--ink-faded)' }}>{row[0]}</div>
                <div style={{ fontSize: 12, fontWeight: 500 }}>{row[1]}</div>
              </motion.div>
            ))}
          </div>
        </Card>
      </section>

      {/* === ÖNİZLEME + META === */}
      <section className="panel" style={{ overflow: 'hidden' }}>
        <div style={{ display: 'flex', borderBottom: '1px solid var(--hairline)' }}>
          {([
            ['preview', 'Pasaport Önizleme'],
            ['pdf', 'PDF Çıktısı'],
            ['shares', 'Paylaşım Geçmişi'],
            ['versions', 'Sürüm Geçmişi'],
          ] as [Tab, string][]).map(([k, label]) => (
            <button key={k} onClick={() => setTab(k)} style={{
              background: 'transparent', border: 'none', cursor: 'pointer',
              padding: '14px 22px', fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.14em', textTransform: 'uppercase',
              color: tab === k ? 'var(--ink)' : 'var(--ink-faded)',
              borderBottom: tab === k ? '2px solid var(--tuff)' : '2px solid transparent',
              fontWeight: tab === k ? 600 : 500, marginBottom: -1,
            }}>
              {label}
            </button>
          ))}
        </div>
        <div style={{ padding: 28, display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 22 }}>
          {/* Doc preview */}
          <div style={{ background: 'var(--bone-deep)', borderRadius: 4, padding: 24, border: '1px solid var(--hairline)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--hairline-strong)', paddingBottom: 14 }}>
              <div className="brand">
                <span className="brand-mark" />
                <span className="brand-name" style={{ fontSize: 18 }}>raw<em>2</em>value</span>
              </div>
              <div style={{ textAlign: 'center' }}>
                <h3 style={{ fontFamily: 'var(--display)', fontSize: 18, margin: 0, fontWeight: 500, letterSpacing: '0.05em' }}>RAW MATERIAL PASSPORT</h3>
                <div className="numerals" style={{ fontSize: 11, color: 'var(--ink-faded)', marginTop: 2 }}>{passportId}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '4px 10px', borderRadius: 999, background: 'rgba(107,142,90,0.16)', color: 'var(--co2-green)', fontFamily: 'var(--mono)', fontSize: 10 }}>
                  🛡 DOĞRULANMIŞ
                </div>
              </div>
            </div>

            <div style={{ marginTop: 22, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
              <div>
                <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 8 }}>ÖZET</div>
                {[
                  ['Hammadde', last ? fmt.matName(last.request.raw_material) : 'Bakır Cevheri'],
                  ['Kaynak', 'Antofagasta, Şili'],
                  ['Seçilen Rota', last ? fmt.routeShort(last.response.recommended_route) : 'Rota-3 (Düşük Karbon)'],
                  ['İşleyici', 'GreenMet Processing Ltd.'],
                ].map(([k, v]) => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: 12 }}>
                    <span style={{ color: 'var(--ink-faded)' }}>{k}</span>
                    <span style={{ fontWeight: 500 }}>{v}</span>
                  </div>
                ))}
              </div>
              <div>
                <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 8 }}>FİNANS & ÇEVRE</div>
                {[
                  ['Toplam CO₂e', `${fmt.num(co2PerTon, 0)} kg / ton`],
                  ['Beklenen Brüt Kâr', '74,20 USD / ton'],
                  ['Değer Artışı', fmt.pct(valid, 1)],
                  ['AI Skoru', `${score} / 100`],
                ].map(([k, v]) => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: 12 }}>
                    <span style={{ color: 'var(--ink-faded)' }}>{k}</span>
                    <span style={{ fontWeight: 500 }}>{v}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ marginTop: 22, padding: 18, background: 'var(--paper)', borderRadius: 4 }}>
              <FakeMap />
            </div>
          </div>

          {/* Meta verileri */}
          <div>
            <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 14 }}>Pasaport Meta Verileri</div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <tbody>
                {[
                  ['Pasaport ID', passportId],
                  ['Oluşturulma Tarihi', '14 May 2025 10:45'],
                  ['Son Güncelleme', '14 May 2025 10:45'],
                  ['Oluşturan', 'Ahmet Yılmaz (Raw2Value AI)'],
                  ['Durum', 'Geçerli'],
                  ['Geçerlilik Süresi', '31 Aug 2025'],
                  ['Bağlı Teklif', 'OFF-1567'],
                  ['Versiyon', 'v1.0'],
                  ['Doğrulama Hash', 'a1b2c3d4e5f6...9a0b'],
                  ['Doğrulama Linki', 'https://raw2value.ai/verify/rmp-2025-000124 ↻'],
                ].map(([k, v]) => (
                  <tr key={k} style={{ borderBottom: '1px dashed var(--hairline)' }}>
                    <td style={{ padding: '8px 0', color: 'var(--ink-faded)', fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.06em' }}>{k}</td>
                    <td style={{ padding: '8px 0', textAlign: 'right', fontWeight: 500, fontFamily: 'var(--mono)', fontSize: 11 }}>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}

function Card({ num, title, children, footer }: { num: string; title: string; children: React.ReactNode; footer?: string }) {
  return (
    <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--hairline)', display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ width: 24, height: 24, borderRadius: '50%', background: 'var(--tuff)', color: 'var(--bone)', display: 'grid', placeItems: 'center', fontFamily: 'var(--display)', fontSize: 11, fontWeight: 500 }}>{num}</span>
        <span style={{ fontFamily: 'var(--display)', fontSize: 14, fontWeight: 500 }}>{title}</span>
      </div>
      <div style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {children}
      </div>
      {footer && (
        <div style={{ padding: '10px 18px', borderTop: '1px solid var(--hairline)', textAlign: 'right' }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.1em', color: 'var(--ink-faded)', textTransform: 'uppercase', cursor: 'pointer' }}>{footer}</span>
        </div>
      )}
    </div>
  );
}

function Mini({ icon, label, v, highlight }: { icon?: string; label: string; v: string; highlight?: boolean }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, padding: '4px 0' }}>
      {icon && <span style={{ fontSize: 12, color: 'var(--ink-faded)', width: 18 }}>{icon}</span>}
      <div style={{ flex: 1 }}>
        <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>{label}</div>
        <div style={{ fontSize: 12, fontWeight: 500, marginTop: 2, color: highlight ? 'var(--tuff)' : 'var(--ink)', fontStyle: highlight ? 'italic' : 'normal', fontFamily: highlight ? 'var(--display)' : 'inherit' }}>{v}</div>
      </div>
    </div>
  );
}

function FakeQR({ size = 80 }: { size?: number }) {
  // Stilize QR — pseudo-random kareler
  return (
    <svg width={size} height={size} viewBox="0 0 21 21" style={{ background: 'var(--bone)', border: '1px solid var(--hairline)', borderRadius: 3 }}>
      {Array.from({ length: 21 * 21 }).map((_, i) => {
        const x = i % 21, y = Math.floor(i / 21);
        const corner = (x < 7 && y < 7) || (x > 13 && y < 7) || (x < 7 && y > 13);
        const innerCorner = ((x === 1 || x === 5) && y < 6 && y > 0) || ((x === 0 || x === 6) && y < 7) ||
                            ((x > 13 && (x === 15 || x === 19)) && y < 6 && y > 0) || ((x === 14 || x === 20) && y < 7) ||
                            ((x === 1 || x === 5) && y > 14 && y < 20) || ((x === 0 || x === 6) && y > 13);
        if (corner && !innerCorner && !((x > 1 && x < 5 && y > 1 && y < 5) || (x > 15 && x < 19 && y > 1 && y < 5) || (x > 1 && x < 5 && y > 15 && y < 19))) return null;
        const seed = (x * 3 + y * 7 + x * y) % 5;
        const fill = (corner && innerCorner) || (!corner && seed < 2);
        return fill ? <rect key={i} x={x} y={y} width="1" height="1" fill="#1B2A3A" /> : null;
      })}
      {/* corner squares */}
      {[[0,0],[14,0],[0,14]].map(([cx, cy]) => (
        <g key={`${cx}${cy}`}>
          <rect x={cx} y={cy} width="7" height="7" fill="#1B2A3A" />
          <rect x={cx + 1} y={cy + 1} width="5" height="5" fill="var(--bone)" />
          <rect x={cx + 2} y={cy + 2} width="3" height="3" fill="#1B2A3A" />
        </g>
      ))}
    </svg>
  );
}

function RouteSteps() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 4 }}>
      {['Maden', 'İşleme', 'Rafineri', 'Lojistik'].map((s, i) => (
        <div key={s} style={{ textAlign: 'center' }}>
          <div style={{ width: 26, height: 26, borderRadius: '50%', background: i < 3 ? 'var(--tuff)' : 'var(--bone-deep)', color: i < 3 ? 'var(--bone)' : 'var(--ink-faded)', margin: '0 auto', display: 'grid', placeItems: 'center', fontFamily: 'var(--display)', fontSize: 11 }}>{i + 1}</div>
          <div style={{ fontSize: 9, fontFamily: 'var(--mono)', letterSpacing: '0.06em', color: 'var(--ink-faded)', marginTop: 4 }}>{s}</div>
        </div>
      ))}
    </div>
  );
}

function FakeMap({ small }: { small?: boolean }) {
  const h = small ? 80 : 160;
  return (
    <svg viewBox="0 0 200 100" style={{ width: '100%', height: h, background: 'var(--bone-deep)', borderRadius: 3 }}>
      <path d="M 30 80 C 50 70, 90 75, 110 60 C 130 50, 160 55, 180 40" fill="none" stroke="#C8553D" strokeWidth="0.8" strokeDasharray="2 1.5" />
      {[
        [30, 80], [80, 65], [110, 60], [150, 50], [180, 40],
      ].map(([x, y], i) => (
        <g key={i}>
          <circle cx={x} cy={y} r="3" fill={i === 0 || i === 4 ? '#C8553D' : '#1B2A3A'} />
          <circle cx={x} cy={y} r="6" fill="none" stroke={i === 0 || i === 4 ? '#C8553D' : '#1B2A3A'} strokeWidth="0.4" opacity="0.5" />
        </g>
      ))}
    </svg>
  );
}
