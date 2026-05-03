import { motion } from 'framer-motion';

/**
 * Türkiye → Avrupa stilize harita.
 * Anadolu silüeti üzerinde origin → buyer rota çizgisi (animasyonlu draw),
 * şehir noktaları, koordinat label'ları.
 */

interface Props {
  originCity?: string;
  targetCountry: 'TR' | 'DE' | 'NL' | string;
  targetCity?: string;
  totalKm?: number;
  transportMode?: string;
  distanceSource?: string;
  height?: number;
}

// Önemli şehirler için stilize SVG koordinatları (gerçek değil — atlas kompozisyonu)
const POINTS: Record<string, { x: number; y: number; label: string }> = {
  'Nevşehir':   { x: 470, y: 318, label: 'Nevşehir' },
  'İzmir':      { x: 360, y: 320, label: 'İzmir' },
  'İstanbul':   { x: 410, y: 250, label: 'İstanbul' },
  'Hamburg':    { x: 200, y: 130, label: 'Hamburg' },
  'Rotterdam':  { x: 160, y: 160, label: 'Rotterdam' },
  'Berlin':     { x: 240, y: 145, label: 'Berlin' },
  'Amsterdam':  { x: 165, y: 145, label: 'Amsterdam' },
};

const COUNTRY_DEFAULT_CITY: Record<string, string> = {
  DE: 'Hamburg', NL: 'Rotterdam', TR: 'İstanbul',
};

export function RouteMap({ originCity, targetCountry, targetCity, totalKm, transportMode, distanceSource, height = 420 }: Props) {
  const origin = POINTS[originCity || 'Nevşehir'] || POINTS['Nevşehir']!;
  const tCity = targetCity || COUNTRY_DEFAULT_CITY[targetCountry] || 'Hamburg';
  const target = POINTS[tCity] || POINTS['Hamburg']!;

  // Bezier kontrol noktası — yumuşak ark
  const cx = (origin.x + target.x) / 2;
  const cy = Math.min(origin.y, target.y) - 80;

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <svg viewBox="0 0 700 460" style={{ width: '100%', height, display: 'block' }} role="img" aria-label="Rota haritası">
        <defs>
          <pattern id="rmgrid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1B2A3A" strokeWidth="0.3" opacity="0.07" />
          </pattern>
          <radialGradient id="rmGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#C8553D" stopOpacity="0.45" />
            <stop offset="60%" stopColor="#C8553D" stopOpacity="0" />
          </radialGradient>
          <filter id="rmShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="2" />
            <feOffset dy="1" />
            <feComponentTransfer><feFuncA type="linear" slope="0.4" /></feComponentTransfer>
            <feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        {/* Grid */}
        <rect width="700" height="460" fill="url(#rmgrid)" />

        {/* Latitudes */}
        {[100, 180, 260, 340].map(y => (
          <g key={y}>
            <line x1="0" y1={y} x2="700" y2={y} stroke="#1B2A3A" strokeWidth="0.4" strokeDasharray="2 4" opacity="0.18" />
            <text x="6" y={y - 4} fontFamily="JetBrains Mono" fontSize="8" fill="#6B7785" letterSpacing="2">
              {60 - (y / 460) * 30 | 0}° N
            </text>
          </g>
        ))}

        {/* Avrupa karası — stilize multi-curve */}
        <g fill="#E5DFCE" stroke="#1B2A3A" strokeWidth="0.5" opacity="0.55">
          <path d="M 80 60 C 110 50, 150 80, 180 90 C 220 100, 250 120, 280 130 C 270 145, 250 160, 240 175 C 230 195, 245 215, 255 230 C 240 240, 215 240, 200 248 L 195 270 C 180 280, 155 260, 140 240 C 125 220, 100 210, 80 195 L 70 160 C 65 140, 70 110, 80 60 Z" />
        </g>

        {/* Türkiye — stilize */}
        <g fill="#E5DFCE" stroke="#1B2A3A" strokeWidth="0.5" opacity="0.65">
          <path d="M 320 290 C 350 280, 400 285, 450 290 C 500 295, 540 300, 580 310 C 590 320, 580 335, 565 340 C 530 350, 480 355, 440 350 C 400 348, 350 350, 320 345 C 305 335, 300 310, 320 290 Z" />
        </g>

        {/* Akdeniz/Karadeniz hint */}
        <text x="430" y="380" fontFamily="Fraunces" fontStyle="italic" fontSize="11" fill="#6B7785" opacity="0.7" letterSpacing="0.5">
          Akdeniz
        </text>
        <text x="430" y="240" fontFamily="Fraunces" fontStyle="italic" fontSize="11" fill="#6B7785" opacity="0.7" letterSpacing="0.5">
          Karadeniz
        </text>

        {/* Origin glow */}
        <circle cx={origin.x} cy={origin.y} r="40" fill="url(#rmGlow)" />
        <circle cx={target.x} cy={target.y} r="40" fill="url(#rmGlow)" />

        {/* Route arc — animated draw */}
        <motion.path
          d={`M ${origin.x} ${origin.y} Q ${cx} ${cy}, ${target.x} ${target.y}`}
          fill="none"
          stroke="#C8553D"
          strokeWidth="1.6"
          strokeDasharray="6 4"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.6, ease: [0.2, 0.7, 0.3, 1] }}
        />

        {/* Origin point */}
        <motion.g initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }}>
          <circle cx={origin.x} cy={origin.y} r="6" fill="#1B2A3A" />
          <circle cx={origin.x} cy={origin.y} r="11" fill="none" stroke="#1B2A3A" strokeWidth="0.8" />
          <text x={origin.x + 14} y={origin.y - 8} fontFamily="JetBrains Mono" fontSize="9" letterSpacing="1.5" fill="#1B2A3A" style={{ textTransform: "uppercase" }}>ORIGIN</text>
          <text x={origin.x + 14} y={origin.y + 6} fontFamily="Fraunces" fontStyle="italic" fontSize="14" fill="#1B2A3A">{origin.label}</text>
        </motion.g>

        {/* Target point */}
        <motion.g initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 1.3 }}>
          <circle cx={target.x} cy={target.y} r="6" fill="#C8553D" />
          <circle cx={target.x} cy={target.y} r="11" fill="none" stroke="#C8553D" strokeWidth="0.8" />
          <text x={target.x + 14} y={target.y - 8} fontFamily="JetBrains Mono" fontSize="9" letterSpacing="1.5" fill="#C8553D" style={{ textTransform: "uppercase" }}>TARGET · {targetCountry}</text>
          <text x={target.x + 14} y={target.y + 6} fontFamily="Fraunces" fontStyle="italic" fontSize="14" fill="#1B2A3A">{target.label}</text>
        </motion.g>

        {/* Distance badge mid-arc */}
        {totalKm != null && (
          <motion.g
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.7 }}
          >
            <rect x={cx - 50} y={cy - 16} width="100" height="32" fill="#FFFDF7" stroke="#1B2A3A" strokeWidth="0.5" rx="2" filter="url(#rmShadow)" />
            <text x={cx} y={cy - 4} textAnchor="middle" fontFamily="JetBrains Mono" fontSize="8" letterSpacing="2" fill="#6B7785" style={{ textTransform: "uppercase" }}>MESAFE</text>
            <text x={cx} y={cy + 9} textAnchor="middle" fontFamily="Fraunces" fontWeight="500" fontSize="13" fill="#1B2A3A">
              {Math.round(totalKm).toLocaleString('tr-TR')} km
            </text>
          </motion.g>
        )}

        {/* Mode/source bottom-right */}
        <g>
          <text x="690" y="448" textAnchor="end" fontFamily="JetBrains Mono" fontSize="8" letterSpacing="2" fill="#6B7785" style={{ textTransform: "uppercase" }}>
            {transportMode ? `MOD · ${transportMode.toUpperCase()}` : ''}{distanceSource ? `   ·   KAYNAK · ${distanceSource}` : ''}
          </text>
        </g>
      </svg>
    </div>
  );
}
