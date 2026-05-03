import type { ReactNode } from 'react';

interface Props {
  title: ReactNode;
  subtitle?: ReactNode;
  breadcrumbs?: { label: string; to?: string }[];
  actions?: ReactNode;
}

export function PageHeader({ title, subtitle, breadcrumbs, actions }: Props) {
  return (
    <header style={{ marginBottom: 28 }}>
      {breadcrumbs && breadcrumbs.length > 0 && (
        <div className="numerals" style={{
          fontSize: 10, letterSpacing: '0.16em', textTransform: 'uppercase',
          color: 'var(--ink-faded)', marginBottom: 10,
        }}>
          {breadcrumbs.map((b, i) => (
            <span key={i}>
              {i > 0 && <span style={{ margin: '0 8px', opacity: 0.5 }}>›</span>}
              {b.to ? <a href={b.to} style={{ color: 'inherit' }}>{b.label}</a> : b.label}
            </span>
          ))}
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', gap: 24, flexWrap: 'wrap' }}>
        <div>
          <h1 style={{
            fontFamily: 'var(--display)', fontSize: 'clamp(36px, 4.5vw, 56px)',
            fontWeight: 500, lineHeight: 0.98, letterSpacing: '-0.025em',
            margin: 0,
          }}>
            {title}
          </h1>
          {subtitle && (
            <p style={{
              marginTop: 8, fontFamily: 'var(--display)', fontStyle: 'italic',
              fontSize: 16, color: 'var(--ink-soft)', fontWeight: 300,
              fontVariationSettings: "'opsz' 36, 'SOFT' 60",
            }}>
              {subtitle}
            </p>
          )}
        </div>
        {actions && <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>{actions}</div>}
      </div>
    </header>
  );
}
