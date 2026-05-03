import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <div className="min-h-screen bg-r2v-base text-r2v-charcoal antialiased font-sans overflow-x-hidden">
      {/* Top promo bar */}
      <div className="bg-r2v-charcoal text-white text-center py-2.5 text-xs md:text-sm font-medium tracking-wide">
        <a className="inline-flex items-center gap-2 hover:text-r2v-terracotta transition-colors" href="#models">
          TR71 Bölgesi · Akıllı Tedarik Zinciri Karar Motoru — Canlı Demo
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </a>
      </div>

      {/* Floating Navbar */}
      <div className={`sticky top-0 z-50 transition-all duration-300 ${scrolled ? 'pt-3 px-3' : 'pt-0 px-0'}`}>
        <header
          className={`mx-auto transition-all duration-300 ${
            scrolled
              ? 'max-w-5xl bg-white/90 backdrop-blur-md border border-r2v-line shadow-[0_4px_24px_rgba(31,34,38,0.06)] rounded-full'
              : 'max-w-full bg-r2v-base border-b border-r2v-line rounded-none'
          }`}
        >
          <div className={`flex items-center justify-between transition-all duration-300 ${scrolled ? 'px-6 py-2.5' : 'px-6 md:px-10 py-4'}`}>
            <Link to="/" className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-r2v-terracotta flex items-center justify-center shadow-sm">
                <div className="w-3 h-3 rounded-full bg-white" />
              </div>
              <span className="font-bold text-lg tracking-tight text-r2v-charcoal">
                Raw2Value <span className="font-normal text-r2v-muted">AI</span>
              </span>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
              {[
                { href: '#models', label: 'Modeller' },
                { href: '#evidence', label: 'Kanıt' },
                { href: '#pipeline', label: 'Pipeline' },
                { href: '#pilot', label: 'Pilot' },
              ].map((l) => (
                <a
                  key={l.href}
                  href={l.href}
                  className="px-4 py-2 text-sm font-medium text-r2v-charcoal/75 hover:text-r2v-charcoal hover:bg-r2v-soft rounded-full transition-colors"
                >
                  {l.label}
                </a>
              ))}
            </nav>

            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 bg-r2v-charcoal text-white px-5 py-2.5 rounded-full text-sm font-semibold shadow-sm hover:bg-r2v-terracotta transition-colors"
            >
              Sisteme Giriş
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M5 12h14M13 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>
          </div>
        </header>
      </div>

      <main>
        {/* HERO — light, soft, jury-friendly */}
        <section className="relative px-4 md:px-8 pt-12 md:pt-20 pb-16 md:pb-24">
          <div className="max-w-7xl mx-auto">
            <div className="relative rounded-[2.5rem] overflow-hidden border border-r2v-line bg-gradient-to-br from-r2v-soft via-r2v-base to-r2v-soft shadow-[0_20px_60px_-20px_rgba(31,34,38,0.15)]">
              {/* Decorative soft blobs */}
              <div className="pointer-events-none absolute -top-32 -right-32 w-96 h-96 rounded-full bg-r2v-terracotta/8 blur-3xl" />
              <div className="pointer-events-none absolute -bottom-32 -left-32 w-96 h-96 rounded-full bg-r2v-green/10 blur-3xl" />

              <div className="relative px-6 md:px-16 py-20 md:py-32">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-r2v-line shadow-sm text-xs font-semibold text-r2v-charcoal mb-8">
                  <span className="w-1.5 h-1.5 rounded-full bg-r2v-green animate-pulse" />
                  TR71 · Kapadokya Hackathon 2026
                </div>

                <h1 className="text-4xl sm:text-5xl md:text-7xl lg:text-[5.5rem] font-medium leading-[1.04] tracking-tightest text-r2v-charcoal max-w-5xl">
                  Don't sell <span className="text-r2v-muted">the rock.</span>
                  <br />
                  <span className="text-r2v-terracotta">Sell the value.</span>
                </h1>

                <p className="mt-8 text-base md:text-xl text-r2v-charcoal/80 max-w-2xl leading-relaxed">
                  Kapadokya'nın üç hammaddesini — <strong className="font-semibold text-r2v-charcoal">pomza, perlit, kabak çekirdeği</strong> — işleyip ihraç etmek için
                  en kârlı rotayı, beklenen kârı (TRY), CO₂ maliyetini ve alıcı eşleşmesini öneren makine öğrenmesi tabanlı karar motoru.
                </p>

                <div className="mt-10 flex flex-col sm:flex-row gap-3">
                  <Link
                    to="/dashboard"
                    className="group inline-flex items-center justify-center gap-2 bg-r2v-charcoal text-white px-7 py-4 rounded-full font-semibold shadow-md hover:bg-r2v-terracotta transition-colors text-base"
                  >
                    Karar Motorunu Aç
                    <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                      <path d="M5 12h14M13 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </Link>
                  <a
                    href="#models"
                    className="inline-flex items-center justify-center gap-2 bg-white text-r2v-charcoal border border-r2v-line px-7 py-4 rounded-full font-semibold hover:border-r2v-charcoal/40 transition-colors text-base"
                  >
                    Nasıl Çalışıyor?
                  </a>
                </div>

                {/* KPI strip */}
                <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { v: '1.500', l: 'Eğitim Senaryosu', s: '120 gerçek + augmented' },
                    { v: 'R² 0.84', l: 'Profit Modeli', s: 'CatBoost holdout' },
                    { v: 'F1 0.78', l: 'Route Sınıflandırıcı', s: 'macro-F1' },
                    { v: '88', l: 'Test', s: 'pytest passing' },
                  ].map((k, i) => (
                    <div key={i} className="bg-white/70 backdrop-blur rounded-2xl border border-r2v-line p-5">
                      <div className="text-2xl md:text-3xl font-semibold tracking-tight text-r2v-charcoal">{k.v}</div>
                      <div className="text-sm font-semibold text-r2v-charcoal/85 mt-1">{k.l}</div>
                      <div className="text-xs text-r2v-muted mt-1">{k.s}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* MODELS */}
        <section id="models" className="bg-r2v-soft border-y border-r2v-line py-20 md:py-28 px-4 md:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-r2v-line text-xs font-semibold text-r2v-terracotta uppercase tracking-wider mb-6">
                Üç AI Modeli
              </div>
              <h2 className="text-3xl md:text-5xl font-medium tracking-tightest leading-[1.1] text-r2v-charcoal">
                Bir ilan platformu <span className="text-r2v-terracotta italic">değildir.</span>
                <br />
                Bir <span className="font-semibold">karar motorudur.</span>
              </h2>
              <p className="mt-6 text-base md:text-lg text-r2v-charcoal/70 leading-relaxed">
                Hammadde, lojistik ve alıcı verisini birleştirip katma değerli işleme rotasını öneren üç ML model.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  num: '01',
                  badge: 'CatBoostRegressor',
                  title: 'Value Uplift',
                  desc: 'Hammadde ve işleme rotasına göre beklenen değer artışı ve net kârı (TRY) tahmin eder. RMSE 11.2M holdout.',
                  meta: '39 feature · target=expected_profit_try',
                  icon: (
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M3 17l6-6 4 4 8-8M21 7v6h-6" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ),
                  accent: 'terracotta',
                },
                {
                  num: '02',
                  badge: 'CatBoostClassifier',
                  title: 'Route Recommendation',
                  desc: 'Pomza, perlit ve kabak çekirdeği için ham satışa karşı katma değerli alternatifler arasından en uygun işleme rotasını seçer.',
                  meta: '10 trained class · macro-F1 0.78',
                  icon: (
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ),
                  accent: 'green',
                },
                {
                  num: '03',
                  badge: 'Deterministic Scorer',
                  title: 'Buyer Match',
                  desc: 'Lojistik mesafe, kapasite ve kalite kriterlerini optimize ederek en kârlı Üretici–İşleyici–Alıcı kombinasyonunu sıralar.',
                  meta: '6 component · 3 ağırlık profili',
                  icon: (
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ),
                  accent: 'earth',
                },
              ].map((c) => {
                const accentBg = c.accent === 'terracotta' ? 'bg-r2v-terracotta/10 text-r2v-terracotta' : c.accent === 'green' ? 'bg-r2v-green/15 text-r2v-green' : 'bg-r2v-earth/10 text-r2v-earth';
                return (
                  <div key={c.num} className="group bg-white rounded-3xl border border-r2v-line p-8 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all">
                    <div className="flex items-center justify-between mb-6">
                      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${accentBg}`}>
                        {c.icon}
                      </div>
                      <span className="text-xs font-mono font-semibold text-r2v-muted">{c.num}</span>
                    </div>
                    <div className="inline-block text-[11px] font-mono text-r2v-terracotta bg-r2v-terracotta/8 px-2.5 py-1 rounded-full mb-3">
                      {c.badge}
                    </div>
                    <h3 className="text-xl font-semibold text-r2v-charcoal mb-3 tracking-tight">{c.title}</h3>
                    <p className="text-sm text-r2v-charcoal/75 leading-relaxed mb-5">{c.desc}</p>
                    <div className="pt-4 border-t border-r2v-line text-xs font-mono text-r2v-muted">{c.meta}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* PIPELINE */}
        <section id="pipeline" className="bg-r2v-base py-20 md:py-28 px-4 md:px-8">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-r2v-soft border border-r2v-line text-xs font-semibold text-r2v-charcoal/70 uppercase tracking-wider mb-6">
                Pipeline
              </div>
              <h2 className="text-3xl md:text-5xl font-medium tracking-tightest leading-[1.1] text-r2v-charcoal">
                Excel'den karar çıktısına
                <br />
                <span className="text-r2v-muted">tek yönlü veri akışı.</span>
              </h2>
            </div>

            <div className="bg-white rounded-3xl border border-r2v-line p-6 md:p-10 shadow-sm">
              <div className="space-y-3">
                {[
                  { n: '01', t: 'Master', s: 'data/master/raw2value_v4.xlsx', d: '16 sheet · single source of truth' },
                  { n: '02', t: 'ETL', s: 'ml/src/etl.py', d: 'Excel → 12 parquet + distance lookup' },
                  { n: '03', t: 'Augmentation', s: 'ml/src/augmentation.py', d: '120 → 1.500 satır · seed=42' },
                  { n: '04', t: 'Training', s: 'ml/src/train_{profit,route}.py', d: 'CatBoost · native categorical' },
                  { n: '05', t: 'Inference', s: 'raw2value_ml/inference.py', d: 'analyze() — backend tek giriş noktası' },
                ].map((s) => (
                  <div key={s.n} className="grid grid-cols-12 gap-3 md:gap-6 items-center p-4 rounded-2xl hover:bg-r2v-soft transition-colors">
                    <div className="col-span-2 md:col-span-1 text-base md:text-xl font-mono font-semibold text-r2v-terracotta">
                      {s.n}
                    </div>
                    <div className="col-span-10 md:col-span-3 text-base font-semibold text-r2v-charcoal tracking-tight">
                      {s.t}
                    </div>
                    <div className="col-span-12 md:col-span-4 font-mono text-sm text-r2v-charcoal/70 break-all">
                      {s.s}
                    </div>
                    <div className="col-span-12 md:col-span-4 text-sm text-r2v-charcoal/70">
                      {s.d}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* EVIDENCE */}
        <section id="evidence" className="bg-r2v-soft border-y border-r2v-line py-20 md:py-28 px-4 md:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-r2v-line text-xs font-semibold text-r2v-charcoal/70 uppercase tracking-wider mb-6">
                AI Evidence
              </div>
              <h2 className="text-3xl md:text-5xl font-medium tracking-tightest leading-[1.1] text-r2v-charcoal">
                Şeffaf metrik. <span className="text-r2v-muted">Reproducible sonuç.</span>
              </h2>
              <p className="mt-6 text-base md:text-lg text-r2v-charcoal/70 leading-relaxed">
                Hackathon projesinde güven, açıklanabilir kanıttan gelir. Random seed 42 ile her sonuç tekrar üretilebilir;
                ablation çalışmaları kuralların load-bearing olduğunu gösterir.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                {
                  t: 'Feature Importance',
                  d: 'CatBoost feature importance + SHAP overlay. Maliyet, kur ve mesafenin kararlardaki ağırlığı.',
                  icon: (
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ),
                },
                {
                  t: 'Ablation Çalışması',
                  d: 'TCMB kuru, CO₂, geo-distance çıkarıldığında tahminin nasıl bozulduğunu gösteren testler. |Δ FX| = 66%.',
                  icon: (
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ),
                },
                {
                  t: 'Veri Çoğaltma',
                  d: '120 gerçek referans satırı + domain-informed synthetic augmentation ile 1.500 senaryo.',
                  icon: (
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ),
                },
                {
                  t: 'Target Leakage Sıfır',
                  d: '14 test ile expected_profit, route_label, value_uplift hiçbir input feature olamaz garantisi.',
                  icon: (
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ),
                },
              ].map((c) => (
                <div key={c.t} className="bg-white rounded-3xl border border-r2v-line p-7 shadow-sm hover:shadow-md transition-shadow">
                  <div className="w-12 h-12 rounded-2xl bg-r2v-soft text-r2v-charcoal flex items-center justify-center mb-5">
                    {c.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-r2v-charcoal mb-3 tracking-tight">{c.t}</h3>
                  <p className="text-sm text-r2v-charcoal/75 leading-relaxed">{c.d}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* RULES K1/K2/K3 */}
        <section className="bg-r2v-base py-20 md:py-28 px-4 md:px-8">
          <div className="max-w-6xl mx-auto">
            <div className="text-center max-w-3xl mx-auto mb-14">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-r2v-soft border border-r2v-line text-xs font-semibold text-r2v-charcoal/70 uppercase tracking-wider mb-6">
                Kural Uyumu
              </div>
              <h2 className="text-3xl md:text-5xl font-medium tracking-tightest leading-[1.1] text-r2v-charcoal">
                Üç zorunlu kural. <span className="text-r2v-muted">Sıfır esneklik.</span>
              </h2>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {[
                { k: 'K1', t: 'Karbon', d: 'Hackathon resmi sabit faktörler — kara 0.100, deniz 0.015, hava 0.500, demiryolu 0.030 kg CO₂/ton-km. Stokastik üretim YOK.' },
                { k: 'K2', t: 'Kur', d: 'TCMB canlı USD/TRY, EUR/TRY her iki modelin input\'unda. Ablation without_fx |Δ| = %66 — load-bearing.' },
                { k: 'K3', t: 'Geo', d: 'ORS\'tan bağımsız precomputed lookup → Haversine fallback. Yeni şehir gelince geometrik mesafe devrede.' },
              ].map((r) => (
                <div key={r.k} className="bg-white rounded-3xl border border-r2v-line p-8 shadow-sm">
                  <div className="flex items-baseline justify-between mb-5 pb-4 border-b border-r2v-line">
                    <span className="text-3xl font-semibold tracking-tight text-r2v-terracotta">{r.k}</span>
                    <span className="text-[11px] font-mono uppercase tracking-widest text-r2v-muted">Mandatory</span>
                  </div>
                  <h3 className="text-xl font-semibold text-r2v-charcoal mb-3 tracking-tight">{r.t}</h3>
                  <p className="text-sm text-r2v-charcoal/75 leading-relaxed">{r.d}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section id="pilot" className="px-4 md:px-8 py-16 md:py-24">
          <div className="max-w-7xl mx-auto">
            <div className="grid md:grid-cols-2 gap-6">
              <Link
                to="/dashboard"
                className="group relative overflow-hidden rounded-[2rem] bg-r2v-charcoal text-white p-10 md:p-14 flex flex-col justify-between min-h-[280px] hover:shadow-2xl hover:shadow-r2v-charcoal/20 transition-all"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-r2v-terracotta/20 to-transparent" />
                <div className="relative">
                  <div className="text-xs font-semibold uppercase tracking-widest text-white/50 mb-3">Başlangıç</div>
                  <h3 className="text-3xl md:text-4xl font-medium tracking-tight leading-tight">
                    Karar Motorunu<br/>Başlat
                  </h3>
                </div>
                <div className="relative self-end">
                  <div className="w-14 h-14 rounded-full bg-r2v-terracotta flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                    <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                      <path d="M5 12h14M13 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                </div>
              </Link>

              <Link
                to="/dashboard/geo"
                className="group rounded-[2rem] bg-r2v-soft text-r2v-charcoal p-10 md:p-14 flex flex-col justify-between min-h-[280px] border border-r2v-line hover:shadow-lg transition-all"
              >
                <div>
                  <div className="text-xs font-semibold uppercase tracking-widest text-r2v-muted mb-3">Görselleştirme</div>
                  <h3 className="text-3xl md:text-4xl font-medium tracking-tight leading-tight">
                    Geo & Karbon<br/>Haritası
                  </h3>
                </div>
                <div className="self-end">
                  <div className="w-14 h-14 rounded-full bg-white border border-r2v-line flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                    <svg className="w-6 h-6 text-r2v-charcoal" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                      <path d="M5 12h14M13 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-r2v-charcoal text-white/70 py-16 md:py-20 px-4 md:px-8 rounded-t-[3rem]">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-10">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="w-8 h-8 rounded-full bg-r2v-terracotta flex items-center justify-center">
                <div className="w-3 h-3 rounded-full bg-white" />
              </div>
              <span className="font-bold text-xl text-white">Raw2Value <span className="font-normal opacity-50">AI</span></span>
            </div>
            <p className="text-sm text-white/60 leading-relaxed max-w-md">
              TR71 / Kapadokya 2026 Hackathon · Kategori 03 · Akıllı Tedarik Zinciri Karar Motoru.
              Hammaddeden katma değerli ürüne en kârlı rotayı öneren ML pipeline.
            </p>
          </div>

          <div>
            <h5 className="font-semibold text-white text-sm mb-4">Modeller</h5>
            <ul className="space-y-2.5 text-sm">
              <li><Link className="hover:text-white transition-colors" to="/dashboard">Value Uplift</Link></li>
              <li><Link className="hover:text-white transition-colors" to="/dashboard">Route Reco</Link></li>
              <li><Link className="hover:text-white transition-colors" to="/dashboard">Buyer Match</Link></li>
            </ul>
          </div>

          <div>
            <h5 className="font-semibold text-white text-sm mb-4">Sistem</h5>
            <ul className="space-y-2.5 text-sm">
              <li><Link className="hover:text-white transition-colors" to="/dashboard">Dashboard</Link></li>
              <li><Link className="hover:text-white transition-colors" to="/dashboard/geo">Geo & Karbon</Link></li>
              <li><a className="hover:text-white transition-colors" href="#evidence">Evidence</a></li>
            </ul>
          </div>
        </div>

        <div className="max-w-7xl mx-auto mt-12 pt-6 border-t border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs text-white/40">
          <span>© 2026 Raw2Value AI</span>
          <span>seed=42 · v0.4.0</span>
        </div>
      </footer>
    </div>
  );
}
