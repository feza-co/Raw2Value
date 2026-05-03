import { Link } from 'react-router-dom';
import {
  ChevronDown, ArrowUpRight, ArrowDown, ArrowRight,
  TrendingDown, TrendingUp, Trophy, Mountain, Factory, Globe2,
  LineChart, GitBranch, Network,
} from 'lucide-react';

function Diamond() {
  return <div className="w-4 h-4 bg-dapper-green transform rotate-45 rounded-sm shrink-0" />;
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2.5">
      <Diamond />
      <span className="font-semibold text-r2v-charcoal tracking-wide">{children}</span>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div className="text-r2v-charcoal antialiased overflow-x-hidden">
      {/* ─────────────── NAVIGATION ─────────────── */}
      <nav className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-7xl bg-white rounded-lg shadow-sm px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#111827" />
            <path d="M2 17L12 22L22 17" stroke="#111827" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M2 12L12 17L22 12" stroke="#111827" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span className="text-xl font-bold tracking-tight">Raw2Value</span>
        </Link>

        <div className="hidden md:flex items-center space-x-8 text-sm font-semibold">
          <a href="#problem" className="hover:text-gray-600 transition-colors">Problem</a>
          <a href="#solution" className="flex items-center gap-1 cursor-pointer hover:text-gray-600 transition-colors">
            Çözüm
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </a>
          <a href="#ecosystem" className="hover:text-gray-600 transition-colors">Ekosistem</a>
          <a href="#models" className="hover:text-gray-600 transition-colors">Modeller</a>
          <a href="#about" className="hover:text-gray-600 transition-colors">Hakkında</a>
        </div>

        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="hidden sm:inline text-sm font-semibold hover:text-gray-600 transition-colors">
            Sisteme giriş
          </Link>
          <Link
            to="/dashboard"
            className="bg-dapper-green p-2 rounded hover:brightness-95 transition-all flex items-center justify-center"
            aria-label="Sisteme giriş"
          >
            <ArrowUpRight className="w-4 h-4 text-r2v-charcoal" strokeWidth={2.5} />
          </Link>
        </div>
      </nav>

      {/* ─────────────── HERO (KORUNDU) ─────────────── */}
      <header className="relative pt-40 pb-32 px-6 lg:px-16 max-w-[1440px] mx-auto min-h-screen flex flex-col justify-center">
        <div className="mb-8">
          <SectionLabel>Akıllı Tedarik Zinciri Karar Motoru</SectionLabel>
        </div>

        <div className="max-w-4xl relative z-10">
          <h1 className="text-6xl md:text-8xl font-bold tracking-tightest text-r2v-charcoal leading-[1.1] mb-12">
            Hammaddeyi <span className="font-serif-italic text-r2v-charcoal">değere</span><br />
            çeviren karar<br />
            motoru, Kapadokya için
          </h1>

          <div className="max-w-md">
            <p className="text-lg md:text-xl font-medium text-r2v-charcoal/85 mb-8 leading-snug">
              Pomza, perlit ve kabak çekirdeği için en kârlı işleme rotasını, beklenen kârı (TRY) ve CO₂ maliyetini öneren ML pipeline.
            </p>
            <div className="flex items-center gap-4">
              <a href="#problem" className="font-semibold text-r2v-charcoal">Daha fazlasını gör</a>
              <a
                href="#problem"
                className="bg-dapper-green p-3 rounded hover:brightness-95 transition-all flex items-center justify-center"
                aria-label="Aşağı kaydır"
              >
                <ArrowDown className="w-5 h-5 text-r2v-charcoal" strokeWidth={2.5} />
              </a>
            </div>
          </div>
        </div>

        {/* Floating Evidence Card */}
        <div className="hidden md:flex absolute right-6 lg:right-16 bottom-20 z-20 bg-white rounded-xl shadow-floating p-4 gap-6 max-w-sm">
          <div className="flex-1 flex flex-col">
            <p className="text-sm font-semibold text-r2v-charcoal mb-4 leading-tight">
              %84 R² doğrulukla beklenen kâr tahmini, 1.500 senaryoda doğrulandı
            </p>
            <div className="flex items-center justify-between mt-auto">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-r2v-charcoal rounded-sm" />
                <div className="w-3 h-3 bg-r2v-charcoal rounded-sm relative -left-1 top-1" />
                <span className="font-bold text-xs">model_lab</span>
              </div>
              <Link
                to="/dashboard"
                className="bg-dapper-green p-1.5 rounded hover:brightness-95 transition-all"
                aria-label="Modeli incele"
              >
                <ArrowUpRight className="w-3 h-3 text-r2v-charcoal" strokeWidth={2.5} />
              </Link>
            </div>
          </div>
          <div className="w-24 h-24 rounded-lg overflow-hidden flex-shrink-0 bg-gradient-to-br from-amber-300 via-orange-400 to-red-500 flex items-center justify-center">
            <span className="text-white font-bold text-3xl tracking-tight">84%</span>
          </div>
        </div>

        <div className="absolute bottom-0 right-1/4 hidden md:flex">
          <div className="w-12 h-12 bg-dapper-green opacity-50" />
          <div className="w-12 h-12 bg-dapper-green" />
        </div>

        <div className="hidden lg:flex absolute right-0 top-1/2 -translate-y-1/2 bg-white rounded-l-full p-3 shadow-md items-center justify-center cursor-pointer">
          <svg className="w-4 h-4 text-r2v-charcoal" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 21a9 9 0 1 1 9-9 9.01 9.01 0 0 1-9 9zm0-16.5a7.5 7.5 0 1 0 7.5 7.5A7.51 7.51 0 0 0 12 4.5zM12 16a4 4 0 1 1 4-4 4.005 4.005 0 0 1-4 4zm0-6.5a2.5 2.5 0 1 0 2.5 2.5A2.503 2.503 0 0 0 12 9.5z" />
          </svg>
        </div>
      </header>

      {/* ─────────────── 02 — PROBLEM ─────────────── */}
      <section id="problem" className="py-24 px-6 lg:px-16 max-w-[1440px] mx-auto relative border-t border-gray-200">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 hidden md:flex">
          <div className="w-16 h-16 bg-dapper-green opacity-75" />
          <div className="w-16 h-16 bg-dapper-green opacity-50" />
          <div className="w-16 h-16 bg-dapper-green opacity-25" />
        </div>

        <div className="flex items-center justify-between flex-wrap gap-4 mb-12">
          <div className="flex items-center gap-3">
            <span className="bg-r2v-terracotta text-white text-xs font-bold px-2.5 py-1 rounded font-mono">02</span>
            <span className="font-semibold text-r2v-charcoal text-lg">Devasa Potansiyel, Devasa Kayıp</span>
          </div>
          <div className="flex items-center gap-2 text-r2v-terracotta font-semibold">
            <span className="w-2.5 h-2.5 rounded-full bg-r2v-terracotta" />
            Masada Bırakılan Para
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
          {/* SOL: Üretim payı */}
          <div className="bg-white rounded-xl p-10 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-widest text-r2v-muted mb-4">
              Dünya Pomza Üretiminde Türkiye
            </p>
            <div className="text-7xl md:text-9xl font-bold tracking-tightest text-blue-600 leading-none mb-6">
              %45,6
            </div>
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-5 h-5 text-r2v-charcoal" />
              <span className="text-xl font-bold text-r2v-charcoal">Dünya 1. Sırada</span>
            </div>
            <p className="text-sm text-r2v-muted">
              Kaynak — USGS, 2025 · İhracat payı %31–40 — Volza, 2023–24
            </p>
          </div>

          {/* SAĞ: Fiyat karşılaştırması */}
          <div className="bg-white rounded-xl p-10 shadow-sm flex flex-col">
            <p className="text-xs font-bold uppercase tracking-widest text-r2v-muted mb-4">
              Ham Pomza İhracatı
            </p>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-6xl md:text-7xl font-bold tracking-tightest text-r2v-terracotta">$91,7</span>
              <span className="text-xl text-r2v-muted font-medium">/ton</span>
            </div>
            <p className="text-sm text-r2v-muted mb-8">
              Kaynak — WITS (UN Comtrade), 2023
            </p>

            <div className="flex items-center gap-2 mb-3">
              <ArrowDown className="w-5 h-5 text-r2v-charcoal" strokeWidth={2.5} />
              <span className="text-xs font-bold uppercase tracking-widest text-r2v-charcoal">
                İşleme & Katma Değer
              </span>
            </div>

            <p className="text-xs font-bold uppercase tracking-widest text-green-700 mb-2">
              Mikronize Pomza · İşlenmiş
            </p>
            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-6xl md:text-7xl font-bold tracking-tightest text-green-700">$200–300</span>
              <span className="text-xl text-r2v-muted font-medium">/ton</span>
            </div>
            <p className="text-sm text-r2v-muted mt-auto">
              Kaynak — TradeKey B2B · Sektörel Pazar Verileri
            </p>
          </div>
        </div>

        {/* Alt slogan */}
        <div className="border-t border-gray-300 pt-8">
          <p className="text-xl md:text-3xl font-serif-italic text-r2v-charcoal leading-snug max-w-5xl">
            Dünyanın yarısını üretiyoruz — ama ucuza ham satarak{' '}
            <span className="not-italic font-bold text-r2v-terracotta">masada para bırakıyoruz.</span>{' '}
            Çünkü üreticimiz kârlı rotayı hesaplayamıyor.
          </p>
        </div>
      </section>

      {/* ─────────────── 04 — ÇÖZÜM ─────────────── */}
      <section id="solution" className="py-24 px-6 lg:px-16 max-w-[1440px] mx-auto border-t border-gray-200">
        <div className="flex items-center justify-between flex-wrap gap-4 mb-10">
          <div className="flex items-center gap-3">
            <span className="bg-blue-600 text-white text-xs font-bold px-2.5 py-1 rounded font-mono">04</span>
            <span className="font-semibold text-blue-600 text-lg">Çözüm</span>
          </div>
          <div className="flex items-center gap-2 text-blue-600 font-semibold">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
            Karar Motoru
          </div>
        </div>

        <h2 className="text-5xl md:text-7xl font-bold tracking-tightest text-r2v-charcoal leading-[1.1] mb-6">
          Pazar yeri değil,{' '}
          <span className="text-blue-600">karar motoru.</span>
        </h2>
        <p className="text-lg md:text-2xl text-r2v-charcoal/85 font-medium mb-16 max-w-3xl">
          Hammaddeyi değil — <span className="font-bold text-r2v-charcoal">katma değeri</span> yönetin.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 01 Kâr Tahmini */}
          <div className="bg-white rounded-xl p-8 shadow-sm hover:shadow-md transition-shadow flex flex-col">
            <div className="flex items-start justify-between mb-12">
              <div className="w-12 h-12 bg-blue-600 rounded flex items-center justify-center">
                <LineChart className="w-6 h-6 text-white" strokeWidth={2.5} />
              </div>
              <span className="text-2xl font-bold text-r2v-charcoal/30 font-mono">01</span>
            </div>
            <h3 className="text-2xl font-bold text-r2v-charcoal mb-4 tracking-tight">Kâr Tahmini</h3>
            <p className="text-base text-r2v-charcoal/75 leading-relaxed">
              Hangi rotanın ne kadar kâr getireceğini, eğitilmiş makine öğrenmesi modeli hesaplar.
            </p>
          </div>

          {/* 02 Rota Önerisi */}
          <div className="bg-white rounded-xl p-8 shadow-sm hover:shadow-md transition-shadow flex flex-col">
            <div className="flex items-start justify-between mb-12">
              <div className="w-12 h-12 bg-r2v-charcoal rounded flex items-center justify-center">
                <GitBranch className="w-6 h-6 text-white" strokeWidth={2.5} />
              </div>
              <span className="text-2xl font-bold text-r2v-charcoal/30 font-mono">02</span>
            </div>
            <h3 className="text-2xl font-bold text-r2v-charcoal mb-4 tracking-tight">Rota Önerisi</h3>
            <p className="text-base text-r2v-charcoal/75 leading-relaxed">
              Ham satış yerine, en yüksek katma değerli işlenmiş ürünü tavsiye eder.
            </p>
          </div>

          {/* 03 B2B Eşleşme */}
          <div className="bg-white rounded-xl p-8 shadow-sm hover:shadow-md transition-shadow flex flex-col">
            <div className="flex items-start justify-between mb-12">
              <div className="w-12 h-12 bg-green-700 rounded flex items-center justify-center">
                <Network className="w-6 h-6 text-white" strokeWidth={2.5} />
              </div>
              <span className="text-2xl font-bold text-r2v-charcoal/30 font-mono">03</span>
            </div>
            <h3 className="text-2xl font-bold text-r2v-charcoal mb-4 tracking-tight">İşletmeden İşletmeye Eşleşme</h3>
            <p className="text-base text-r2v-charcoal/75 leading-relaxed">
              Üretici, işleyici ve alıcıyı skorlayarak en uygun zinciri kurar.
            </p>
          </div>
        </div>
      </section>

      {/* ─────────────── 06 — EKOSİSTEM ─────────────── */}
      <section id="ecosystem" className="py-24 px-6 lg:px-16 max-w-[1440px] mx-auto border-t border-gray-200">
        <div className="flex items-center justify-between flex-wrap gap-4 mb-10">
          <div className="flex items-center gap-3">
            <span className="bg-green-700 text-white text-xs font-bold px-2.5 py-1 rounded font-mono">06</span>
            <span className="font-semibold text-green-700 text-lg">Kazanan Bir Ekosistem</span>
          </div>
          <div className="flex items-center gap-2 text-green-700 font-semibold">
            <span className="w-2.5 h-2.5 rounded-full bg-green-700" />
            Üç Taraf — Tek Zincir
          </div>
        </div>

        {/* Zincir kartı */}
        <div className="bg-white rounded-2xl p-8 md:p-12 shadow-sm mb-12">
          <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr_auto_1fr] gap-6 md:gap-4 items-center">
            {/* Halka 1 */}
            <div className="text-center flex flex-col items-center">
              <span className="bg-r2v-terracotta text-white text-[11px] font-bold px-3 py-1.5 rounded font-mono uppercase tracking-widest mb-6">
                Birinci Halka
              </span>
              <div className="w-20 h-20 rounded-full bg-r2v-soft border border-gray-200 flex items-center justify-center mb-6">
                <Mountain className="w-10 h-10 text-r2v-charcoal" strokeWidth={1.5} />
              </div>
              <h3 className="text-2xl font-bold text-r2v-charcoal tracking-tight mb-2">
                Hammadde<br />Üreticisi
              </h3>
              <p className="text-sm text-r2v-muted font-medium">
                Pomza · Perlit · Çekirdek
              </p>
            </div>

            <ArrowRight className="hidden md:block w-7 h-7 text-r2v-muted mx-auto" strokeWidth={2} />

            {/* Halka 2 */}
            <div className="text-center flex flex-col items-center">
              <span className="bg-blue-600 text-white text-[11px] font-bold px-3 py-1.5 rounded font-mono uppercase tracking-widest mb-6">
                İkinci Halka
              </span>
              <div className="w-20 h-20 rounded-full bg-r2v-soft border border-gray-200 flex items-center justify-center mb-6">
                <Factory className="w-10 h-10 text-r2v-charcoal" strokeWidth={1.5} />
              </div>
              <h3 className="text-2xl font-bold text-r2v-charcoal tracking-tight mb-2">
                İşleyici<br />Tesis
              </h3>
              <p className="text-sm text-r2v-muted font-medium">
                Mikronize · Genleştirilmiş
              </p>
            </div>

            <ArrowRight className="hidden md:block w-7 h-7 text-r2v-muted mx-auto" strokeWidth={2} />

            {/* Halka 3 */}
            <div className="text-center flex flex-col items-center">
              <span className="bg-green-700 text-white text-[11px] font-bold px-3 py-1.5 rounded font-mono uppercase tracking-widest mb-6">
                Üçüncü Halka
              </span>
              <div className="w-20 h-20 rounded-full bg-r2v-soft border border-gray-200 flex items-center justify-center mb-6">
                <Globe2 className="w-10 h-10 text-r2v-charcoal" strokeWidth={1.5} />
              </div>
              <h3 className="text-2xl font-bold text-r2v-charcoal tracking-tight mb-2">
                Küresel<br />Alıcı
              </h3>
              <p className="text-sm text-r2v-muted font-medium">
                Almanya · Hollanda · İç Pazar
              </p>
            </div>
          </div>
        </div>

        {/* Alt slogan */}
        <div className="pt-4">
          <p className="text-3xl md:text-5xl font-bold tracking-tightest text-r2v-charcoal leading-[1.15]">
            Biz <span className="line-through text-r2v-muted/60 font-normal">aracıları</span> değil,{' '}
            <span className="text-r2v-terracotta">bilgisizliği</span> ortadan kaldırıyoruz.
          </p>
        </div>
      </section>

      {/* ─────────────── CTA ─────────────── */}
      <section id="models" className="py-24 px-6 lg:px-16 max-w-[1440px] mx-auto border-t border-gray-200">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Link
            to="/dashboard"
            className="group relative overflow-hidden rounded-2xl bg-r2v-charcoal text-white p-10 md:p-14 flex flex-col justify-between min-h-[260px] hover:shadow-2xl transition-all"
          >
            <div className="absolute -top-20 -right-20 w-80 h-80 bg-dapper-green/30 rounded-full blur-3xl" />
            <div className="relative">
              <div className="text-xs font-semibold uppercase tracking-widest text-white/60 mb-3">Demo</div>
              <h3 className="text-3xl md:text-4xl font-bold tracking-tight leading-tight">
                Karar Motorunu<br />Çalıştır
              </h3>
            </div>
            <div className="relative self-end">
              <div className="w-14 h-14 rounded-xl bg-dapper-green flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <ArrowUpRight className="w-6 h-6 text-r2v-charcoal" strokeWidth={2.5} />
              </div>
            </div>
          </Link>

          <Link
            to="/dashboard/geo"
            className="group rounded-2xl bg-white text-r2v-charcoal p-10 md:p-14 flex flex-col justify-between min-h-[260px] border border-gray-200 hover:shadow-lg transition-all"
          >
            <div>
              <div className="text-xs font-semibold uppercase tracking-widest text-r2v-muted mb-3">Görselleştirme</div>
              <h3 className="text-3xl md:text-4xl font-bold tracking-tight leading-tight">
                Geo & Karbon<br />Haritası
              </h3>
            </div>
            <div className="self-end">
              <div className="w-14 h-14 rounded-xl bg-r2v-charcoal flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <ArrowUpRight className="w-6 h-6 text-white" strokeWidth={2.5} />
              </div>
            </div>
          </Link>
        </div>
      </section>

      {/* ─────────────── FOOTER ─────────────── */}
      <footer id="about" className="bg-r2v-charcoal text-white/75 py-14 px-6 lg:px-16 mt-12">
        <div className="max-w-[1440px] mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-sm">
          <span className="font-semibold text-white">Raw2Value · Kapadokya Hackathon — 2026</span>
          <span className="font-mono text-white/50">seed=42 · build v0.4.0</span>
        </div>
      </footer>
    </div>
  );
}