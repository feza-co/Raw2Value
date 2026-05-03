import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { fmt } from '../lib/format';
import { external } from '../lib/external';
import { useStore } from '../lib/store';
import { PageHeader } from '../components/PageHeader';
import { ConfidenceGauge } from '../components/Gauges';
import { RouteMap } from '../components/RouteMap';

export function AIDecisionCockpitPage() {
  const nav = useNavigate();
  const { last } = useStore();
  const fx = useQuery({ queryKey: ['fx'], queryFn: api.fxCurrent });
  const country = useQuery({
    queryKey: ['country', last?.request.target_country],
    queryFn: () => external.country(last!.request.target_country),
    enabled: !!last,
    retry: 0,
  });

  if (!last) {
    return (
      <div>
        <PageHeader title="AI Decision Cockpit" subtitle="Model tabanlı karar ve öneri paneli" breadcrumbs={[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Hızlı Analiz' }, { label: 'AI Decision Cockpit' }]} />
        <div className="empty" style={{ padding: 80 }}>
          Önce <em>Material Analyzer</em>'dan bir analiz çalıştırın.<br/>
          <button className="btn btn-primary btn-arrow" style={{ marginTop: 22 }} onClick={() => nav('/analyzer')}>Analyzer'a Git</button>
        </div>
      </div>
    );
  }

  const r = last.response;
  const req = last.request;
  const score = Math.round(r.confidence.overall);
  const reasons = r.reason_codes.slice(0, 5);
  const co2PerTon = r.co2_kg / Math.max(req.tonnage, 1);

  return (
    <div>
      <PageHeader
        title="AI Decision Cockpit"
        subtitle="Model tabanlı karar ve öneri paneli"
        breadcrumbs={[{ label: 'Dashboard', to: '/dashboard' }, { label: 'Hızlı Analiz' }, { label: 'AI Decision Cockpit' }]}
      />

      {/* === GİRDİ ÖZETİ === */}
      <section className="panel" style={{ padding: '14px 22px', marginBottom: 20, display: 'flex', flexWrap: 'wrap', gap: 28, alignItems: 'center' }}>
        {[
          { icon: '⚙', label: 'Hammadde',  v: fmt.matName(req.raw_material) },
          { icon: '◉', label: 'Kaynak',    v: req.origin_city },
          { icon: '⊟', label: 'Tonaj',     v: `${fmt.num(req.tonnage)} ton` },
          { icon: '◆', label: 'Kalite',    v: fmt.qualityLabel(req.quality) },
          { icon: '⚐', label: 'Hedef Pazar', v: fmt.countryName(req.target_country) },
          { icon: '⛟', label: 'Taşıma Modu', v: fmt.transportLabel(req.transport_mode) },
        ].map((c, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 18, color: 'var(--ink-faded)' }}>{c.icon}</span>
            <div>
              <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>{c.label}</div>
              <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 14 }}>{c.v}</div>
            </div>
          </div>
        ))}
      </section>

      {/* === ANA KARAR + KPI === */}
      <section style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 18, marginBottom: 20 }}>
        <div className="panel" style={{ padding: 28, position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, right: 0, width: 200, height: 200, background: 'radial-gradient(circle, rgba(200,85,61,0.10), transparent 70%)', pointerEvents: 'none' }} />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
            <div>
              <span className="eyebrow tuff with-rule">★ Önerilen Rota</span>
              <h2 style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 32, margin: '8px 0 0', letterSpacing: '-0.02em' }}>
                <em className="tuff-em">{fmt.routeShort(r.recommended_route)}</em>
              </h2>
            </div>
            <span className="numerals" style={{ fontSize: 10, color: 'var(--ink-faded)', letterSpacing: '0.14em', textTransform: 'uppercase' }}>
              {r.duration_ms}ms · req {r.request_id.slice(0, 12)}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr 1fr 1fr 1fr', gap: 28, alignItems: 'center', paddingTop: 14, borderTop: '1px solid var(--hairline)' }}>
            <ConfidenceGauge value={score} size={140} label="AI Skoru" />

            <Stat label="Güven Skoru" value={`%${Math.round(r.confidence.model_confidence)}`} />
            <Stat label="Tahmini Kâr" value={fmt.try(r.expected_profit_try)} sub={`/ ${fmt.num(req.tonnage)} ton`} highlight />
            <Stat label="Değer Artışı" value={fmt.pct(r.value_uplift_pct, 0)} sub="vs. ham satış" />
            <Stat label="Teslim Süresi" value="5–7 gün" sub="Tahmini" />
          </div>

          <div style={{ marginTop: 22, paddingTop: 16, borderTop: '1px dashed var(--hairline-strong)' }}>
            <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)', marginBottom: 8 }}>Öneri Nedenleri</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {reasons.map((rc, i) => (
                <span key={i} style={{
                  fontFamily: 'var(--mono)', fontSize: 10, padding: '4px 10px',
                  background: i === 0 ? 'var(--tuff)' : 'var(--bone-deep)',
                  color: i === 0 ? 'var(--bone)' : 'var(--ink)',
                  borderRadius: 999, letterSpacing: '0.06em',
                }}>{rc.feature}</span>
              ))}
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <KCard icon="€" label="Canlı Kur" main={`${fx.data?.usd_try.toFixed(2) ?? '—'}`} sub={`Günlük Değişim · ${fx.data ? '+%0,45' : '—'}`} note="₺ / TRY" />
          <KCard icon="☁" label="CO₂ (Tahmini)" main={`${fmt.num(co2PerTon, 0)}`} sub="kg CO₂ / ton" note={`alt. ortalamasından %6 az`} />
          <KCard icon="◉" label="Toplam Mesafe" main={`${fmt.num(1132, 0)}`} sub="km" note="(~ ${fmt.num(req.tonnage)} t lojistik)" />
          <KCard icon="🏭" label="En Yakın İşleyici" main="128" sub="km" note="Nevşehir Organize Sanayi" />
        </div>
      </section>

      {/* === ALTERNATİFLER + ESLEŞMELER === */}
      <section style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 18, marginBottom: 20 }}>
        <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '18px 22px', borderBottom: '1px solid var(--hairline)' }}>
            <span className="eyebrow">Alternatif Rotaların Karşılaştırması</span>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ background: 'var(--bone-deep)' }}>
                {['Rota', 'Kâr (₺/100 ton)', 'Değer Artışı', 'CO₂ (kg/ton)', 'Teslim (gün)', 'AI Skoru', 'Risk', 'Seç'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '10px 14px', fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--ink-faded)', fontWeight: 500 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {r.route_alternatives.map((alt, i) => {
                const isBest = alt.route === r.recommended_route;
                const score = Math.round(alt.route_probability * 100);
                const risk = score > 80 ? 'Düşük' : score > 50 ? 'Orta' : 'Yüksek';
                const riskColor = score > 80 ? 'var(--co2-green)' : score > 50 ? 'var(--co2-amber)' : 'var(--co2-red)';
                return (
                  <tr key={alt.route} style={{ borderTop: '1px solid var(--hairline)', background: isBest ? 'rgba(200,85,61,0.06)' : 'transparent' }}>
                    <td style={{ padding: '14px', fontFamily: 'var(--display)', fontWeight: 500, fontSize: 14, color: isBest ? 'var(--tuff)' : 'var(--ink)' }}>
                      {isBest && <span style={{ marginRight: 6, fontStyle: 'italic' }}>★ Önerilen</span>}
                      {fmt.routeShort(alt.route)}
                    </td>
                    <td style={{ padding: '14px' }} className="numerals">{fmt.try(alt.predicted_profit_try / Math.max(req.tonnage, 1) * 100)}</td>
                    <td style={{ padding: '14px', color: alt.value_uplift_pct >= 0 ? 'var(--co2-green)' : 'var(--co2-red)' }} className="numerals">{fmt.pct(alt.value_uplift_pct, 0)}</td>
                    <td style={{ padding: '14px' }} className="numerals">{fmt.num(alt.co2_kg / Math.max(req.tonnage, 1), 0)}</td>
                    <td style={{ padding: '14px' }} className="numerals">{i === 0 ? '5–7' : i === 1 ? '3–4' : '6–9'}</td>
                    <td style={{ padding: '14px' }}>
                      <span style={{ fontFamily: 'var(--display)', fontWeight: 600, fontSize: 13, color: isBest ? 'var(--tuff)' : 'var(--ink)' }}>{score}</span>
                    </td>
                    <td style={{ padding: '14px' }}>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: 'var(--mono)', fontSize: 10, color: riskColor }}>
                        <span style={{ width: 6, height: 6, borderRadius: '50%', background: riskColor }} /> {risk}
                      </span>
                    </td>
                    <td style={{ padding: '14px' }}>
                      <input type="radio" name="route" defaultChecked={isBest} style={{ accentColor: 'var(--tuff)' }} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <div style={{ padding: '12px 22px', fontSize: 10, color: 'var(--ink-faded)', fontStyle: 'italic', borderTop: '1px solid var(--hairline)' }}>
            * Tüm değerler tonaj × birim hesabıyla projeksiyon olarak gösterilir.
          </div>
        </div>

        <div className="panel" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '18px 22px', borderBottom: '1px solid var(--hairline)' }}>
            <span className="eyebrow">İşleyici (Alıcı) Eşleşme Sıralaması</span>
          </div>
          <div style={{ padding: '6px 0' }}>
            {r.match_results.slice(0, 5).map((mr, i) => (
              <motion.div key={i}
                initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                style={{
                  display: 'grid', gridTemplateColumns: 'auto 1fr auto auto', gap: 14, alignItems: 'center',
                  padding: '14px 22px', borderTop: i === 0 ? 'none' : '1px solid var(--hairline)',
                }}>
                <div className="numerals" style={{ fontFamily: 'var(--display)', fontStyle: 'italic', fontSize: 22, fontWeight: 500, color: 'var(--tuff)', minWidth: 28 }}>
                  {i + 1}
                </div>
                <div>
                  <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 14 }}>{mr.processor_name}</div>
                  <div style={{ fontSize: 11, color: 'var(--ink-faded)' }}>→ {mr.buyer_name}</div>
                </div>
                <div className="numerals" style={{ fontSize: 11, color: 'var(--ink-faded)', whiteSpace: 'nowrap' }}>
                  {Math.round(120 + i * 86)} km
                </div>
                <div style={{ fontFamily: 'var(--display)', fontWeight: 600, fontSize: 14, color: 'var(--ink)' }}>
                  %{Math.round(mr.score * 100)}
                </div>
              </motion.div>
            ))}
          </div>
          <div style={{ padding: '12px 22px', borderTop: '1px solid var(--hairline)', textAlign: 'right' }}>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-faded)', cursor: 'pointer' }}>Tümünü Gör →</span>
          </div>
        </div>
      </section>

      {/* === HARITA + AKSIYONLAR === */}
      <section style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 18, marginBottom: 20 }}>
        <div className="panel" style={{ padding: 22 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
            <span className="eyebrow">Rota Önizleme · Harita</span>
            {country.data && (
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-faded)' }}>
                <span style={{ fontSize: 14 }}>{country.data.flag}</span> {country.data.name?.common} · {country.data.capital?.[0]}
              </span>
            )}
          </div>
          <RouteMap originCity={req.origin_city} targetCountry={req.target_country} targetCity={req.target_city || undefined} transportMode={req.transport_mode} height={300} />
        </div>

        <div className="panel" style={{ padding: 22 }}>
          <span className="eyebrow">Sonraki Aksiyonlar</span>
          <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 10 }}>
            <ActionRow icon="◇" title="Teklif Oluştur" desc="Seçilen rota için teklif oluştur." onClick={() => nav('/offer')} />
            <ActionRow icon="◉" title="Haritada Gör"   desc="Detaylı rota ve mesafe analizini haritada görüntüle." onClick={() => nav('/geo')} />
            <ActionRow icon="≋" title="What-If Simülasyonu" desc="Farklı senaryoları test et ve sonuçları karşılaştır." onClick={() => nav('/whatif')} />
            <ActionRow icon="✦" title="Pasaport Oluştur" desc="Raw Material Passport oluştur ve çıktısını al." onClick={() => nav('/passport')} />
          </div>
        </div>
      </section>

      {/* === AÇIKLAMA + FEATURE IMPORTANCE === */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: 18 }}>
        <div className="panel" style={{ padding: 22 }}>
          <span className="eyebrow">Öneri Açıklaması</span>
          <p style={{ fontSize: 12, color: 'var(--ink-faded)', marginTop: 8, fontStyle: 'italic' }}>
            AI modelinizin girdiklerinize göre "<strong>{fmt.routeShort(r.recommended_route)}</strong>" rotasını en yüksek değer üreten seçenek olarak belirledi.
          </p>
          <ol style={{ paddingLeft: 0, listStyle: 'none', marginTop: 14, display: 'flex', flexDirection: 'column', gap: 10 }}>
            {reasons.map((rc, i) => (
              <li key={i} style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 12, padding: '8px 0', borderBottom: i === reasons.length - 1 ? 'none' : '1px dashed var(--hairline)' }}>
                <span style={{
                  width: 28, height: 28, borderRadius: '50%',
                  background: 'var(--tuff)', color: 'var(--bone)',
                  display: 'grid', placeItems: 'center', flexShrink: 0,
                  fontFamily: 'var(--display)', fontSize: 13, fontWeight: 500,
                }}>{i + 1}</span>
                <div>
                  <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 13 }}>{rc.feature}</div>
                  <div style={{ fontSize: 11, color: 'var(--ink-soft)', marginTop: 2, fontStyle: 'italic' }}>{rc.text}</div>
                </div>
              </li>
            ))}
          </ol>
        </div>

        <div className="panel" style={{ padding: 22 }}>
          <span className="eyebrow">Karar Etkileyen Faktörler</span>
          <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 8 }}>
            {r.feature_importance.slice(0, 8).map((fi, i) => {
              const max = r.feature_importance[0]!.importance;
              const w = (fi.importance / max) * 100;
              return (
                <div key={fi.feature}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 4 }}>
                    <span>{fi.feature}</span>
                    <span className="numerals" style={{ color: 'var(--ink-faded)' }}>{Math.round(fi.importance)}%</span>
                  </div>
                  <div style={{ height: 6, background: 'var(--bone-deep)' }}>
                    <motion.div initial={{ width: 0 }} animate={{ width: `${w}%` }} transition={{ duration: 0.9, delay: i * 0.04 }}
                      style={{ height: '100%', background: i < 3 ? 'var(--tuff)' : 'var(--ink)' }} />
                  </div>
                </div>
              );
            })}
          </div>
          <div style={{ marginTop: 12, fontSize: 10, color: 'var(--ink-faded)', fontStyle: 'italic', textAlign: 'right' }}>Toplam %100</div>
        </div>
      </section>
    </div>
  );
}

function Stat({ label, value, sub, highlight }: { label: string; value: string; sub?: string; highlight?: boolean }) {
  return (
    <div>
      <div className="numerals" style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>{label}</div>
      <div style={{ fontFamily: 'var(--display)', fontSize: 26, fontWeight: 500, marginTop: 4, lineHeight: 1, color: highlight ? 'var(--tuff)' : 'var(--ink)' }}>{value}</div>
      {sub && <div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-faded)', marginTop: 4, letterSpacing: '0.06em' }}>{sub}</div>}
    </div>
  );
}

function KCard({ icon, label, main, sub, note }: { icon: string; label: string; main: string; sub?: string; note?: string }) {
  return (
    <div className="panel" style={{ padding: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
        <div style={{ width: 32, height: 32, borderRadius: 4, background: 'var(--bone-deep)', display: 'grid', placeItems: 'center', fontSize: 16 }}>{icon}</div>
        <span className="numerals" style={{ fontSize: 9, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--ink-faded)' }}>{label}</span>
      </div>
      <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 24, lineHeight: 1, letterSpacing: '-0.02em' }}>{main}</div>
      {sub && <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-faded)', marginTop: 4 }}>{sub}</div>}
      {note && <div style={{ fontSize: 10, color: 'var(--ink-soft)', marginTop: 4, fontStyle: 'italic' }}>{note}</div>}
    </div>
  );
}

function ActionRow({ icon, title, desc, onClick }: { icon: string; title: string; desc: string; onClick: () => void }) {
  return (
    <button onClick={onClick} style={{
      background: 'transparent', border: '1px solid var(--hairline)', borderRadius: 4,
      padding: '12px 14px', display: 'grid', gridTemplateColumns: 'auto 1fr auto', gap: 12, alignItems: 'center',
      textAlign: 'left', cursor: 'pointer', transition: 'all 200ms ease', color: 'var(--ink)',
    }}
      onMouseEnter={e => { e.currentTarget.style.background = 'var(--bone-deep)'; e.currentTarget.style.borderColor = 'var(--tuff)'; }}
      onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = 'var(--hairline)'; }}>
      <span style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--bone-deep)', display: 'grid', placeItems: 'center', fontSize: 14 }}>{icon}</span>
      <div>
        <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 13 }}>{title}</div>
        <div style={{ fontSize: 10, color: 'var(--ink-faded)' }}>{desc}</div>
      </div>
      <span style={{ color: 'var(--ink-faded)', fontFamily: 'var(--display)' }}>›</span>
    </button>
  );
}
