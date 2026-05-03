import { Link, useLocation } from 'react-router-dom';
import { Search, Map } from 'lucide-react';

export default function TopNav() {
  const location = useLocation();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 bg-r2v-base border-b border-r2v-charcoal/10 flex items-center px-6 gap-4">
      {/* Logo */}
      <Link to="/" className="flex items-center gap-2 shrink-0">
        <div className="w-6 h-6 rounded-full bg-r2v-terracotta flex items-center justify-center">
          <div className="w-2.5 h-2.5 rounded-full bg-white" />
        </div>
        <span className="font-bold text-r2v-charcoal tracking-tight text-base">Raw2Value <span className="font-light opacity-40">AI</span></span>
      </Link>

      {/* Search — center */}
      <div className="flex-1 flex justify-center">
        <div className="w-full max-w-md flex items-center gap-2 bg-white border border-r2v-charcoal/10 rounded-full px-4 py-1.5 focus-within:border-r2v-charcoal/30 transition-colors shadow-sm">
          <Search className="w-3.5 h-3.5 text-r2v-charcoal/40 shrink-0" />
          <input
            type="text"
            placeholder="Senaryo veya hammadde ara..."
            className="bg-transparent border-none focus:ring-0 outline-none text-sm text-r2v-charcoal w-full placeholder:text-r2v-charcoal/35"
          />
        </div>
      </div>

      {/* Right: GeoCarbon link + user */}
      <div className="flex items-center gap-3 shrink-0">
        <Link
          to="/dashboard/geo"
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest transition-colors ${
            location.pathname === '/dashboard/geo'
              ? 'bg-r2v-charcoal text-white'
              : 'text-r2v-charcoal/60 hover:text-r2v-charcoal hover:bg-r2v-charcoal/5'
          }`}
        >
          <Map className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">GeoCarbon</span>
        </Link>

        <div className="h-5 w-px bg-r2v-charcoal/10" />

        <div className="flex items-center gap-2 cursor-pointer group">
          <div className="text-right hidden sm:block">
            <p className="text-xs font-bold text-r2v-charcoal group-hover:text-r2v-terracotta transition-colors leading-none">Kullanıcı</p>
            <p className="text-[9px] uppercase tracking-widest text-r2v-charcoal/40 font-bold mt-0.5">İşleyici</p>
          </div>
          <div className="w-8 h-8 rounded-full bg-r2v-charcoal text-white flex items-center justify-center font-mono text-xs font-bold">
            KL
          </div>
        </div>
      </div>
    </header>
  );
}
