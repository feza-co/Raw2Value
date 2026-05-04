import { Link } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import FxTicker from '@/components/domain/FxTicker'

export default function TopBar() {
  const { user, logout } = useAuth()

  const displayName = user?.full_name ?? user?.email ?? 'User'
  const initials = displayName.substring(0, 2).toUpperCase()

  return (
    <header className="fixed top-0 left-16 right-0 z-30 h-20 bg-white/95 backdrop-blur-md border-b border-stone-100 shadow-[0_2px_15px_-3px_rgba(0,0,0,0.03)] flex items-center px-8 gap-6 transition-all duration-300">
      <Link to="/" className="font-display text-ink text-2xl font-semibold tracking-tight mr-auto hover:text-amber transition-colors duration-200">
        Raw2Value AI
      </Link>

      <div className="hidden md:block">
        <FxTicker compact />
      </div>

      <div className="flex items-center gap-5 pl-6 ml-2 border-l border-stone-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-parchment border border-stone-200 flex items-center justify-center text-charcoal font-body font-medium shadow-sm">
            {initials}
          </div>
          <span className="font-body text-sm font-medium text-charcoal hidden sm:block">
            {displayName}
          </span>
        </div>
        <button
          onClick={logout}
          className="font-body text-sm font-medium text-stone-400 hover:text-danger hover:bg-danger/5 px-4 py-2 rounded-lg transition-all duration-200"
        >
          Çıkış
        </button>
      </div>
    </header>
  )
}
