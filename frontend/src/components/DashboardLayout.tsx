import { Link, Outlet, useLocation } from 'react-router-dom';
import {
  FlaskConical,
  Target,
  Map as MapIcon,
  SlidersHorizontal,
  Settings,
  Search,
  Bell,
} from 'lucide-react';

const navItems = [
  { id: 'material', label: 'Material Analyzer', icon: FlaskConical, path: '/dashboard/material' },
  { id: 'cockpit', label: 'AI Decision Cockpit', icon: Target, path: '/dashboard/cockpit' },
  { id: 'geo', label: 'GeoCarbon Map', icon: MapIcon, path: '/dashboard/geo' },
  { id: 'whatif', label: 'What-if Simulator', icon: SlidersHorizontal, path: '/dashboard/whatif' },
];

export default function DashboardLayout() {
  const location = useLocation();

  return (
    <div className="bg-r2v-base text-r2v-charcoal flex h-screen overflow-hidden font-sans antialiased">
      {/* SIDEBAR */}
      <aside className="w-72 bg-r2v-base flex-col hidden md:flex z-20 shrink-0 border-r border-r2v-charcoal/10">
        <div className="h-20 flex items-center px-8">
          <Link to="/" className="text-r2v-charcoal font-bold text-2xl flex items-center gap-2 tracking-tight">
            Raw2Value <span className="font-light opacity-50">AI</span>
          </Link>
        </div>

        <nav className="flex-1 overflow-y-auto py-8">
          <div className="px-8 text-[10px] font-bold text-r2v-charcoal/40 uppercase tracking-widest mb-4">Modüller</div>
          <ul className="space-y-1 px-4">
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.path);
              return (
                <li key={item.id}>
                  <Link
                    to={item.path}
                    className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-white text-r2v-charcoal shadow-sm font-bold'
                        : 'text-r2v-charcoal/60 hover:bg-white/50 hover:text-r2v-charcoal font-medium'
                    }`}
                  >
                    <item.icon className={`w-4 h-4 ${isActive ? 'text-r2v-terracotta' : ''}`} />
                    <span className="text-sm tracking-wide">{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>

          <div className="mt-12 px-8 text-[10px] font-bold text-r2v-charcoal/40 uppercase tracking-widest mb-4">Ayarlar</div>
          <ul className="space-y-1 px-4">
            <li>
              <Link to="/admin" className="flex items-center gap-3 px-4 py-2 rounded-lg text-r2v-charcoal/60 hover:bg-white/50 transition-colors font-medium">
                <Settings className="w-4 h-4" />
                <span className="text-sm tracking-wide">Admin</span>
              </Link>
            </li>
          </ul>
        </nav>
      </aside>

      {/* MAIN CONTENT WRAPPER */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* TOPBAR */}
        <header className="h-20 bg-r2v-base flex items-center justify-between px-10 z-10 shrink-0">
          <div className="flex items-center w-96 bg-white rounded-none px-4 py-3 border-b-2 border-r2v-charcoal/10 focus-within:border-r2v-charcoal transition-colors">
            <Search className="w-4 h-4 text-r2v-charcoal/50" />
            <input
              type="text"
              placeholder="Senaryo veya hammadde ara..."
              className="bg-transparent border-none focus:ring-0 outline-none text-sm font-medium text-r2v-charcoal w-full ml-3 placeholder:text-r2v-charcoal/40"
            />
          </div>

          <div className="flex items-center gap-6">
            <button className="relative text-r2v-charcoal/60 hover:text-r2v-charcoal transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-r2v-terracotta rounded-full border-2 border-white"></span>
            </button>

            <div className="h-6 w-px bg-r2v-charcoal/10"></div>

            <div className="flex items-center gap-4 cursor-pointer group">
              <div className="text-right">
                <p className="text-sm font-bold text-r2v-charcoal group-hover:text-r2v-terracotta transition-colors">Kullanıcı</p>
                <p className="text-[10px] uppercase tracking-widest text-r2v-charcoal/50 font-bold mt-0.5">İşleyici</p>
              </div>
              <div className="w-10 h-10 bg-r2v-charcoal text-white flex items-center justify-center font-mono font-light text-lg">
                KL
              </div>
            </div>
          </div>
        </header>

        {/* PAGE CONTENT */}
        <main className="flex-1 overflow-y-auto bg-r2v-base px-10 pt-4">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
