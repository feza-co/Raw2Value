import { Link, useLocation } from 'react-router-dom';
import { Search, Map } from 'lucide-react';

export default function TopNav() {
  const location = useLocation();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-16 bg-white border-b border-r2v-line flex items-center px-6 gap-5 shadow-[0_1px_2px_rgba(31,34,38,0.04)]">
      {/* Logo */}
      <Link to="/" className="flex items-center gap-2.5 shrink-0">
        <div className="w-8 h-8 rounded-full bg-r2v-terracotta flex items-center justify-center shadow-sm">
          <div className="w-3 h-3 rounded-full bg-white" />
        </div>
        <span className="font-bold text-r2v-charcoal tracking-tight text-base">
          Raw2Value <span className="font-normal text-r2v-muted">AI</span>
        </span>
      </Link>

      {/* Search — center */}
      <div className="flex-1 flex justify-center">
        <div className="w-full max-w-md flex items-center gap-2.5 bg-r2v-soft border border-r2v-line rounded-full px-4 py-2 focus-within:bg-white focus-within:border-r2v-charcoal/30 focus-within:shadow-sm transition-all">
          <Search className="w-4 h-4 text-r2v-muted shrink-0" />
          <input
            type="text"
            placeholder="Senaryo veya hammadde ara..."
            className="bg-transparent border-none focus:ring-0 outline-none text-sm text-r2v-charcoal w-full placeholder:text-r2v-muted"
          />
        </div>
      </div>

      {/* Right: GeoCarbon link + user */}
      <div className="flex items-center gap-3 shrink-0">
        <Link
          to="/dashboard/geo"
          className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
            location.pathname === '/dashboard/geo'
              ? 'bg-r2v-charcoal text-white shadow-sm'
              : 'text-r2v-charcoal/75 hover:text-r2v-charcoal hover:bg-r2v-soft'
          }`}
        >
          <Map className="w-4 h-4" />
          <span className="hidden sm:inline">GeoCarbon</span>
        </Link>

        <div className="h-6 w-px bg-r2v-line" />

        <div className="flex items-center gap-2.5 cursor-pointer group">
          <div className="text-right hidden sm:block leading-tight">
            <p className="text-sm font-semibold text-r2v-charcoal group-hover:text-r2v-terracotta transition-colors">
              Kullanıcı
            </p>
            <p className="text-[11px] text-r2v-muted font-medium">İşleyici</p>
          </div>
          <div className="w-9 h-9 rounded-full bg-r2v-charcoal text-white flex items-center justify-center font-mono text-sm font-bold">
            KL
          </div>
        </div>
      </div>
    </header>
  );
}
