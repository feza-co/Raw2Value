import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface Step {
  num: string;
  title: string;
  desc: string;
  icon?: ReactNode;
}

export function ProcessFlow({ steps }: { steps: Step[] }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: `repeat(${steps.length}, 1fr) ${'auto '.repeat(steps.length - 1)}`.trim(), alignItems: 'center', gap: 0 }}>
      {/* simpler: flex with separators */}
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${steps.length}, 1fr)`, gap: 0, gridColumn: `1 / -1`, position: 'relative' }}>
        {steps.map((s, i) => (
          <motion.div
            key={s.num}
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08, duration: 0.5 }}
            style={{
              padding: '18px 22px',
              borderRight: i < steps.length - 1 ? '1px solid var(--hairline)' : 'none',
              position: 'relative', textAlign: 'center',
            }}
          >
            <div style={{
              width: 36, height: 36, borderRadius: '50%',
              border: '1px solid var(--ink)', background: 'var(--bone)',
              display: 'grid', placeItems: 'center', margin: '0 auto 14px',
              fontFamily: 'var(--display)', fontWeight: 500, fontSize: 14, color: 'var(--ink)',
            }}>{s.num}</div>
            {s.icon && (
              <div style={{ display: 'grid', placeItems: 'center', height: 36, color: 'var(--ink-soft)', marginBottom: 8 }}>
                {s.icon}
              </div>
            )}
            <div style={{ fontFamily: 'var(--display)', fontWeight: 500, fontSize: 14, marginBottom: 4 }}>
              {s.title}
            </div>
            <div style={{ fontSize: 11, color: 'var(--ink-faded)', lineHeight: 1.4 }}>
              {s.desc}
            </div>

            {/* connector arrow */}
            {i < steps.length - 1 && (
              <span style={{
                position: 'absolute', right: -8, top: 36,
                color: 'var(--ink-faded)', fontFamily: 'var(--display)', fontSize: 16,
              }}>›</span>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
