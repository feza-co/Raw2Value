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
    <div className="bg-white text-[#0a0a0a] flex h-screen overflow-hidden font-sans antialiased">
      {/* SIDEBAR — Swiss */}
      <aside className="w-72 bg-white flex-col hidden md:flex z-20 shrink-0 border-r-2 border-[#0a0a0a]">
        <div className="h-20 flex items-center px-8 border-b-2 border-[#0a0a0a]">
          <Link to="/" className="flex items-center gap-3">
            <div className="grid grid-cols-2 grid-rows-2 w-8 h-8 border-2 border-[#0a0a0a]">
              <div className="bg-white" />
              <div className="bg-[#0a0a0a]" />
              <div className="bg-[#1d4fd6]" />
              <div className="bg-[#d6342a]" />
            </div>
            <span className="text-[#0a0a0a] font-bold text-xl tracking-tight">
              Raw2Value <span className="font-normal text-[#6b6b6b]">AI</span>
            </span>
          </Link>
        </div>

        <nav className="flex-1 overflow-y-auto py-8">
          <div className="px-8 font-mono text-[10px] font-semibold text-[#6b6b6b] uppercase tracking-widest mb-4">Modüller</div>
          <ul className="space-y-1 px-4">
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.path);
              return (
                <li key={item.id}>
                  <Link
                    to={item.path}
                    className={`flex items-center gap-3 px-4 py-2.5 transition-colors ${
                      isActive
                        ? 'bg-[#0a0a0a] text-white font-semibold'
                        : 'text-[#2a2a2a] hover:bg-[#f4f4f4] hover:text-[#0a0a0a] font-medium border border-transparent hover:border-[#0a0a0a]'
                    }`}
                  >
                    <item.icon className={`w-4 h-4 ${isActive ? 'text-[#d6342a]' : ''}`} />
                    <span className="text-sm tracking-wide">{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>

          <div className="mt-12 px-8 font-mono text-[10px] font-semibold text-[#6b6b6b] uppercase tracking-widest mb-4">Ayarlar</div>
          <ul className="space-y-1 px-4">
            <li>
              <Link to="/admin" className="flex items-center gap-3 px-4 py-2.5 text-[#2a2a2a] hover:bg-[#f4f4f4] transition-colors font-medium border border-transparent hover:border-[#0a0a0a]">
                <Settings className="w-4 h-4" />
                <span className="text-sm tracking-wide">Admin</span>
              </Link>
            </li>
          </ul>
        </nav>
      </aside>

      {/* MAIN CONTENT WRAPPER */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* TOPBAR — Swiss */}
        <header className="h-20 bg-white flex items-center justify-between px-10 z-10 shrink-0 border-b-2 border-[#0a0a0a]">
          <div className="flex items-center w-96 bg-white border border-[#0a0a0a] px-4 py-3 focus-within:ring-2 focus-within:ring-[#1d4fd6]/30 transition-all">
            <Search className="w-4 h-4 text-[#6b6b6b]" />
            <input
              type="text"
              placeholder="Senaryo veya hammadde ara..."
              className="bg-transparent border-none focus:ring-0 outline-none text-sm font-medium text-[#0a0a0a] w-full ml-3 placeholder:text-[#6b6b6b]"
            />
          </div>

          <div className="flex items-center gap-6">
            <button className="relative text-[#0a0a0a] hover:text-[#d6342a] transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-[#d6342a] border-2 border-white"></span>
            </button>

            <div className="h-6 w-px bg-[#0a0a0a]"></div>

            <div className="flex items-center gap-4 cursor-pointer group">
              <div className="text-right">
                <p className="text-sm font-bold text-[#0a0a0a] group-hover:text-[#d6342a] transition-colors">Kullanıcı</p>
                <p className="text-[10px] uppercase tracking-widest text-[#6b6b6b] font-mono font-semibold mt-0.5">İşleyici</p>
              </div>
              <div className="w-10 h-10 bg-[#0a0a0a] text-white flex items-center justify-center font-mono font-bold text-sm">
                KL
              </div>
            </div>
          </div>
        </header>

        {/* PAGE CONTENT */}
        <main className="flex-1 overflow-y-auto bg-white px-10 pt-4">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
