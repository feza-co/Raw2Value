import { Outlet, Link, useLocation } from 'react-router-dom'
import { clsx } from 'clsx'

export default function PublicShell() {
  const { pathname } = useLocation()
  const isLanding = pathname === '/'

  return (
    <div className="min-h-screen bg-parchment">
      <header
        className={clsx(
          'fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 md:px-16 h-16',
          isLanding ? 'bg-transparent' : 'bg-parchment border-b border-stone-100',
        )}
      >
        <Link
          to="/"
          className="font-display text-xl tracking-tight"
          style={{ color: isLanding ? '#F8F7F5' : '#0D0D0D' }}
        >
          Raw2Value
        </Link>
        <nav className="flex items-center gap-8">
          <Link
            to="/evidence"
            className="font-body text-sm tracking-wide hover:text-amber transition-colors duration-150"
            style={{ color: isLanding ? '#C4BDB0' : '#1A1A1A' }}
          >
            Model
          </Link>
          <Link
            to="/login"
            className="font-body text-sm tracking-wide"
            style={{ color: isLanding ? '#C4BDB0' : '#1A1A1A' }}
          >
            Giriş
          </Link>
          <Link
            to="/register"
            className="font-body text-sm px-4 py-2 bg-amber text-white tracking-wide hover:bg-amber-dark transition-colors duration-150"
          >
            Başla
          </Link>
        </nav>
      </header>
      <Outlet />
    </div>
  )
}
