import { Link } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import FxTicker from '@/components/domain/FxTicker'

export default function TopBar() {
  const { user, logout } = useAuth()

  return (
    <header className="fixed top-0 left-16 right-0 z-30 h-14 bg-white border-b border-stone-100 flex items-center px-6 gap-6">
      <Link to="/" className="font-display text-ink text-base tracking-tight mr-auto">
        Raw2Value AI
      </Link>

      <FxTicker compact />

      <div className="flex items-center gap-3">
        <span className="font-body text-sm text-stone-300">
          {user?.full_name ?? user?.email}
        </span>
        <button
          onClick={logout}
          className="font-body text-xs text-stone-300 hover:text-danger transition-colors duration-150"
        >
          Çıkış
        </button>
      </div>
    </header>
  )
}
