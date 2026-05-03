import { motion } from 'framer-motion';
import { fmt } from '../lib/format';

/** Confidence — radial gauge (atlas pusula) */
export function ConfidenceGauge({ value, label = 'Güven', size = 200 }: { value: number; label?: string; size?: number }) {
  const r = (size - 20) / 2;
  const c = 2 * Math.PI * r;
  const v = Math.max(0, Math.min(100, value));
  const dash = (v / 100) * c;

  // Confidence renk
  const color = v >= 80 ? '#6B8E5A' : v >= 60 ? '#C68442' : '#A8392E';

  return (
    <div style={{ position: 'relative', width: size, height: size, margin: '0 auto' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#1B2A3A" strokeWidth="0.5" opacity="0.18" strokeDasharray="2 4" />
        <circle cx={size / 2} cy={size / 2} r={r - 8} fill="none" stroke="#E5DFCE" strokeWidth="6" />
        <motion.circle
          cx={size / 2} cy={size / 2} r={r - 8}
          fill="none" stroke={color} strokeWidth="6" strokeLinecap="butt"
          strokeDasharray={`${dash} ${c}`}
          initial={{ strokeDasharray: `0 ${c}` }}
          animate={{ strokeDasharray: `${dash} ${c}` }}
          transition={{ duration: 1.4, ease: [0.2, 0.7, 0.3, 1] }}
        />
        {/* tick marks */}
        {Array.from({ length: 12 }).map((_, i) => {
          const a = (i / 12) * 2 * Math.PI;
          const x1 = size / 2 + (r - 2) * Math.cos(a);
          const y1 = size / 2 + (r - 2) * Math.sin(a);
          const x2 = size / 2 + r * Math.cos(a);
          const y2 = size / 2 + r * Math.sin(a);
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#1B2A3A" strokeWidth="0.5" opacity="0.4" />;
        })}
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', textAlign: 'center' }}>
        <div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.18em', color: 'var(--ink-faded)', textTransform: 'uppercase' }}>{label}</div>
          <div style={{ fontFamily: 'var(--display)', fontSize: 48, fontWeight: 500, lineHeight: 1, letterSpacing: '-0.02em', color }}>
            {fmt.num(v, 0)}<span style={{ fontSize: 18, fontStyle: 'italic', fontWeight: 300, opacity: 0.6, marginLeft: 2 }}>/100</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/** CO₂ — horizontal volcanic plume gauge (saçma kutu yerine) */
export function CO2Strip({ co2Kg, tonnage }: { co2Kg: number; tonnage: number }) {
  const co2PerTon = tonnage > 0 ? co2Kg / tonnage : 0;

  // Benchmark: 50 kg/ton düşük, 200 kg/ton yüksek
  const tracks = [
    { label: 'Düşük', max: 50, color: '#6B8E5A' },
    { label: 'Orta',  max: 120, color: '#C68442' },
    { label: 'Yüksek', max: 300, color: '#A8392E' },
  ];
  const total = 300;
  const pct = Math.min(100, (co2PerTon / total) * 100);
  const tier = co2PerTon < 50 ? 'low' : co2PerTon < 120 ? 'mid' : 'high';
  const tierColor = tier === 'low' ? '#6B8E5A' : tier === 'mid' ? '#C68442' : '#A8392E';

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10 }}>
        <span className="eyebrow">CO₂ · ton başına</span>
        <span className="numerals" style={{ fontSize: 12, color: 'var(--ink-faded)' }}>{fmt.num(co2Kg, 0)} kg toplam</span>
      </div>

      <div style={{ position: 'relative', height: 12, background: 'var(--bone-deep)', borderRadius: 0, border: '1px solid var(--hairline-strong)' }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1.2, ease: [0.2, 0.7, 0.3, 1], delay: 0.2 }}
          style={{ height: '100%', background: tierColor, position: 'relative' }}
        />
        {/* Threshold ticks */}
        {tracks.map(t => (
          <div key={t.label} style={{
            position: 'absolute', top: -4, bottom: -4,
            left: `${(t.max / total) * 100}%`,
            width: 1, background: 'var(--ink)', opacity: 0.4,
          }} />
        ))}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6, fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.1em', color: 'var(--ink-faded)' }}>
        <span>0</span>
        <span>50</span>
        <span>120</span>
        <span>300+ kg/t</span>
      </div>

      <div style={{ marginTop: 14, display: 'flex', alignItems: 'baseline', gap: 12 }}>
        <span className="numerals" style={{ fontFamily: 'var(--display)', fontSize: 38, fontWeight: 500, color: tierColor, letterSpacing: '-0.02em', lineHeight: 1 }}>
          {fmt.num(co2PerTon, 1)}
        </span>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-faded)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>kg CO₂ / ton</span>
      </div>
    </div>
  );
}

/** Sparkline — match score progression */
export function Sparkline({ values, color = '#1B2A3A', height = 36, width = 120 }: { values: number[]; color?: string; height?: number; width?: number }) {
  if (!values.length) return null;
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const span = max - min || 1;
  const pts = values.map((v, i) => {
    const x = (i / Math.max(values.length - 1, 1)) * width;
    const y = height - ((v - min) / span) * height;
    return `${x},${y}`;
  }).join(' ');
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ display: 'block' }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.4" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}
