import { Outlet, Link, useLocation } from 'react-router-dom'
import { clsx } from 'clsx'

export default function PublicShell() {
  const { pathname } = useLocation()
  const isLanding = pathname === '/'

  return (
    <div className="min-h-screen bg-slate-50">
      <header
        className={clsx(
          'fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 md:px-20 h-28 transition-all duration-300',
          isLanding ? 'bg-white/40 backdrop-blur-md border-b border-white/20' : 'bg-white border-b border-slate-200',
        )}
      >
        <Link
          to="/"
          className="font-display font-black text-4xl tracking-tight text-slate-900 drop-shadow-sm"
        >
          Raw2Value
        </Link>
        <nav className="flex items-center gap-12">
          <Link
            to="/evidence"
            className="font-body text-lg font-semibold tracking-wide text-slate-700 hover:text-amber-600 transition-colors duration-150 drop-shadow-sm"
          >
            Model
          </Link>
          <Link
            to="/login"
            className="font-body text-lg font-semibold tracking-wide text-slate-700 hover:text-slate-900 transition-colors duration-150 drop-shadow-sm"
          >
            Giriş
          </Link>
          <Link
            to="/register"
            className="font-body text-lg font-bold px-8 py-3.5 rounded-full bg-slate-900 text-white tracking-wide hover:bg-slate-800 shadow-md hover:-translate-y-0.5 transition-all duration-150"
          >
            Başla
          </Link>
        </nav>
      </header>
      <Outlet />
    </div>
  )
}
