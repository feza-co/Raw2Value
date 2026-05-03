interface Props {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  marks?: number[];
  suffix?: string;
  hint?: string;
}

/** Atlas slider — kalın hairline track + tuff thumb + tick marks */
export function Slider({ label, value, onChange, min, max, step = 1, unit, marks, suffix, hint }: Props) {
  const pct = ((value - min) / (max - min)) * 100;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10 }}>
        <span className="numerals" style={{ fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'var(--ink-faded)', fontWeight: 500 }}>
          {label}{unit && ` (${unit})`}
        </span>
        <span className="numerals" style={{
          fontFamily: 'var(--mono)', fontWeight: 600, fontSize: 13, color: 'var(--ink)',
          padding: '3px 9px', background: 'var(--bone-deep)', borderRadius: 3,
          border: '1px solid var(--hairline)',
        }}>
          {new Intl.NumberFormat('tr-TR').format(value)}{suffix || ''}
        </span>
      </div>

      <div style={{ position: 'relative', padding: '12px 0' }}>
        {/* Track */}
        <div style={{
          position: 'absolute', left: 0, right: 0, top: '50%', height: 2,
          background: 'var(--hairline-strong)', transform: 'translateY(-50%)',
        }} />
        {/* Filled */}
        <div style={{
          position: 'absolute', left: 0, top: '50%', height: 2, width: `${pct}%`,
          background: 'var(--tuff)', transform: 'translateY(-50%)',
          transition: 'width 180ms ease',
        }} />
        {/* Marks */}
        {marks && marks.map(m => {
          const p = ((m - min) / (max - min)) * 100;
          return <div key={m} style={{
            position: 'absolute', left: `${p}%`, top: '50%',
            width: 1, height: 6, background: 'var(--ink-faded)',
            transform: 'translate(-50%, -50%)',
          }} />;
        })}
        {/* Thumb */}
        <div style={{
          position: 'absolute', left: `${pct}%`, top: '50%',
          width: 16, height: 16, borderRadius: '50%',
          background: 'var(--ink)', border: '2px solid var(--bone)',
          boxShadow: '0 2px 8px -2px rgba(27,42,58,0.4)',
          transform: 'translate(-50%, -50%)',
          pointerEvents: 'none',
          transition: 'left 180ms ease',
        }} />
        <input
          type="range" min={min} max={max} step={step} value={value}
          onChange={e => onChange(Number(e.target.value))}
          style={{
            position: 'relative', zIndex: 2, opacity: 0, cursor: 'pointer',
            width: '100%', height: 24, margin: 0,
          }}
        />
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4, fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-faded)', letterSpacing: '0.06em' }}>
        <span>{new Intl.NumberFormat('tr-TR').format(min)}</span>
        {hint && <span style={{ fontStyle: 'italic', fontFamily: 'var(--display)', color: 'var(--ink-soft)' }}>{hint}</span>}
        <span>{new Intl.NumberFormat('tr-TR').format(max)}</span>
      </div>
    </div>
  );
}
