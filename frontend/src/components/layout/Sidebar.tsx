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
    <aside className="fixed top-0 left-0 bottom-0 w-16 hover:w-56 group z-40 bg-ink transition-all duration-300 ease-out-expo overflow-hidden">
      <div className="flex flex-col h-full pt-16">
        <div className="px-4 py-6 border-b border-white/10">
          <span className="font-display text-parchment text-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 delay-100">
            Raw2Value
          </span>
        </div>
        <nav className="flex flex-col gap-1 p-2 mt-2">
          {NAV.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/cockpit'}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-4 px-3 py-3 rounded-sm transition-colors duration-150 relative',
                  isActive
                    ? 'text-amber before:absolute before:left-0 before:top-2 before:bottom-2 before:w-0.5 before:bg-amber'
                    : 'text-stone-300 hover:text-parchment',
                )
              }
            >
              <span className="w-6 text-center text-base flex-shrink-0">{icon}</span>
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
