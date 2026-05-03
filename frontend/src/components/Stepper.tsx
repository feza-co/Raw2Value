interface Step { label: string; sub?: string; }

interface Props {
  steps: Step[];
  current: number;       // 1-indexed
  onSelect?: (i: number) => void;
}

export function Stepper({ steps, current, onSelect }: Props) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: `repeat(${steps.length * 2 - 1}, auto)`, alignItems: 'center', gap: 0, justifyContent: 'space-between' }}>
      {steps.map((s, i) => {
        const idx = i + 1;
        const isActive = idx === current;
        const isDone = idx < current;
        return (
          <div key={s.label} style={{ display: 'contents' }}>
            <button
              type="button"
              onClick={() => onSelect && onSelect(idx)}
              disabled={!onSelect || idx > current}
              style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
                background: 'transparent', border: 'none', cursor: onSelect ? 'pointer' : 'default',
                padding: 0,
              }}
            >
              <div style={{
                width: 36, height: 36, borderRadius: '50%',
                display: 'grid', placeItems: 'center',
                background: isActive ? 'var(--ink)' : isDone ? 'var(--tuff)' : 'var(--bone-deep)',
                color: (isActive || isDone) ? 'var(--bone)' : 'var(--ink-faded)',
                fontFamily: 'var(--display)', fontWeight: 500, fontSize: 16,
                border: `1px solid ${isActive ? 'var(--ink)' : isDone ? 'var(--tuff)' : 'var(--hairline-strong)'}`,
                transition: 'all 240ms ease',
              }}>
                {isDone ? '✓' : idx}
              </div>
              <div style={{
                fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.14em',
                textTransform: 'uppercase',
                color: isActive ? 'var(--ink)' : isDone ? 'var(--tuff)' : 'var(--ink-faded)',
                fontWeight: isActive ? 600 : 500,
                whiteSpace: 'nowrap',
              }}>{s.label}</div>
            </button>
            {i < steps.length - 1 && (
              <div style={{
                height: 1, minWidth: 40, flex: 1, marginTop: -28,
                background: idx < current ? 'var(--tuff)' : 'var(--hairline-strong)',
              }} />
            )}
          </div>
        );
      })}
    </div>
  );
}
