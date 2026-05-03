interface Props { value: number }

export default function ConfidenceRing({ value }: Props) {
  const r = 36
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - value)
  const color = value > 0.7 ? '#10B981' : value > 0.4 ? '#F59E0B' : '#EF4444'

  return (
    <svg width="88" height="88" viewBox="0 0 88 88" className="drop-shadow-sm">
      <circle cx="44" cy="44" r={r} fill="none" stroke="#F1F5F9" strokeWidth="6" />
      <circle
        cx="44" cy="44" r={r} fill="none"
        stroke={color} strokeWidth="6"
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 44 44)"
        style={{ transition: 'stroke-dashoffset 1s cubic-bezier(0.16,1,0.3,1)' }}
      />
      <text x="44" y="49" textAnchor="middle" fontSize="16" fontWeight="bold" fontFamily="var(--font-mono)" fill={color}>
        {Math.round(value * 100)}%
      </text>
    </svg>
  )
}
