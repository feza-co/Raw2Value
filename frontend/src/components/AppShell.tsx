import { useState, type ReactNode } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../lib/auth';
import { FxStrip } from './FxStrip';

const NAV: { to: string; label: string; icon: ReactNode }[] = [
  { to: '/dashboard',  label: 'Dashboard',            icon: <IconDashboard /> },
  { to: '/analyzer',   label: 'Material Analyzer',    icon: <IconBeaker /> },
  { to: '/cockpit',    label: 'AI Decision Cockpit',  icon: <IconCockpit /> },
  { to: '/geo',        label: 'GeoCarbon Map',        icon: <IconGlobe /> },
  { to: '/whatif',     label: 'What-if Simulator',    icon: <IconSliders /> },
  { to: '/offer',      label: 'Offer Builder',        icon: <IconDoc /> },
  { to: '/passport',   label: 'Raw Material Passport',icon: <IconPassport /> },
  { to: '/evidence',   label: 'AI Evidence',          icon: <IconShield /> },
  { to: '/admin',      label: 'Admin',                icon: <IconGear /> },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const loc = useLocation();
  const ini = user?.email ? user.email[0]!.toUpperCase() : 'r';

  return (
    <div className={`shell-root ${collapsed ? 'is-collapsed' : ''}`}>
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-mark" />
          {!collapsed && <span className="brand-name">raw<em>2</em>value</span>}
        </div>

        <nav className="sidebar-nav">
          {NAV.map(item => (
            <NavLink key={item.to} to={item.to}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
              title={collapsed ? item.label : undefined}
            >
              <span className="sidebar-icon">{item.icon}</span>
              {!collapsed && <span className="sidebar-label">{item.label}</span>}
              {!collapsed && loc.pathname === item.to && (
                <motion.span layoutId="nav-indicator" className="sidebar-indicator" />
              )}
            </NavLink>
          ))}
        </nav>

        <button className="sidebar-collapse" onClick={() => setCollapsed(c => !c)} title={collapsed ? 'Genişlet' : 'Daralt'}>
          {collapsed ? '›' : '‹ Daralt'}
        </button>
      </aside>

      <div className="shell-main">
        <header className="appbar">
          <button className="appbar-burger" onClick={() => setCollapsed(c => !c)} aria-label="Menü">≡</button>

          <div className="appbar-search">
            <span className="appbar-search-icon">⌕</span>
            <input className="appbar-search-input" placeholder="Arama yapın · hammadde · rota · işleyici…" />
            <span className="appbar-search-shortcut numerals">⌘K</span>
          </div>

          <div className="appbar-right">
            <FxStrip compact />
            <button className="appbar-notif" aria-label="Bildirimler">
              <span style={{ fontSize: 16 }}>♪</span>
              <span className="appbar-notif-dot">3</span>
            </button>
            {user && (
              <div className="appbar-user" onClick={logout} title="Çıkış">
                <div className="appbar-user-avatar">{ini}</div>
                <div className="appbar-user-meta">
                  <div className="appbar-user-name">{user.full_name || user.email.split('@')[0]}</div>
                  <div className="appbar-user-role">Rol: {user.role || 'kullanıcı'}</div>
                </div>
                <span className="appbar-user-chevron">▾</span>
              </div>
            )}
          </div>
        </header>

        <main className="shell-canvas">
          {children}
        </main>

        <footer className="shell-foot">
          <span>© 2026 RAW2VALUE AI · v0.1.0</span>
          <span>Gizlilik Politikası · Kullanım Şartları · Destek</span>
        </footer>
      </div>

      <style>{`
        .shell-root {
          display: grid;
          grid-template-columns: 248px 1fr;
          min-height: 100vh;
          transition: grid-template-columns 280ms cubic-bezier(.2,.7,.3,1);
        }
        .shell-root.is-collapsed { grid-template-columns: 72px 1fr; }

        .sidebar {
          background: var(--paper);
          border-right: 1px solid var(--hairline);
          display: flex; flex-direction: column;
          padding: 22px 14px;
          position: sticky; top: 0; height: 100vh;
          z-index: 20;
        }
        .sidebar-brand { display: flex; align-items: baseline; gap: 10px; padding: 4px 10px 26px; border-bottom: 1px solid var(--hairline); margin-bottom: 18px; }
        .sidebar-brand .brand-name { font-family: var(--display); font-size: 20px; font-weight: 500; letter-spacing: -0.02em; color: var(--ink); }
        .sidebar-brand .brand-name em { font-style: italic; color: var(--tuff); font-weight: 300; }

        .sidebar-nav { flex: 1; display: flex; flex-direction: column; gap: 2px; overflow-y: auto; }

        .sidebar-link {
          position: relative;
          display: flex; align-items: center; gap: 12px;
          padding: 11px 14px; border-radius: 6px;
          font-size: 13px; font-weight: 500; color: var(--ink-soft);
          letter-spacing: 0.01em;
          transition: all 200ms ease;
          white-space: nowrap;
        }
        .sidebar-link:hover { background: var(--bone-deep); color: var(--ink); }
        .sidebar-link.active {
          background: var(--ink); color: var(--bone);
          box-shadow: 0 8px 22px -14px rgba(27, 42, 58, 0.6);
        }
        .sidebar-link.active .sidebar-icon { color: var(--tuff); }

        .sidebar-icon { width: 20px; height: 20px; display: grid; place-items: center; flex-shrink: 0; color: currentColor; }
        .sidebar-icon svg { width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.5; }
        .sidebar-label { flex: 1; }

        .sidebar-collapse {
          margin-top: 14px; padding: 10px 14px;
          background: transparent; border: 1px solid var(--hairline);
          border-radius: 6px; cursor: pointer;
          font-family: var(--mono); font-size: 10px; letter-spacing: 0.18em;
          text-transform: uppercase; color: var(--ink-faded);
          transition: all 180ms ease;
        }
        .sidebar-collapse:hover { background: var(--bone-deep); color: var(--ink); }

        .shell-main { display: flex; flex-direction: column; min-width: 0; }

        .appbar {
          position: sticky; top: 0; z-index: 30;
          display: grid; grid-template-columns: auto 1fr auto;
          align-items: center; gap: 18px;
          padding: 14px 32px;
          background: rgba(250, 247, 240, 0.9);
          backdrop-filter: blur(14px) saturate(120%);
          -webkit-backdrop-filter: blur(14px) saturate(120%);
          border-bottom: 1px solid var(--hairline);
        }
        .appbar-burger {
          display: none;
          background: transparent; border: 1px solid var(--hairline);
          border-radius: 4px; padding: 6px 12px; font-size: 18px;
          cursor: pointer; color: var(--ink);
        }

        .appbar-search {
          display: flex; align-items: center; gap: 10px;
          background: var(--bone-deep);
          border: 1px solid var(--hairline);
          border-radius: 8px; padding: 8px 14px;
          max-width: 520px;
          transition: all 200ms ease;
        }
        .appbar-search:focus-within { background: var(--paper); border-color: var(--tuff); }
        .appbar-search-icon { color: var(--ink-faded); font-size: 16px; }
        .appbar-search-input {
          flex: 1; background: transparent; border: none; outline: none;
          font-family: var(--body); font-size: 13px; color: var(--ink);
        }
        .appbar-search-input::placeholder { color: var(--ink-faded); }
        .appbar-search-shortcut {
          font-size: 9px; letter-spacing: 0.16em;
          color: var(--ink-faded); text-transform: uppercase;
          padding: 2px 6px; border: 1px solid var(--hairline-strong); border-radius: 3px;
        }

        .appbar-right { display: flex; align-items: center; gap: 16px; }
        .appbar-notif {
          position: relative; background: transparent; border: 1px solid var(--hairline);
          border-radius: 8px; padding: 8px 12px; cursor: pointer;
        }
        .appbar-notif:hover { background: var(--bone-deep); }
        .appbar-notif-dot {
          position: absolute; top: -6px; right: -6px;
          background: var(--tuff); color: var(--bone);
          font-family: var(--mono); font-size: 9px; font-weight: 600;
          width: 18px; height: 18px; border-radius: 50%;
          display: grid; place-items: center;
          letter-spacing: 0;
        }

        .appbar-user {
          display: flex; align-items: center; gap: 10px;
          padding: 6px 12px 6px 6px; border-radius: 999px;
          cursor: pointer; transition: all 200ms ease;
          border: 1px solid var(--hairline);
        }
        .appbar-user:hover { background: var(--bone-deep); border-color: var(--tuff); }
        .appbar-user-avatar {
          width: 32px; height: 32px; border-radius: 50%;
          background: var(--ink); color: var(--bone);
          display: grid; place-items: center;
          font-family: var(--display); font-size: 13px; font-weight: 500;
        }
        .appbar-user-meta { display: flex; flex-direction: column; line-height: 1.15; }
        .appbar-user-name { font-size: 12px; font-weight: 600; color: var(--ink); }
        .appbar-user-role { font-family: var(--mono); font-size: 9px; letter-spacing: 0.06em; color: var(--ink-faded); text-transform: uppercase; }
        .appbar-user-chevron { color: var(--ink-faded); font-size: 11px; }

        .shell-canvas { flex: 1; padding: 32px 36px 48px; max-width: 1640px; width: 100%; align-self: flex-start; }
        .shell-foot {
          padding: 18px 36px; border-top: 1px solid var(--hairline);
          display: flex; justify-content: space-between; gap: 12px;
          font-family: var(--mono); font-size: 10px; letter-spacing: 0.06em;
          color: var(--ink-faded); text-transform: uppercase;
        }

        @media (max-width: 980px) {
          .shell-root { grid-template-columns: 1fr !important; }
          .sidebar { position: fixed; left: -260px; transition: left 280ms ease; }
          .sidebar.open { left: 0; }
          .appbar-burger { display: block; }
          .appbar-user-meta { display: none; }
          .shell-canvas { padding: 20px; }
        }
      `}</style>
    </div>
  );
}

/* ========== Inline icon set (1.5px stroke, atlas tone) ========== */
function svg(p: string) {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">{<path d={p} />}</svg>;
}
function IconDashboard() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="7" height="9" rx="1" /><rect x="14" y="3" width="7" height="5" rx="1" /><rect x="14" y="12" width="7" height="9" rx="1" /><rect x="3" y="16" width="7" height="5" rx="1" /></svg>;
}
function IconBeaker() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 3h6M10 3v6L5 19a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-10V3" /><path d="M7 14h10" /></svg>;
}
function IconCockpit() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="3" /><path d="M12 3v3M12 18v3M3 12h3M18 12h3" /></svg>;
}
function IconGlobe() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" /></svg>;
}
function IconSliders() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><line x1="4" y1="6" x2="20" y2="6" /><circle cx="9" cy="6" r="2" fill="currentColor" stroke="none" /><line x1="4" y1="12" x2="20" y2="12" /><circle cx="15" cy="12" r="2" fill="currentColor" stroke="none" /><line x1="4" y1="18" x2="20" y2="18" /><circle cx="11" cy="18" r="2" fill="currentColor" stroke="none" /></svg>;
}
function IconDoc() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5M9 13h6M9 17h4" /></svg>;
}
function IconPassport() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="3" width="14" height="18" rx="2" /><circle cx="12" cy="11" r="3" /><path d="M9 17h6" /></svg>;
}
function IconShield() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3l8 4v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7l8-4z" /><path d="m9 12 2 2 4-4" /></svg>;
}
function IconGear() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" /></svg>;
}
