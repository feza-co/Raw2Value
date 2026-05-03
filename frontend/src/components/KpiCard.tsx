import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface Props {
  icon?: ReactNode;
  label: string;
  value: ReactNode;
  delta?: { value: string; up?: boolean };
  foot?: string;
  highlight?: boolean;
  delay?: number;
}

export function KpiCard({ icon, label, value, delta, foot, highlight, delay = 0 }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.2, 0.7, 0.3, 1] }}
      style={{
        background: highlight ? 'var(--ink)' : 'var(--paper)',
        color: highlight ? 'var(--bone)' : 'var(--ink)',
        border: '1px solid var(--hairline)',
        borderRadius: 4,
        padding: '20px 22px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {highlight && (
        <div style={{
          position: 'absolute', top: 0, right: 0, bottom: 0, width: '40%',
          background: 'radial-gradient(circle at 80% 30%, rgba(200,85,61,0.18) 0%, transparent 60%)',
          pointerEvents: 'none',
        }} />
      )}

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="numerals" style={{
            fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase',
            color: highlight ? 'rgba(250,247,240,0.65)' : 'var(--ink-faded)',
          }}>{label}</div>

          <div style={{
            marginTop: 8, fontFamily: 'var(--display)', fontWeight: 500,
            fontSize: 'clamp(28px, 3vw, 40px)', lineHeight: 1.0,
            letterSpacing: '-0.025em',
          }}>
            {value}
          </div>

          {(delta || foot) && (
            <div style={{
              marginTop: 8, display: 'flex', gap: 8, alignItems: 'center',
              fontFamily: 'var(--mono)', fontSize: 10,
              color: highlight ? 'rgba(250,247,240,0.7)' : 'var(--ink-faded)',
              letterSpacing: '0.04em',
            }}>
              {delta && (
                <span style={{ color: delta.up ? 'var(--co2-green)' : 'var(--co2-red)', fontWeight: 600 }}>
                  {delta.up ? '↗' : '↘'} {delta.value}
                </span>
              )}
              {foot && <span>{foot}</span>}
            </div>
          )}
        </div>

        {icon && (
          <div style={{
            width: 44, height: 44, borderRadius: 6,
            background: highlight ? 'rgba(200,85,61,0.18)' : 'var(--bone-deep)',
            color: highlight ? 'var(--tuff)' : 'var(--ink)',
            display: 'grid', placeItems: 'center', flexShrink: 0,
          }}>
            {icon}
          </div>
        )}
      </div>
    </motion.div>
  );
}

export const KpiIcon = {
  Doc: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5" /></svg>,
  Database: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" /></svg>,
  Cloud: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M18 10a5 5 0 0 0-9.6-1.5A4 4 0 0 0 6 16h11a3.5 3.5 0 0 0 1-6.9z" /></svg>,
  Pin: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 21s7-7 7-12a7 7 0 0 0-14 0c0 5 7 12 7 12z" /><circle cx="12" cy="9" r="2.5" /></svg>,
  Truck: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="2" y="7" width="11" height="9" /><path d="M13 10h5l3 3v3h-8z" /><circle cx="6" cy="18" r="2" /><circle cx="17" cy="18" r="2" /></svg>,
  Users: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="9" cy="8" r="3" /><path d="M3 20a6 6 0 0 1 12 0" /><circle cx="17" cy="9" r="2.5" /><path d="M20 19a5 5 0 0 0-3-4.6" /></svg>,
  Bag: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M5 9h14l-1 12H6z" /><path d="M9 9V6a3 3 0 0 1 6 0v3" /></svg>,
  Sparkle: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 3l2 6 6 2-6 2-2 6-2-6-6-2 6-2z" /></svg>,
  Trophy: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M8 21h8M10 17v4M14 17v4M6 4h12v3a6 6 0 0 1-12 0z" /><path d="M6 4H4v3a3 3 0 0 0 2 3M18 4h2v3a3 3 0 0 1-2 3" /></svg>,
  Clock: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></svg>,
  Factory: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M3 21V11l5 3V11l5 3V8l8 5v8z" /><path d="M7 17h2M11 17h2M15 17h2" /></svg>,
};
