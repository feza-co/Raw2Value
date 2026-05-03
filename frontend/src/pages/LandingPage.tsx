import { Link } from 'react-router-dom';
import {
  ChevronDown, ArrowUpRight, ArrowDown, ArrowRight,
  Trophy, Mountain, Factory, Globe2,
  LineChart, GitBranch, Network,
  RefreshCw, Leaf, MapPin, Map, Locate,
} from 'lucide-react';

/* ---------- Küçük yardımcı bileşenler ---------- */

function Diamond({ className = 'bg-[#0a0a0a]' }: { className?: string }) {
  return <div className={`w-3.5 h-3.5 ${className} transform rotate-45 rounded-[1px] shrink-0`} />;
}

function NumPill({
  num,
  color = 'bg-[#0a0a0a]',
}: {
  num: string;
  color?: string;
}) {
  return (
    <span className={`inline-block ${color} text-white text-xs md:text-sm font-semibold font-mono px-2.5 py-1 tracking-wider`}>
      {num}
    </span>
  );
}

function Eyebrow({
  num,
  numColor,
  children,
}: {
  num: string;
  numColor?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-4 font-mono text-sm md:text-base tracking-wider text-[#0a0a0a]">
      <NumPill num={num} color={numColor} />
      <span className="font-medium">{children}</span>
    </div>
  );
}

function HeadDot({ color = 'bg-[#0a0a0a]', label }: { color?: string; label: string }) {
  return (
    <div className="flex items-center gap-2.5 font-mono text-xs md:text-sm tracking-wider uppercase">
      <Diamond className={color} />
      <span>{label}</span>
    </div>
  );
}

/* ---------- Sayfa ---------- */

export default function LandingPage() {
  return (
    <div className="text-[#0a0a0a] antialiased overflow-x-hidden bg-white">
      {/* ─────────────── NAVIGATION (KORUNDU) ─────────────── */}
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

      {/* ============================================================
          SLAYT 1 — KAPAK / HERO
      ============================================================ */}
      <header className="relative pt-40 pb-24 px-6 lg:px-16 max-w-[1440px] mx-auto min-h-screen flex flex-col justify-center bg-white">
        {/* Kapak işareti — 4'lü grid */}
        <div className="absolute top-32 right-6 lg:right-16 hidden md:grid grid-cols-2 grid-rows-2 w-[120px] h-[120px] border-2 border-[#0a0a0a]">
          <div className="border border-[#0a0a0a] bg-white" />
          <div className="border border-[#0a0a0a] bg-[#0a0a0a]" />
          <div className="border border-[#0a0a0a] bg-[#1d4fd6]" />
          <div className="border border-[#0a0a0a] bg-[#d6342a]" />
        </div>

        <div className="mb-8">
          <Eyebrow num="01">Hammadde &nbsp;—&nbsp; Katma Değer</Eyebrow>
        </div>

        <h1 className="text-6xl md:text-8xl lg:text-9xl font-bold tracking-tightest text-[#0a0a0a] leading-[0.92] mb-10">
          Raw2Value<br />
          <span className="text-[#d6342a]">Yapay Zekâ.</span>
        </h1>

        <p className="text-xl md:text-3xl text-[#2a2a2a] font-normal leading-snug max-w-4xl tracking-tight mb-12">
          Kapadokya'nın hammaddesini değere bağlayan{' '}
          <span className="text-[#1d4fd6] font-medium">zekâ katmanı.</span>
        </p>

        <div className="flex items-center gap-4">
          <a href="#problem" className="font-semibold text-[#0a0a0a]">Daha fazlasını gör</a>
          <a
            href="#problem"
            className="bg-dapper-green p-3 rounded hover:brightness-95 transition-all flex items-center justify-center"
            aria-label="Aşağı kaydır"
          >
            <ArrowDown className="w-5 h-5 text-[#0a0a0a]" strokeWidth={2.5} />
          </a>
        </div>

        {/* Alt sağ köşe — sayfa numarası */}
        <div className="absolute bottom-8 right-6 lg:right-16 font-mono text-sm tracking-wider text-[#6b6b6b]">
          1 / 6
        </div>
      </header>

      {/* ============================================================
          SLAYT 2 — DEVASA POTANSİYEL, DEVASA KAYIP
      ============================================================ */}
      <section id="problem" className="py-24 px-6 lg:px-16 max-w-[1440px] mx-auto bg-white border-t-2 border-[#0a0a0a]">
        <div className="flex items-center justify-between flex-wrap gap-4 mb-12">
          <Eyebrow num="02" numColor="bg-[#d6342a]">Devasa Potansiyel, Devasa Kayıp</Eyebrow>
          <HeadDot color="bg-[#d6342a]" label="Masada Bırakılan Para" />
        </div>

        {/* İki kolon: Üretim Gücümüz | Birim Fiyat Uçurumu */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_2px_1fr] gap-12 lg:gap-14 mb-12">
          {/* SOL — Üretim Gücü */}
          <div className="flex flex-col justify-center gap-3 py-2">
            <div className="font-mono text-xs md:text-sm uppercase tracking-widest text-[#0a0a0a] font-medium">
              Dünya Pomza Üretiminde Türkiye
            </div>
            <div className="text-7xl md:text-9xl font-bold tracking-tightest text-[#1d4fd6] leading-[0.86] tabular-nums">
              %45,6
            </div>
            <div className="flex items-center gap-3 text-2xl md:text-3xl font-bold text-[#0a0a0a] tracking-tight">
              <Trophy className="w-7 h-7 text-[#1d4fd6]" strokeWidth={2} />
              Dünya 1. Sırada
            </div>
            <div className="font-mono text-xs md:text-sm text-[#6b6b6b] tracking-wide leading-relaxed">
              Kaynak — USGS, 2025<br />
              İhracat payı %31–40 — Volza, 2023–24
            </div>
          </div>

          {/* Orta dikey çizgi */}
          <div className="hidden lg:block w-[2px] bg-[#0a0a0a] self-stretch" />

          {/* SAĞ — Birim Fiyat Uçurumu */}
          <div className="flex flex-col justify-center gap-2 py-2">
            <div className="flex flex-col gap-1">
              <div className="font-mono text-xs md:text-sm uppercase tracking-widest text-[#6b6b6b] font-medium">
                Ham Pomza İhracatı
              </div>
              <div className="text-5xl md:text-7xl font-bold tracking-tightest text-[#d6342a] leading-[0.92] tabular-nums opacity-90">
                $91,7
                <span className="text-xl md:text-2xl font-medium text-[#6b6b6b] tracking-normal ml-2">/ ton</span>
              </div>
              <div className="font-mono text-xs md:text-sm text-[#6b6b6b] tracking-wide">
                Kaynak — WITS (UN Comtrade), 2023
              </div>
            </div>

            <div className="flex items-center gap-3 my-4">
              <ArrowDown className="w-7 h-7 text-[#0a0a0a]" strokeWidth={2.5} />
              <div className="font-mono text-xs md:text-sm uppercase tracking-widest text-[#0a0a0a] font-medium">
                İşleme &amp; Katma Değer
              </div>
            </div>

            <div className="flex flex-col gap-1">
              <div className="font-mono text-xs md:text-sm uppercase tracking-widest text-[#1f7a3a] font-semibold">
                Mikronize Pomza · İşlenmiş
              </div>
              <div className="text-5xl md:text-7xl font-bold tracking-tightest text-[#1f7a3a] leading-[0.92] tabular-nums">
                $200–300
                <span className="text-xl md:text-2xl font-medium text-[#6b6b6b] tracking-normal ml-2">/ ton</span>
              </div>
              <div className="font-mono text-xs md:text-sm text-[#6b6b6b] tracking-wide">
                Kaynak — TradeKey B2B · Sektörel Pazar Verileri
              </div>
            </div>
          </div>
        </div>

        {/* Kapanış vurgusu */}
        <div className="border-t-2 border-[#0a0a0a] pt-6 max-w-5xl mx-auto text-center">
          <p className="font-serif-italic text-lg md:text-2xl text-[#0a0a0a] leading-relaxed">
            Dünyanın yarısını üretiyoruz — ama ucuza ham satarak{' '}
            <span className="not-italic font-semibold text-[#d6342a]">masada para bırakıyoruz</span>.
            Çünkü üreticimiz kârlı rotayı hesaplayamıyor.
          </p>
        </div>

        {/* Alt sağ — sayfa numarası */}
        <div className="flex justify-end pt-8 mt-8 border-t border-[#e6e6e6] font-mono text-xs tracking-wider text-[#6b6b6b]">
          02 / 06
        </div>
      </section>

      {/* ============================================================
          SLAYT 3 — İÇGÖRÜ / BİLGİ ASİMETRİSİ
      ============================================================ */}
      <section id="insight" className="py-24 px-6 lg:px-16 max-w-[1440px] mx-auto bg-white border-t-2 border-[#0a0a0a]">
        <div className="mb-12">
          <Eyebrow num="03" numColor="bg-[#c97a17]">İçgörü</Eyebrow>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
          {/* SOL: Başlık */}
          <div className="lg:col-span-5 flex flex-col gap-8">
            <h2 className="text-5xl md:text-7xl font-bold tracking-tightest text-[#0a0a0a] leading-[0.94]">
              Bilgi<br />
              <span className="text-[#c97a17]">Asimetrisi.</span>
            </h2>
            <p className="text-xl md:text-2xl text-[#2a2a2a] leading-snug font-normal max-w-md">
              Üretici kârlı rotayı biliyor —<br />
              ama riski hesaplayamıyor.
            </p>
            <div className="h-1.5 bg-[#c97a17] w-48" />
            <p className="font-mono text-sm text-[#6b6b6b] tracking-wide">
              Kararlar veriyle değil, sezgiyle veriliyor.
            </p>
          </div>

          {/* SAĞ: Liste */}
          <div className="lg:col-span-7">
            <ul className="flex flex-col">
              {/* 01 */}
              <li className="grid grid-cols-[40px_72px_1fr_auto] items-center gap-6 py-7 border-y-2 border-[#0a0a0a] first:border-t-2 last:border-b-2 [&:not(:first-child)]:border-t-0">
                <span className="font-mono text-base md:text-lg font-medium text-[#0a0a0a]">01</span>
                <RefreshCw className="w-12 h-12 text-[#1d4fd6]" strokeWidth={1.6} />
                <span className="text-2xl md:text-3xl font-medium text-[#0a0a0a] tracking-tight leading-snug">
                  Kur dalgalanmaları
                </span>
                <span className="hidden md:block font-mono text-xs text-[#6b6b6b] tracking-wide text-right max-w-[280px]">
                  Euro &amp; Dolar etkisi
                </span>
              </li>
              {/* 02 */}
              <li className="grid grid-cols-[40px_72px_1fr_auto] items-center gap-6 py-7 border-b border-[#0a0a0a]">
                <span className="font-mono text-base md:text-lg font-medium text-[#0a0a0a]">02</span>
                <Leaf className="w-12 h-12 text-[#0a0a0a]" strokeWidth={1.6} />
                <span className="text-2xl md:text-3xl font-medium text-[#0a0a0a] tracking-tight leading-snug">
                  Karbon ve lojistik maliyetleri
                </span>
                <span className="hidden md:block font-mono text-xs text-[#6b6b6b] tracking-wide text-right max-w-[280px]">
                  Ton-kilometre · taşıma maliyeti
                </span>
              </li>
              {/* 03 */}
              <li className="grid grid-cols-[40px_72px_1fr_auto] items-center gap-6 py-7 border-b-2 border-[#0a0a0a]">
                <span className="font-mono text-base md:text-lg font-medium text-[#0a0a0a]">03</span>
                <MapPin className="w-12 h-12 text-[#d6342a]" strokeWidth={1.6} />
                <span className="text-2xl md:text-3xl font-medium text-[#0a0a0a] tracking-tight leading-snug">
                  En yakın doğru işleyiciyi bulamama
                </span>
                <span className="hidden md:block font-mono text-xs text-[#6b6b6b] tracking-wide text-right max-w-[280px]">
                  Coğrafi körlük
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div className="flex justify-end pt-8 mt-12 border-t border-[#e6e6e6] font-mono text-xs tracking-wider text-[#6b6b6b]">
          03 / 06
        </div>
      </section>

      {/* ============================================================
          SLAYT 4 — ÇÖZÜM
      ============================================================ */}
      <section id="solution" className="py-24 px-6 lg:px-16 max-w-[1440px] mx-auto bg-white border-t-2 border-[#0a0a0a]">
        <div className="flex items-center justify-between flex-wrap gap-4 mb-10">
          <Eyebrow num="04" numColor="bg-[#1d4fd6]">Çözüm</Eyebrow>
          <HeadDot color="bg-[#1d4fd6]" label="Karar Motoru" />
        </div>

        <h2 className="text-5xl md:text-7xl font-bold tracking-tightest text-[#0a0a0a] leading-[0.94] mb-6">
          Pazar yeri değil, <span className="text-[#1d4fd6]">karar motoru.</span>
        </h2>
        <p className="text-xl md:text-2xl text-[#2a2a2a] font-normal mb-14 max-w-3xl tracking-tight">
          Hammaddeyi değil — <span className="font-semibold text-[#0a0a0a]">katma değeri</span> yönetin.
        </p>

        {/* Üç kolonlu Swiss kart sistemi — kenarlıklı, gölgesiz */}
        <div className="grid grid-cols-1 md:grid-cols-3 border-2 border-[#0a0a0a]">
          {/* 01 — Kâr Tahmini */}
          <div className="p-8 md:p-12 flex flex-col bg-white border-b-2 md:border-b-0 md:border-r-2 border-[#0a0a0a] min-h-[420px]">
            <div className="flex items-start justify-between w-full mb-9">
              <div className="w-16 h-16 bg-[#1d4fd6] flex items-center justify-center">
                <LineChart className="w-8 h-8 text-white" strokeWidth={2} />
              </div>
              <span className="font-mono text-3xl md:text-4xl font-bold text-[#1d4fd6] tracking-tightest">01</span>
            </div>
            <h3 className="text-3xl md:text-4xl font-bold text-[#0a0a0a] tracking-tight leading-tight mb-5">
              Kâr Tahmini
            </h3>
            <p className="text-base md:text-lg text-[#2a2a2a] leading-relaxed">
              Hangi rotanın ne kadar kâr getireceğini, eğitilmiş makine öğrenmesi modeli hesaplar.
            </p>
          </div>

          {/* 02 — Rota Önerisi */}
          <div className="p-8 md:p-12 flex flex-col bg-white border-b-2 md:border-b-0 md:border-r-2 border-[#0a0a0a] min-h-[420px]">
            <div className="flex items-start justify-between w-full mb-9">
              <div className="w-16 h-16 bg-[#0a0a0a] flex items-center justify-center">
                <GitBranch className="w-8 h-8 text-white" strokeWidth={2} />
              </div>
              <span className="font-mono text-3xl md:text-4xl font-bold text-[#0a0a0a] tracking-tightest">02</span>
            </div>
            <h3 className="text-3xl md:text-4xl font-bold text-[#0a0a0a] tracking-tight leading-tight mb-5">
              Rota Önerisi
            </h3>
            <p className="text-base md:text-lg text-[#2a2a2a] leading-relaxed">
              Ham satış yerine, en yüksek katma değerli işlenmiş ürünü tavsiye eder.
            </p>
          </div>

          {/* 03 — B2B Eşleşme */}
          <div className="p-8 md:p-12 flex flex-col bg-white min-h-[420px]">
            <div className="flex items-start justify-between w-full mb-9">
              <div className="w-16 h-16 bg-[#1f7a3a] flex items-center justify-center">
                <Network className="w-8 h-8 text-white" strokeWidth={2} />
              </div>
              <span className="font-mono text-3xl md:text-4xl font-bold text-[#1f7a3a] tracking-tightest">03</span>
            </div>
            <h3 className="text-3xl md:text-4xl font-bold text-[#0a0a0a] tracking-tight leading-tight mb-5">
              İşletmeden İşletmeye Eşleşme
            </h3>
            <p className="text-base md:text-lg text-[#2a2a2a] leading-relaxed">
              Üretici, işleyici ve alıcıyı skorlayarak en uygun zinciri kurar.
            </p>
          </div>
        </div>

        <div className="flex justify-end pt-8 mt-12 border-t border-[#e6e6e6] font-mono text-xs tracking-wider text-[#6b6b6b]">
          04 / 06
        </div>
      </section>

      {/* ============================================================
          SLAYT 5 — TEKNOLOJİK KANIT / CANLI VERİ
      ============================================================ */}
      <section id="models" className="py-24 px-6 lg:px-16 max-w-[1440px] mx-auto bg-white border-t-2 border-[#0a0a0a]">
        <div className="mb-8">
          <Eyebrow num="05">Canlı Veri, Gerçek Karar</Eyebrow>
        </div>

        <h2 className="text-4xl md:text-6xl font-bold tracking-tightest text-[#0a0a0a] leading-[0.96] mb-12">
          Ekrandaki rakam değil, <span className="text-[#1d4fd6]">karara giden veri.</span>
        </h2>

        <ul className="flex flex-col">
          {/* 01 — TCMB */}
          <li className="grid grid-cols-[40px_80px_1fr_auto] items-start md:items-center gap-6 py-8 border-y-2 border-[#0a0a0a]">
            <span className="font-mono text-base md:text-lg font-medium text-[#0a0a0a]">01</span>
            <RefreshCw className="w-14 h-14 text-[#1d4fd6]" strokeWidth={1.6} />
            <div className="flex flex-col gap-2">
              <div className="text-xl md:text-2xl font-medium text-[#0a0a0a] tracking-tight">
                Canlı kur, sadece ekranda durmaz —
              </div>
              <div className="text-base md:text-lg text-[#2a2a2a] leading-relaxed">
                Modelin kararını ve hesaplanan kârı anında değiştirir.
              </div>
            </div>
            <div className="hidden md:block font-mono text-xs text-[#1d4fd6] tracking-wide text-right max-w-[280px] leading-relaxed">
              Türkiye Cumhuriyet<br />
              Merkez Bankası — Veri Sistemi
            </div>
          </li>

          {/* 02 — OSM Rota */}
          <li className="grid grid-cols-[40px_80px_1fr_auto] items-start md:items-center gap-6 py-8 border-b border-[#0a0a0a]">
            <span className="font-mono text-base md:text-lg font-medium text-[#0a0a0a]">02</span>
            <Map className="w-14 h-14 text-[#0a0a0a]" strokeWidth={1.6} />
            <div className="flex flex-col gap-2">
              <div className="text-xl md:text-2xl font-medium text-[#0a0a0a] tracking-tight">
                Kuş uçuşu değil, gerçek yol mesafesi —
              </div>
              <div className="text-base md:text-lg text-[#2a2a2a] leading-relaxed">
                Karbon ayak izi resmi katsayılarla, ton-kilometre üzerinden hesaplanır.
              </div>
            </div>
            <div className="hidden md:block font-mono text-xs text-[#6b6b6b] tracking-wide text-right max-w-[280px] leading-relaxed">
              Açık Kaynaklı Rota<br />
              Servisi — Mesafe Matrisi
            </div>
          </li>

          {/* 03 — Konum */}
          <li className="grid grid-cols-[40px_80px_1fr_auto] items-start md:items-center gap-6 py-8 border-b-2 border-[#0a0a0a]">
            <span className="font-mono text-base md:text-lg font-medium text-[#0a0a0a]">03</span>
            <Locate className="w-14 h-14 text-[#1f7a3a]" strokeWidth={1.6} />
            <div className="flex flex-col gap-2">
              <div className="text-xl md:text-2xl font-medium text-[#0a0a0a] tracking-tight">
                Karbon hesabından bağımsız —
              </div>
              <div className="text-base md:text-lg text-[#2a2a2a] leading-relaxed">
                Konum tabanlı en yakın işleyici tesis tespiti.
              </div>
            </div>
            <div className="hidden md:block font-mono text-xs text-[#1f7a3a] tracking-wide text-right max-w-[280px] leading-relaxed">
              Açık Sokak Haritası —<br />
              Adres ve Konum Servisi
            </div>
          </li>
        </ul>

        <div className="flex justify-end pt-8 mt-12 border-t border-[#e6e6e6] font-mono text-xs tracking-wider text-[#6b6b6b]">
          05 / 06
        </div>
      </section>

      {/* ============================================================
          SLAYT 6 — EKOSİSTEM & KAPANIŞ
      ============================================================ */}
      <section id="ecosystem" className="py-24 px-6 lg:px-16 max-w-[1440px] mx-auto bg-white border-t-2 border-[#0a0a0a]">
        <div className="flex items-center justify-between flex-wrap gap-4 mb-10">
          <Eyebrow num="06" numColor="bg-[#1f7a3a]">Kazanan Bir Ekosistem</Eyebrow>
          <HeadDot color="bg-[#1f7a3a]" label="Üç Taraf — Tek Zincir" />
        </div>

        {/* Zincir akışı — Swiss kenarlıklı */}
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr_auto_1fr] items-center border-2 border-[#0a0a0a] mb-12">
          {/* Halka 1 */}
          <div className="text-center flex flex-col items-center gap-5 py-12 px-6 bg-white">
            <span className="bg-[#d6342a] text-white text-[11px] font-medium px-3 py-1.5 font-mono uppercase tracking-widest">
              Birinci Halka
            </span>
            <Mountain className="w-20 h-20 text-[#d6342a]" strokeWidth={1.6} />
            <h3 className="text-2xl md:text-3xl font-bold text-[#0a0a0a] tracking-tight leading-tight">
              Hammadde<br />Üreticisi
            </h3>
            <p className="font-mono text-xs text-[#6b6b6b] tracking-wide">
              Pomza · perlit · çekirdek
            </p>
          </div>

          {/* Ok */}
          <div className="hidden md:flex items-center justify-center px-4 text-[#0a0a0a]">
            <ArrowRight className="w-9 h-9" strokeWidth={1.6} />
          </div>

          {/* Halka 2 */}
          <div className="text-center flex flex-col items-center gap-5 py-12 px-6 bg-white border-y-2 md:border-y-0 md:border-x-2 border-[#0a0a0a]">
            <span className="bg-[#1d4fd6] text-white text-[11px] font-medium px-3 py-1.5 font-mono uppercase tracking-widest">
              İkinci Halka
            </span>
            <Factory className="w-20 h-20 text-[#1d4fd6]" strokeWidth={1.6} />
            <h3 className="text-2xl md:text-3xl font-bold text-[#0a0a0a] tracking-tight leading-tight">
              İşleyici<br />Tesis
            </h3>
            <p className="font-mono text-xs text-[#6b6b6b] tracking-wide">
              Mikronize · genleştirilmiş
            </p>
          </div>

          {/* Ok */}
          <div className="hidden md:flex items-center justify-center px-4 text-[#0a0a0a]">
            <ArrowRight className="w-9 h-9" strokeWidth={1.6} />
          </div>

          {/* Halka 3 */}
          <div className="text-center flex flex-col items-center gap-5 py-12 px-6 bg-white">
            <span className="bg-[#1f7a3a] text-white text-[11px] font-medium px-3 py-1.5 font-mono uppercase tracking-widest">
              Üçüncü Halka
            </span>
            <Globe2 className="w-20 h-20 text-[#1f7a3a]" strokeWidth={1.6} />
            <h3 className="text-2xl md:text-3xl font-bold text-[#0a0a0a] tracking-tight leading-tight">
              Küresel<br />Alıcı
            </h3>
            <p className="font-mono text-xs text-[#6b6b6b] tracking-wide">
              Almanya · Hollanda · iç pazar
            </p>
          </div>
        </div>

        {/* Kapanış sloganı */}
        <p className="text-3xl md:text-5xl lg:text-6xl font-medium tracking-tightest text-[#0a0a0a] leading-[1.15]">
          Biz{' '}
          <span className="line-through decoration-[#d6342a] decoration-[4px] text-[#6b6b6b] font-normal">
            aracıları
          </span>{' '}
          değil,<br />
          <span className="font-bold text-[#d6342a]">bilgisizliği</span> ortadan kaldırıyoruz.
        </p>

        {/* CTA — Karar Motoru / Geo */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-16">
          <Link
            to="/dashboard"
            className="group relative overflow-hidden rounded-2xl bg-[#0a0a0a] text-white p-10 md:p-14 flex flex-col justify-between min-h-[260px] hover:shadow-2xl transition-all"
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
                <ArrowUpRight className="w-6 h-6 text-[#0a0a0a]" strokeWidth={2.5} />
              </div>
            </div>
          </Link>

          <Link
            to="/dashboard/geo"
            className="group rounded-2xl bg-white text-[#0a0a0a] p-10 md:p-14 flex flex-col justify-between min-h-[260px] border-2 border-[#0a0a0a] hover:shadow-lg transition-all"
          >
            <div>
              <div className="text-xs font-semibold uppercase tracking-widest text-[#6b6b6b] mb-3">Görselleştirme</div>
              <h3 className="text-3xl md:text-4xl font-bold tracking-tight leading-tight">
                Geo &amp; Karbon<br />Haritası
              </h3>
            </div>
            <div className="self-end">
              <div className="w-14 h-14 rounded-xl bg-[#0a0a0a] flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <ArrowUpRight className="w-6 h-6 text-white" strokeWidth={2.5} />
              </div>
            </div>
          </Link>
        </div>

        <div className="flex justify-end pt-8 mt-12 border-t border-[#e6e6e6] font-mono text-xs tracking-wider text-[#6b6b6b]">
          06 / 06
        </div>
      </section>

      {/* ─────────────── FOOTER (KORUNDU) ─────────────── */}
      <footer id="about" className="bg-r2v-charcoal text-white/75 py-14 px-6 lg:px-16 mt-12">
        <div className="max-w-[1440px] mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-sm">
          <span className="font-semibold text-white">Raw2Value · Kapadokya Hackathon — 2026</span>
          <span className="font-mono text-white/50">seed=42 · build v0.4.0</span>
        </div>
      </footer>
    </div>
  );
}
