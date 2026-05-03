interface Props {
  fromColor?: string
  toColor?: string
  flip?: boolean
}

export default function DiagonalDivider({
  fromColor = '#F8F7F5',
  toColor = '#FFFFFF',
  flip = false,
}: Props) {
  const points = flip
    ? '0,0 100,4 100,0'
    : '0,4 100,0 100,4'

  return (
    <div style={{ background: fromColor, lineHeight: 0 }}>
      <svg
        viewBox="0 0 100 4"
        preserveAspectRatio="none"
        style={{ display: 'block', width: '100%', height: '4vw' }}
      >
        <polygon points={points} fill={toColor} />
      </svg>
    </div>
  )
}
