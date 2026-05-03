import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { FxStrip } from './FxStrip';

export function Topbar() {
  const { user, logout } = useAuth();
  const ini = user?.email ? user.email[0]!.toUpperCase() : 'r';

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <Link to="/dashboard" className="brand">
          <span className="brand-mark" />
          <span className="brand-name">raw<em>2</em>value</span>
        </Link>

        <nav className="nav">
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'active' : ''}>Atölye</NavLink>
          <NavLink to="/whatif"    className={({ isActive }) => isActive ? 'active' : ''}>What-if</NavLink>
          <NavLink to="/evidence"  className={({ isActive }) => isActive ? 'active' : ''}>Kanıt</NavLink>
          <NavLink to="/history"   className={({ isActive }) => isActive ? 'active' : ''}>Tarihçe</NavLink>
        </nav>

        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <FxStrip />
          {user && (
            <button className="user-chip" onClick={logout} aria-label="Çıkış">
              <span className="user-chip-dot">{ini}</span>
              <span style={{ textTransform: 'lowercase' }}>{user.email.split('@')[0]}</span>
              <span style={{ opacity: 0.5 }}>·</span>
              <span>ÇIK</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
