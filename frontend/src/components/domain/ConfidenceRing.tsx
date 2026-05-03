interface Props { value: number }

export default function ConfidenceRing({ value }: Props) {
  const r = 36
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - value)
  const color = value > 0.7 ? '#3D7A4E' : value > 0.4 ? '#B8832A' : '#8B3A3A'

  return (
    <svg width="88" height="88" viewBox="0 0 88 88">
      <circle cx="44" cy="44" r={r} fill="none" stroke="#E8E4DC" strokeWidth="4" />
      <circle
        cx="44" cy="44" r={r} fill="none"
        stroke={color} strokeWidth="4"
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="butt"
        transform="rotate(-90 44 44)"
        style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.16,1,0.3,1)' }}
      />
      <text x="44" y="49" textAnchor="middle" fontSize="14" fontFamily="var(--font-body)" fill={color}>
        {Math.round(value * 100)}%
      </text>
    </svg>
  )
}
