import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <div className="min-h-screen bg-r2v-base text-r2v-ink antialiased font-sans">
      {/* Top meta bar */}
      <div className="border-b border-r2v-line bg-r2v-base">
        <div className="max-w-[1440px] mx-auto px-6 md:px-10 h-9 flex items-center justify-between text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted">
          <span>TR71 / Kapadokya</span>
          <span className="hidden md:inline">Hackathon 2026 — Kategori 03 — Akıllı Tedarik Zinciri</span>
          <span>v0.4.0</span>
        </div>
      </div>

      {/* Navbar */}
      <header
        className={`sticky top-0 z-50 bg-r2v-base/90 backdrop-blur-sm transition-shadow ${
          scrolled ? 'border-b border-r2v-line shadow-[0_1px_0_0_rgba(0,0,0,0.04)]' : 'border-b border-transparent'
        }`}
      >
        <div className="max-w-[1440px] mx-auto px-6 md:px-10 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-7 h-7 bg-r2v-ink flex items-center justify-center">
              <div className="w-3 h-3 bg-r2v-terracotta" />
            </div>
            <span className="text-[15px] font-semibold tracking-tight">Raw2Value</span>
            <span className="hidden md:inline text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted ml-2">
              Decision Engine
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm">
            <a href="#models" className="text-r2v-ink/70 hover:text-r2v-ink transition-colors">Modeller</a>
            <a href="#evidence" className="text-r2v-ink/70 hover:text-r2v-ink transition-colors">Kanıtlar</a>
            <a href="#pipeline" className="text-r2v-ink/70 hover:text-r2v-ink transition-colors">Pipeline</a>
            <a href="#pilot" className="text-r2v-ink/70 hover:text-r2v-ink transition-colors">Pilot</a>
          </nav>

          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 bg-r2v-ink text-r2v-base px-4 py-2 text-sm font-medium hover:bg-r2v-terracotta transition-colors"
          >
            Sisteme Giriş
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M13 5l7 7-7 7" strokeLinecap="square" strokeLinejoin="miter" />
            </svg>
          </Link>
        </div>
      </header>

      <main>
        {/* HERO — Swiss grid */}
        <section className="border-b border-r2v-line">
          <div className="max-w-[1440px] mx-auto px-6 md:px-10 pt-20 md:pt-28 pb-16 md:pb-24">
            <div className="grid grid-cols-12 gap-x-6 md:gap-x-8">
              <div className="col-span-12 md:col-span-2 mb-10 md:mb-0">
                <div className="text-[11px] font-mono uppercase tracking-[0.2em] text-r2v-muted">
                  01 — Manifesto
                </div>
              </div>

              <div className="col-span-12 md:col-span-10">
                <h1 className="text-[clamp(3rem,9vw,9.5rem)] leading-[0.92] font-medium tracking-tightest text-r2v-ink">
                  Don't sell <br />
                  the rock.<br />
                  <span className="text-r2v-terracotta">Sell the value.</span>
                </h1>

                <div className="mt-12 grid grid-cols-12 gap-x-6 md:gap-x-8">
                  <div className="col-span-12 md:col-span-6">
                    <p className="text-base md:text-lg leading-relaxed text-r2v-ink/80 max-w-xl">
                      Kapadokya'nın üç hammaddesini — pomza, perlit, kabak çekirdeği —
                      işleyip ihraç etmek için en kârlı rotayı, beklenen kârı (TRY),
                      CO₂ maliyetini ve alıcı eşleşmesini öneren makine öğrenmesi
                      tabanlı karar motoru.
                    </p>
                  </div>
                  <div className="col-span-12 md:col-span-4 md:col-start-9 mt-8 md:mt-0">
                    <div className="flex flex-col gap-4">
                      <Link
                        to="/dashboard"
                        className="inline-flex items-center justify-between bg-r2v-ink text-r2v-base px-5 py-4 text-sm font-medium hover:bg-r2v-terracotta transition-colors"
                      >
                        <span>Karar Motorunu Aç</span>
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M5 12h14M13 5l7 7-7 7" strokeLinecap="square" />
                        </svg>
                      </Link>
                      <a
                        href="#evidence"
                        className="inline-flex items-center justify-between border border-r2v-ink text-r2v-ink px-5 py-4 text-sm font-medium hover:bg-r2v-ink hover:text-r2v-base transition-colors"
                      >
                        <span>Model Kanıtları</span>
                        <span className="font-mono text-xs">↓</span>
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* KPI strip */}
          <div className="border-t border-r2v-line bg-r2v-surface">
            <div className="max-w-[1440px] mx-auto px-6 md:px-10 grid grid-cols-2 md:grid-cols-4 divide-x divide-r2v-line">
              {[
                { k: '1.500', l: 'Eğitim Senaryosu', s: '120 gerçek + augmented' },
                { k: 'R² 0.84', l: 'Profit Modeli', s: 'CatBoost holdout' },
                { k: 'F1 0.78', l: 'Route Sınıflandırıcı', s: 'macro-F1' },
                { k: '88', l: 'Test', s: 'pytest passing' },
              ].map((m, i) => (
                <div key={i} className="px-5 py-8 first:pl-0 md:px-8">
                  <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted mb-3">
                    0{i + 1} — {m.l}
                  </div>
                  <div className="text-3xl md:text-4xl font-medium tracking-tight text-r2v-ink">{m.k}</div>
                  <div className="mt-2 text-xs text-r2v-muted">{m.s}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* MODELS — 3 columns */}
        <section id="models" className="border-b border-r2v-line">
          <div className="max-w-[1440px] mx-auto px-6 md:px-10 py-20 md:py-28">
            <div className="grid grid-cols-12 gap-x-6 md:gap-x-8 mb-16">
              <div className="col-span-12 md:col-span-2">
                <div className="text-[11px] font-mono uppercase tracking-[0.2em] text-r2v-muted">
                  02 — Modeller
                </div>
              </div>
              <div className="col-span-12 md:col-span-10">
                <h2 className="text-4xl md:text-6xl leading-[1.02] font-medium tracking-tightest max-w-3xl">
                  Bir ilan platformu değil.<br />
                  <span className="text-r2v-muted">Bir karar motoru.</span>
                </h2>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 border-t border-r2v-line">
              {[
                {
                  n: '01',
                  t: 'Value Uplift',
                  s: 'CatBoostRegressor',
                  d: 'Hammadde ve işleme rotasına göre beklenen değer artışı ve net kârı (TRY) tahmin eder. RMSE 11.2M.',
                  m: '39 feature · target=expected_profit_try',
                },
                {
                  n: '02',
                  t: 'Route Recommendation',
                  s: 'CatBoostClassifier',
                  d: 'Pomza, perlit ve kabak çekirdeği için ham satışa karşı katma değerli alternatifler arasından en uygun işleme rotasını seçer.',
                  m: '10 trained class · macro-F1 0.78',
                },
                {
                  n: '03',
                  t: 'Buyer Match',
                  s: 'Deterministic scorer',
                  d: 'Lojistik mesafe, kapasite ve kaliteyi optimize ederek en kârlı Üretici–İşleyici–Alıcı kombinasyonunu sıralar.',
                  m: '6 component · 3 ağırlık profili',
                },
              ].map((c, i) => (
                <div
                  key={i}
                  className={`p-8 md:p-10 border-r2v-line ${
                    i < 2 ? 'border-b md:border-b-0 md:border-r' : ''
                  }`}
                >
                  <div className="flex items-baseline justify-between mb-8">
                    <span className="text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted">
                      Model {c.n}
                    </span>
                    <span className="text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-terracotta">
                      {c.s}
                    </span>
                  </div>
                  <h3 className="text-2xl md:text-3xl font-medium tracking-tight mb-4">{c.t}</h3>
                  <p className="text-sm leading-relaxed text-r2v-ink/75 mb-8">{c.d}</p>
                  <div className="pt-6 border-t border-r2v-line text-[11px] font-mono uppercase tracking-[0.16em] text-r2v-muted">
                    {c.m}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* PIPELINE — vertical sequence */}
        <section id="pipeline" className="border-b border-r2v-line bg-r2v-surface">
          <div className="max-w-[1440px] mx-auto px-6 md:px-10 py-20 md:py-28">
            <div className="grid grid-cols-12 gap-x-6 md:gap-x-8 mb-16">
              <div className="col-span-12 md:col-span-2">
                <div className="text-[11px] font-mono uppercase tracking-[0.2em] text-r2v-muted">
                  03 — Pipeline
                </div>
              </div>
              <div className="col-span-12 md:col-span-10">
                <h2 className="text-4xl md:text-6xl leading-[1.02] font-medium tracking-tightest max-w-3xl">
                  Excel'den karar çıktısına<br />
                  <span className="text-r2v-muted">tek yönlü veri akışı.</span>
                </h2>
              </div>
            </div>

            <div className="grid grid-cols-12 gap-x-6 md:gap-x-8">
              <div className="hidden md:block md:col-span-2" />
              <div className="col-span-12 md:col-span-10">
                <div className="border-t border-r2v-ink">
                  {[
                    { n: '01', t: 'Master', s: 'data/master/raw2value_v4.xlsx', d: '16 sheet · single source of truth' },
                    { n: '02', t: 'ETL', s: 'ml/src/etl.py', d: 'Excel → 12 parquet + distance lookup' },
                    { n: '03', t: 'Augmentation', s: 'ml/src/augmentation.py', d: '120 → 1.500 satır · seed=42' },
                    { n: '04', t: 'Training', s: 'ml/src/{train_profit,train_route}.py', d: 'CatBoost native categorical' },
                    { n: '05', t: 'Inference', s: 'raw2value_ml/inference.py', d: 'analyze() — backend tek giriş noktası' },
                  ].map((s, i) => (
                    <div
                      key={i}
                      className="grid grid-cols-12 gap-x-6 py-6 border-b border-r2v-line items-baseline"
                    >
                      <div className="col-span-2 md:col-span-1 text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted">
                        {s.n}
                      </div>
                      <div className="col-span-10 md:col-span-3 text-lg md:text-xl font-medium tracking-tight">
                        {s.t}
                      </div>
                      <div className="col-span-12 md:col-span-4 mt-2 md:mt-0 font-mono text-xs text-r2v-terracotta break-all">
                        {s.s}
                      </div>
                      <div className="col-span-12 md:col-span-4 mt-2 md:mt-0 text-sm text-r2v-ink/75">
                        {s.d}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* EVIDENCE — proof grid */}
        <section id="evidence" className="border-b border-r2v-line">
          <div className="max-w-[1440px] mx-auto px-6 md:px-10 py-20 md:py-28">
            <div className="grid grid-cols-12 gap-x-6 md:gap-x-8 mb-16">
              <div className="col-span-12 md:col-span-2">
                <div className="text-[11px] font-mono uppercase tracking-[0.2em] text-r2v-muted">
                  04 — Kanıt
                </div>
              </div>
              <div className="col-span-12 md:col-span-10">
                <h2 className="text-4xl md:text-6xl leading-[1.02] font-medium tracking-tightest max-w-3xl">
                  Şeffaf metrik.<br />
                  <span className="text-r2v-muted">Reproducible sonuç.</span>
                </h2>
                <p className="mt-6 text-base md:text-lg text-r2v-ink/75 max-w-2xl">
                  Hackathon projesinde güven, açıklanabilir kanıttan gelir.
                  Random seed 42 ile her sonuç tekrar üretilebilir, ablation
                  çalışmaları kuralların load-bearing olduğunu gösterir.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 border-t border-l border-r2v-line">
              {[
                { t: 'Feature Importance', d: 'CatBoost feature importance + SHAP overlay. Maliyet, kur ve mesafenin kararlardaki ağırlığı.' },
                { t: 'Ablation', d: 'TCMB kuru, CO₂, geo-distance çıkarıldığında tahminin nasıl bozulduğunu gösteren testler. |Δ FX| 66%.' },
                { t: 'Target Leakage', d: '14 test ile expected_profit, route_label, value_uplift hiçbir input feature\'da olamaz garantisi.' },
                { t: 'Reproducibility', d: 'numpy.default_rng(42), sklearn, catboost, xgboost — tek seed ile bit-for-bit aynı çıktı.' },
              ].map((c, i) => (
                <div key={i} className="p-8 border-r border-b border-r2v-line">
                  <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted mb-6">
                    Kanıt 0{i + 1}
                  </div>
                  <h3 className="text-xl font-medium tracking-tight mb-4 text-r2v-ink">{c.t}</h3>
                  <p className="text-sm leading-relaxed text-r2v-ink/70">{c.d}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* RULES — K1/K2/K3 */}
        <section className="border-b border-r2v-line">
          <div className="max-w-[1440px] mx-auto px-6 md:px-10 py-20 md:py-28">
            <div className="grid grid-cols-12 gap-x-6 md:gap-x-8 mb-16">
              <div className="col-span-12 md:col-span-2">
                <div className="text-[11px] font-mono uppercase tracking-[0.2em] text-r2v-muted">
                  05 — Kural Uyumu
                </div>
              </div>
              <div className="col-span-12 md:col-span-10">
                <h2 className="text-4xl md:text-6xl leading-[1.02] font-medium tracking-tightest max-w-3xl">
                  Üç zorunlu kural.<br />
                  <span className="text-r2v-muted">Sıfır esneklik.</span>
                </h2>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-r2v-line border border-r2v-line">
              {[
                {
                  k: 'K1',
                  t: 'Karbon',
                  d: 'Hackathon resmi sabit faktörler — kara 0.100, deniz 0.015, hava 0.500, demiryolu 0.030 kg CO₂/ton-km. Stokastik üretim YOK.',
                },
                {
                  k: 'K2',
                  t: 'Kur',
                  d: 'TCMB canlı USD/TRY, EUR/TRY her iki modelin input\'unda. Ablation without_fx |Δ| = %66 — load-bearing.',
                },
                {
                  k: 'K3',
                  t: 'Geo',
                  d: 'ORS\'tan bağımsız precomputed lookup → Haversine fallback. Yeni şehir gelince geometrik mesafe devrede.',
                },
              ].map((r, i) => (
                <div key={i} className="bg-r2v-base p-8 md:p-10">
                  <div className="flex items-baseline justify-between mb-8 pb-4 border-b border-r2v-line">
                    <span className="text-3xl font-medium tracking-tight text-r2v-terracotta">{r.k}</span>
                    <span className="text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted">
                      Mandatory
                    </span>
                  </div>
                  <h3 className="text-2xl font-medium tracking-tight mb-4">{r.t}</h3>
                  <p className="text-sm leading-relaxed text-r2v-ink/75">{r.d}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section id="pilot">
          <div className="max-w-[1440px] mx-auto px-6 md:px-10 py-20 md:py-28">
            <div className="grid grid-cols-12 gap-x-6 md:gap-x-8 items-end">
              <div className="col-span-12 md:col-span-7">
                <div className="text-[11px] font-mono uppercase tracking-[0.2em] text-r2v-muted mb-6">
                  06 — Şimdi
                </div>
                <h2 className="text-5xl md:text-7xl leading-[0.98] font-medium tracking-tightest">
                  Hammaddeyi <br />
                  değere çevir.
                </h2>
              </div>
              <div className="col-span-12 md:col-span-5 mt-10 md:mt-0">
                <div className="flex flex-col gap-3">
                  <Link
                    to="/dashboard"
                    className="group flex items-center justify-between bg-r2v-ink text-r2v-base px-6 py-5 hover:bg-r2v-terracotta transition-colors"
                  >
                    <span className="text-base font-medium">Karar Motorunu Başlat</span>
                    <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M5 12h14M13 5l7 7-7 7" strokeLinecap="square" />
                    </svg>
                  </Link>
                  <Link
                    to="/dashboard/geo"
                    className="group flex items-center justify-between border border-r2v-ink px-6 py-5 hover:bg-r2v-ink hover:text-r2v-base transition-colors"
                  >
                    <span className="text-base font-medium">Geo & Karbon Haritası</span>
                    <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M5 12h14M13 5l7 7-7 7" strokeLinecap="square" />
                    </svg>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-r2v-line bg-r2v-base">
        <div className="max-w-[1440px] mx-auto px-6 md:px-10 py-16">
          <div className="grid grid-cols-12 gap-x-6 md:gap-x-8">
            <div className="col-span-12 md:col-span-4 mb-10 md:mb-0">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-7 h-7 bg-r2v-ink flex items-center justify-center">
                  <div className="w-3 h-3 bg-r2v-terracotta" />
                </div>
                <span className="text-[15px] font-semibold tracking-tight">Raw2Value</span>
              </div>
              <p className="text-sm text-r2v-muted max-w-xs leading-relaxed">
                TR71 / Kapadokya 2026 Hackathon · Kategori 03 · Akıllı Tedarik Zinciri Karar Motoru.
              </p>
            </div>

            <div className="col-span-6 md:col-span-2">
              <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted mb-5">
                Modeller
              </div>
              <ul className="space-y-3 text-sm">
                <li><Link to="/dashboard" className="hover:text-r2v-terracotta transition-colors">Value Uplift</Link></li>
                <li><Link to="/dashboard" className="hover:text-r2v-terracotta transition-colors">Route Reco</Link></li>
                <li><Link to="/dashboard" className="hover:text-r2v-terracotta transition-colors">Buyer Match</Link></li>
              </ul>
            </div>

            <div className="col-span-6 md:col-span-2">
              <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted mb-5">
                Sistem
              </div>
              <ul className="space-y-3 text-sm">
                <li><Link to="/dashboard" className="hover:text-r2v-terracotta transition-colors">Dashboard</Link></li>
                <li><Link to="/dashboard/geo" className="hover:text-r2v-terracotta transition-colors">Geo & Karbon</Link></li>
                <li><a href="#evidence" className="hover:text-r2v-terracotta transition-colors">Evidence</a></li>
              </ul>
            </div>

            <div className="col-span-12 md:col-span-4">
              <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted mb-5">
                Hammaddeler
              </div>
              <div className="grid grid-cols-3 gap-3">
                {['Pomza', 'Perlit', 'Kabak Çek.'].map((m) => (
                  <div key={m} className="border border-r2v-line p-4">
                    <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted mb-1">
                      {m === 'Kabak Çek.' ? 'Seed' : 'Mineral'}
                    </div>
                    <div className="text-sm font-medium tracking-tight">{m}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-16 pt-6 border-t border-r2v-line flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-[11px] font-mono uppercase tracking-[0.18em] text-r2v-muted">
            <span>© 2026 Raw2Value AI</span>
            <span>Kapadokya Hackathon — Kategori 03</span>
            <span>Build v0.4.0 — seed=42</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
