import { useEffect } from 'react';
import { Link } from 'react-router-dom';

// Pumice/volcanic rock fractal noise texture encoded as SVG data URI
const PUMICE_TEXTURE = `url("data:image/svg+xml,${encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240">' +
  '<filter id="p"><feTurbulence type="fractalNoise" baseFrequency="0.78 0.85" numOctaves="5" seed="9" stitchTiles="stitch"/>' +
  '<feColorMatrix type="matrix" values="0.12 0 0 0 0.54 0.12 0 0 0 0.48 0.12 0 0 0 0.40 0 0 0 1 0"/></filter>' +
  '<rect width="240" height="240" filter="url(#p)"/></svg>'
)}")`;

export default function LandingPage() {
  useEffect(() => {
    const handleScroll = () => {
      const header = document.getElementById('main-header');
      const navContainer = document.getElementById('nav-container');
      const navHalo = document.getElementById('nav-halo');
      const navBg = document.getElementById('nav-bg');
      const headerInner = document.getElementById('header-inner');
      const topBanner = document.getElementById('top-banner');
      
      const scrollY = window.scrollY;
      
      if (!header || !navContainer || !navHalo || !navBg || !headerInner || !topBanner) return;

      if (scrollY > 50) {
        topBanner.style.marginTop = `-${topBanner.offsetHeight}px`;
        
        navContainer.classList.add('pt-4');
        navContainer.classList.remove('pt-0', 'px-0');
        navContainer.classList.add('px-4');
        
        header.classList.remove('max-w-full');
        header.classList.add('max-w-4xl');
        
        navBg.classList.remove('bg-transparent', 'rounded-none');
        navBg.classList.add('bg-white/95', 'rounded-full', 'shadow-md');
        
        navHalo.classList.remove('opacity-0', 'rounded-none');
        navHalo.classList.add('opacity-100', 'rounded-full');
        
        headerInner.classList.remove('py-5', 'px-6');
        headerInner.classList.add('py-2', 'px-8');

      } else {
        topBanner.style.marginTop = '0px';

        navContainer.classList.remove('pt-4', 'px-4');
        navContainer.classList.add('pt-0', 'px-0');
        
        header.classList.remove('max-w-4xl');
        header.classList.add('max-w-full');
        
        navBg.classList.remove('bg-white/95', 'rounded-full', 'shadow-md');
        navBg.classList.add('bg-transparent', 'rounded-none');
        
        navHalo.classList.remove('opacity-100', 'rounded-full');
        navHalo.classList.add('opacity-0', 'rounded-none');
        
        headerInner.classList.remove('py-2', 'px-8');
        headerInner.classList.add('py-5', 'px-6');
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div
      className="antialiased overflow-x-hidden relative"
      style={{ backgroundColor: '#8a7a6a', backgroundImage: PUMICE_TEXTURE, backgroundSize: '240px 240px' }}
    >
      {/* Top Banner */}
      <div id="top-banner" className="bg-r2v-charcoal text-[#FAF9F6] text-center py-2 text-xs font-medium tracking-wide transition-all duration-500">
        <a className="hover:text-r2v-terracotta transition-colors flex items-center justify-center gap-2" href="#">
          TR71 Bölgesi Akıllı Tedarik Zinciri Karar Motoru Canlı Yayında
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" strokeLinecap="round" strokeLinejoin="round"></path>
          </svg>
        </a>
      </div>

      {/* Floating Navbar */}
      <div id="nav-container" className="fixed top-8 left-0 right-0 z-50 flex justify-center transition-all duration-500 px-0 pt-0">
        <header id="main-header" className="relative w-full max-w-full transition-all duration-500">
          <div id="nav-halo" className="absolute -inset-y-1 -inset-x-2 bg-r2v-base/40 rounded-none opacity-0 backdrop-blur-md transition-all duration-500 -z-20 border border-r2v-charcoal/5 shadow-sm"></div>
          <div id="nav-bg" className="absolute inset-0 bg-transparent rounded-none transition-all duration-500 -z-10"></div>
          
          <div id="header-inner" className="px-6 py-5 flex justify-between items-center transition-all duration-500 relative z-10 w-full">
            <a className="text-r2v-charcoal hover:text-r2v-terracotta font-bold text-xl flex items-center gap-2 tracking-tight transition-colors duration-300" href="#" id="logo-text">
              <svg className="w-6 h-6 text-r2v-terracotta" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"></path><circle cx="12" cy="12" r="5" fill="#FAF9F6"></circle></svg>
              Raw2Value
            </a>
            
            <nav className="hidden md:flex items-center" id="nav-links">
              <a href="#modeller" className="px-5 text-r2v-charcoal/80 hover:text-r2v-charcoal text-sm font-medium transition-colors">Modeller</a>
              <div className="h-4 w-px bg-r2v-charcoal/20 nav-separator transition-colors duration-300"></div>
              <a href="#cockpit" className="px-5 text-r2v-charcoal/80 hover:text-r2v-charcoal text-sm font-medium transition-colors">Cockpit</a>
              <div className="h-4 w-px bg-r2v-charcoal/20 nav-separator transition-colors duration-300"></div>
              <a href="#kanit" className="px-5 text-r2v-charcoal/80 hover:text-r2v-charcoal text-sm font-medium transition-colors">Model Kanıtı</a>
              <div className="h-4 w-px bg-r2v-charcoal/20 nav-separator transition-colors duration-300"></div>
              <a href="#pilot" className="px-5 text-r2v-charcoal/80 hover:text-r2v-charcoal text-sm font-medium transition-colors">Pilot Program</a>
            </nav>

            <div className="flex items-center gap-4">
              {/* IMPORTANT: Link to the Dashboard application */}
              <Link to="/dashboard" id="nav-btn" className="bg-r2v-charcoal text-white px-6 py-2 rounded-full font-medium hover:bg-r2v-charcoal/90 transition-colors text-sm shadow-sm">
                Sisteme Giriş
              </Link>
            </div>
          </div>
        </header>
      </div>

      <main>
        {/* Floating Boxed Hero Section */}
        <div className="pt-32 pb-12 px-4 md:px-8">
          <section className="relative h-[80vh] min-h-[600px] flex items-center justify-center overflow-hidden rounded-[2.5rem] max-w-[1400px] mx-auto shadow-2xl">
            <div className="absolute inset-0 z-0 bg-r2v-charcoal">
              <img alt="Raw2Value AI Operations" className="w-full h-full object-cover object-center opacity-75" src="assets/hero_kapadokya.png"/>
              <div className="absolute inset-0 bg-gradient-to-t from-r2v-charcoal/80 via-r2v-charcoal/40 to-transparent"></div>
              <div className="absolute inset-x-0 top-0 h-2/3 bg-gradient-to-b from-r2v-terracotta/20 to-transparent mix-blend-overlay"></div>
              <div className="absolute inset-0 bg-r2v-earth/20 mix-blend-multiply"></div>
            </div>
            
            <div className="relative z-10 text-center px-4 max-w-4xl mx-auto mt-10">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/30 bg-white/10 backdrop-blur text-white text-xs font-medium mb-8 shadow-sm">
                <svg className="w-4 h-4 text-r2v-terracotta" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
                TR71 Akıllı Karar Motoru
              </div>
              <h1 className="text-5xl md:text-7xl lg:text-8xl font-light text-white tracking-tight leading-[1.05]">
                Don't sell the rock.<br/><span className="font-medium text-r2v-base drop-shadow-lg">Sell the value.</span>
              </h1>
              <p className="mt-8 text-lg md:text-xl text-r2v-base/90 font-light max-w-2xl mx-auto drop-shadow-md">
                Kapadokya hammaddeleri için ham satıştan katma değerli rotaya geçişi optimize eden tedarik zinciri karar motoru.
              </p>
            </div>
            
            <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 text-white/80 flex flex-col items-center gap-2 z-10">
              <svg className="w-6 h-6 animate-bounce" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M19.5 13.5L12 21m0 0l-7.5-7.5M12 21V3" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </div>
          </section>
        </div>

        {/* Mission Statement Section */}
        <section id="modeller" className="bg-r2v-surface py-32 px-6 border-y border-r2v-charcoal/5">
          <div className="max-w-6xl mx-auto text-center">
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-light leading-[1.15] tracking-tight text-r2v-earth">
              Raw2Value AI bir ilan platformu <span className="text-r2v-terracotta italic font-medium">değildir.</span><br/>
              Katma değerli işleme rotası öneren<br/>
              ML tabanlı bir <span className="font-semibold text-r2v-charcoal">karar motorudur.</span>
            </h2>
            
            <div className="mt-24 text-left grid md:grid-cols-3 gap-8">
              <div className="bg-r2v-base p-10 rounded-[2rem] shadow-sm border border-r2v-charcoal/5 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-r2v-terracotta/10 text-r2v-terracotta flex items-center justify-center rounded-xl mb-6">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                </div>
                <h3 className="text-xl font-semibold mb-4 text-r2v-charcoal">Value Uplift Prediction</h3>
                <p className="text-r2v-charcoal/70 font-light leading-relaxed">
                  Hammadde ve işleme rotasına göre beklenen değer artışı ve net kârı tahmin eden regresyon modeli. Ham satış ile katma değerli ürün arasındaki gerçek farkı hesaplar.
                </p>
              </div>
              <div className="bg-r2v-base p-10 rounded-[2rem] shadow-sm border border-r2v-charcoal/5 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-r2v-green/10 text-r2v-green flex items-center justify-center rounded-xl mb-6">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
                </div>
                <h3 className="text-xl font-semibold mb-4 text-r2v-charcoal">Route Recommendation</h3>
                <p className="text-r2v-charcoal/70 font-light leading-relaxed">
                  Pomza, perlit ve kabak çekirdeği için ham satıştan katma değerli alternatiflere en uygun işleme rotasını seçen sınıflandırıcı.
                </p>
              </div>
              <div className="bg-r2v-base p-10 rounded-[2rem] shadow-sm border border-r2v-charcoal/5 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-r2v-earth/10 text-r2v-earth flex items-center justify-center rounded-xl mb-6">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                </div>
                <h3 className="text-xl font-semibold mb-4 text-r2v-charcoal">Supplier-Buyer Match</h3>
                <p className="text-r2v-charcoal/70 font-light leading-relaxed">
                  Lojistik mesafe, işletme kapasitesi ve hedeflenen kalite kriterlerini optimize ederek en kârlı Üretici–İşleyici–Alıcı kombinasyonunu sıralar.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Model Lab / Grid Section */}
        <section id="kanit" className="bg-r2v-surface py-24 px-6 border-y border-r2v-charcoal/5">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-r2v-charcoal/10 bg-white text-r2v-charcoal text-xs font-bold uppercase tracking-widest mb-6 shadow-sm">
                AI Evidence
              </div>
              <h2 className="text-3xl md:text-5xl font-light text-r2v-charcoal mb-6">Model Lab & Kanıtlar</h2>
              <p className="text-lg text-r2v-charcoal/60 font-light max-w-2xl mx-auto">
                Hackathon projelerinde güvenilirlik esastır. Modellerimizin doğruluğunu, ablation çalışmalarını ve feature importance skorlarını şeffafça sunuyoruz.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="bg-r2v-base p-8 rounded-3xl shadow-sm border border-r2v-charcoal/5">
                <div className="w-14 h-14 bg-r2v-surface rounded-2xl flex items-center justify-center mb-6 text-r2v-earth">
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                </div>
                <h4 className="text-lg font-semibold text-r2v-charcoal mb-3">Feature Importance</h4>
                <p className="text-sm text-r2v-charcoal/70 font-light leading-relaxed">
                  Maliyet, kur ve mesafe verilerinin model kararındaki ağırlığını SHAP ile şeffaf bir şekilde analiz edin. XGBoost ve LightGBM altyapısı.
                </p>
              </div>
              <div className="bg-r2v-base p-8 rounded-3xl shadow-sm border border-r2v-charcoal/5">
                <div className="w-14 h-14 bg-r2v-surface rounded-2xl flex items-center justify-center mb-6 text-r2v-earth">
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                </div>
                <h4 className="text-lg font-semibold text-r2v-charcoal mb-3">Ablation Çalışması</h4>
                <p className="text-sm text-r2v-charcoal/70 font-light leading-relaxed">
                  Zorunlu kuralların (TCMB canlı kur, CO2) modelden çıkarıldığında tahmin başarısının (R²) nasıl düştüğünü kanıtlayan testler.
                </p>
              </div>
              <div className="bg-r2v-base p-8 rounded-3xl shadow-sm border border-r2v-charcoal/5">
                <div className="w-14 h-14 bg-r2v-surface rounded-2xl flex items-center justify-center mb-6 text-r2v-earth">
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>
                </div>
                <h4 className="text-lg font-semibold text-r2v-charcoal mb-3">Veri Çoğaltma</h4>
                <p className="text-sm text-r2v-charcoal/70 font-light leading-relaxed">
                  120 gerçek referans satırı ve domain-informed synthetic augmentation ile üretilen 1.500 senaryo ile eğitilmiş modeller.
                </p>
              </div>
              <div className="bg-r2v-base p-8 rounded-3xl shadow-sm border border-r2v-charcoal/5">
                <div className="w-14 h-14 bg-r2v-surface rounded-2xl flex items-center justify-center mb-6 text-r2v-green">
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                </div>
                <h4 className="text-lg font-semibold text-r2v-charcoal mb-3">Yüksek Doğruluk</h4>
                <p className="text-sm text-r2v-charcoal/70 font-light leading-relaxed">
                  Baseline Random Forest modellerinin ötesinde, CatBoost ve XGBoost ile optimize edilmiş %84 üzeri R-kare skorları.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Massive CTA Blocks */}
        <section className="bg-r2v-base max-w-[100%] px-6 py-24">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row gap-6">
            <Link to="/evidence" className="flex-1 bg-r2v-surface p-12 rounded-[2rem] flex flex-col justify-between group hover:shadow-lg transition-all border border-r2v-charcoal/5 h-64 relative overflow-hidden">
              <div className="relative z-10">
                <div className="text-sm font-semibold uppercase tracking-widest text-r2v-charcoal/50 mb-2">Dokümantasyon</div>
                <h3 className="text-3xl font-light text-r2v-charcoal">Teknik Altyapı</h3>
              </div>
              <div className="relative z-10 self-end">
                <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                  <svg className="w-6 h-6 text-r2v-charcoal" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                </div>
              </div>
            </Link>
            <Link to="/dashboard" className="flex-1 bg-r2v-charcoal p-12 rounded-[2rem] flex flex-col justify-between group hover:shadow-2xl hover:shadow-r2v-charcoal/20 transition-all h-64 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-r2v-terracotta/10 to-transparent"></div>
              <div className="relative z-10">
                <div className="text-sm font-semibold uppercase tracking-widest text-white/50 mb-2">Başlangıç</div>
                <h3 className="text-3xl font-light text-white">Sistemi İncele</h3>
              </div>
              <div className="relative z-10 self-end">
                <div className="w-12 h-12 rounded-full bg-r2v-terracotta flex items-center justify-center shadow-md group-hover:scale-110 transition-transform">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                </div>
              </div>
            </Link>
          </div>
        </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="bg-r2v-charcoal text-white/70 py-20 px-6 text-sm rounded-t-[3rem] border-t border-white/5">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
          <div>
            <a className="text-white font-bold text-2xl flex items-center gap-2 tracking-tight mb-6" href="#">
              <svg className="w-6 h-6 text-r2v-terracotta" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"></path><circle cx="12" cy="12" r="5" fill="#FAF9F6"></circle></svg>
              Raw2Value AI
            </a>
            <p className="mb-4 text-white/50 text-xs">© 2026 Kapadokya Hackathon<br/>Kategori 3: Akıllı Tedarik Zinciri.</p>
          </div>
          <div>
            <h5 className="font-semibold mb-6 text-white text-xs tracking-widest uppercase">Modeller</h5>
            <ul className="space-y-3 font-medium">
              <li><Link className="hover:text-white transition-colors" to="/dashboard">Value Uplift Model</Link></li>
              <li><Link className="hover:text-white transition-colors" to="/dashboard">Route Recommendation</Link></li>
            </ul>
          </div>
        </div>
      </footer>
    </div>
  );
}
