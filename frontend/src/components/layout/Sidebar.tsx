import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'

const NAV = [
  { to: '/cockpit', label: 'Kokpit', icon: '⬡' },
  { to: '/cockpit/what-if', label: 'What-If', icon: '⇌' },
  { to: '/history', label: 'Geçmiş', icon: '○' },
  { to: '/processors', label: 'İşlemciler', icon: '◉' },
  { to: '/org', label: 'Organizasyon', icon: '▣' },
  { to: '/settings', label: 'Ayarlar', icon: '◈' },
]

export default function Sidebar() {
  return (
    <aside className="fixed top-0 left-0 bottom-0 w-16 hover:w-56 group z-40 bg-white border-r border-slate-200 shadow-sm transition-all duration-300 ease-out overflow-hidden">
      <div className="flex flex-col h-full pt-16">
        <div className="px-4 py-6 border-b border-slate-100 bg-slate-50/50">
          <span className="font-display font-bold text-slate-900 text-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 delay-100">
            Raw2Value
          </span>
        </div>
        <nav className="flex flex-col gap-2 p-3 mt-2">
          {NAV.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/cockpit'}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-4 px-3 py-3 rounded-xl transition-all duration-200 relative',
                  isActive
                    ? 'bg-amber-50 text-amber-600 font-semibold'
                    : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50',
                )
              }
            >
              <span className="w-6 text-center text-lg flex-shrink-0">{icon}</span>
              <span className="font-body text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 delay-100">
                {label}
              </span>
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  )
}
