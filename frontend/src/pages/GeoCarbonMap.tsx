import { useState, useEffect } from 'react';
import { Truck, Ship, Train, Plane, Leaf, AlertTriangle, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAnalysis } from '../contexts/AnalysisContext';

// ── SVG Map constants ─────────────────────────────────────────────────────────
// Equirectangular projection: x = (lon + 8) * 15.2, y = (56 - lat) * 19.5
// ViewBox: "0 0 870 460"

const lon = (v: number) => (v + 8) * 15.2;
const lat = (v: number) => (56 - v) * 19.5;

// Simplified land mass polygons (rough but geographically recognizable)
const EUROPE = [
  [0, 0], [400, 0], [520, 55], [515, 135], [460, 185],
  [530, 290], [530, 395], [480, 415], [436, 385], [395, 315],
  [360, 260], [275, 260], [215, 285], [170, 285],
  [108, 395], [42, 415], [0, 375],
].map(([x, y]) => `${x},${y}`).join(' ');

const ITALY = [
  [275, 260], [380, 260], [408, 335], [388, 395],
  [365, 375], [265, 325],
].map(([x, y]) => `${x},${y}`).join(' ');

const TURKEY = [
  [lon(26), lat(42)], [lon(30), lat(42)], [lon(36), lat(42)],
  [lon(40), lat(41)], [lon(44), lat(39)], [lon(44), lat(37)],
  [lon(36), lat(37)], [lon(30), lat(36)], [lon(26), lat(37)],
  [lon(25), lat(39)], [lon(26), lat(41)],
].map(([x, y]) => `${Math.round(x)},${Math.round(y)}`).join(' ');

// Key city screen positions
const C = {
  nevsehir:     { x: Math.round(lon(34.7)),  y: Math.round(lat(38.6)), label: 'Nevşehir',    sub: 'Kapadokya Menşei' },
  istanbul:     { x: Math.round(lon(29.0)),  y: Math.round(lat(41.0)), label: 'İstanbul',    sub: 'Boğaz Geçişi' },
  mersin:       { x: Math.round(lon(34.6)),  y: Math.round(lat(36.8)), label: 'Mersin',      sub: 'Liman Yükleme' },
  belgrade:     { x: Math.round(lon(20.5)),  y: Math.round(lat(44.8)), label: 'Belgrad',     sub: 'Transit' },
  vienna:       { x: Math.round(lon(16.4)),  y: Math.round(lat(48.2)), label: 'Viyana',      sub: 'Transit' },
  hamburg:      { x: Math.round(lon(10.0)),  y: Math.round(lat(53.6)), label: 'Hamburg',     sub: 'Hedef Liman' },
  rotterdam:    { x: Math.round(lon(4.5)),   y: Math.round(lat(51.9)), label: 'Rotterdam',   sub: 'Hedef Liman' },
  istanbul_port:{ x: Math.round(lon(28.5)),  y: Math.round(lat(40.8)), label: 'İstanbul',    sub: 'Deniz Çıkışı' },
  aegean:       { x: Math.round(lon(24)),    y: Math.round(lat(37.5)), label: 'Ege',         sub: 'Deniz Yolu' },
  med_mid:      { x: Math.round(lon(10)),    y: Math.round(lat(36)),   label: 'Akdeniz',     sub: 'Deniz Yolu' },
  gibraltar:    { x: Math.round(lon(-4.5)),  y: Math.round(lat(36.2)), label: 'Cebelitarık', sub: 'Boğaz' },
  biscay:       { x: Math.round(lon(-1)),    y: Math.round(lat(46)),   label: 'Biscay',      sub: 'Atlantik' },
};

type Waypoint = { x: number; y: number; label: string; sub: string };

interface RouteConfig {
  mainPath: string;
  prePath?: string;  // dotted pre-segment (truck to port)
  color: string;
  waypoints: Waypoint[];
}

function buildRoutes(dest: 'DE' | 'NL' | 'TR'): Record<string, RouteConfig> {
  const d = dest === 'NL' ? C.rotterdam : C.hamburg;

  const seaPath = dest === 'NL'
    ? `M${C.mersin.x},${C.mersin.y} C${lon(22)},${lat(35)+20} ${lon(5)},${lat(36)} ${lon(-4)},${lat(37)} C${lon(-6)},${lat(43)} ${lon(-4)},${lat(48)} ${lon(1)},${lat(51)} Q${lon(3)},${lat(52)} ${d.x},${d.y}`
    : `M${C.mersin.x},${C.mersin.y} C${lon(22)},${lat(35)+20} ${lon(8)},${lat(36)} ${lon(-4)},${lat(37)} C${lon(-5)},${lat(43)} ${lon(-2)},${lat(50)} ${lon(4)},${lat(52)} Q${lon(7)},${lat(53)} ${d.x},${d.y}`;

  const roadPath = dest === 'NL'
    ? `M${C.nevsehir.x},${C.nevsehir.y} L${C.istanbul.x},${C.istanbul.y} L${C.belgrade.x},${C.belgrade.y} L${C.vienna.x},${C.vienna.y} L${d.x},${d.y}`
    : `M${C.nevsehir.x},${C.nevsehir.y} L${C.istanbul.x},${C.istanbul.y} L${C.belgrade.x},${C.belgrade.y} L${C.vienna.x},${C.vienna.y} L${d.x},${d.y}`;

  const railPath = dest === 'NL'
    ? `M${C.nevsehir.x},${C.nevsehir.y} L${C.istanbul.x},${C.istanbul.y} L${Math.round(lon(18))},${Math.round(lat(46))} L${d.x},${d.y}`
    : `M${C.nevsehir.x},${C.nevsehir.y} L${C.istanbul.x},${C.istanbul.y} L${Math.round(lon(18))},${Math.round(lat(46))} L${d.x},${d.y}`;

  const airCtrlX = Math.round((C.nevsehir.x + d.x) / 2);
  const airCtrlY = Math.round(Math.min(C.nevsehir.y, d.y) - 80);
  const airPath = `M${C.nevsehir.x},${C.nevsehir.y} Q${airCtrlX},${airCtrlY} ${d.x},${d.y}`;

  return {
    deniz: {
      mainPath: seaPath,
      prePath: `M${C.nevsehir.x},${C.nevsehir.y} L${C.mersin.x},${C.mersin.y}`,
      color: '#3B82F6',
      waypoints: [C.nevsehir, C.mersin, C.aegean, C.gibraltar, d],
    },
    kara: {
      mainPath: roadPath,
      color: '#B85C38',
      waypoints: [C.nevsehir, C.istanbul, C.belgrade, C.vienna, d],
    },
    demiryolu: {
      mainPath: railPath,
      color: '#6B8E78',
      waypoints: [C.nevsehir, C.istanbul, { x: Math.round(lon(18)), y: Math.round(lat(46)), label: 'Merkez Avrupa', sub: 'Demir Ağı' }, d],
    },
    hava: {
      mainPath: airPath,
      color: '#7A6652',
      waypoints: [C.nevsehir, d],
    },
  };
}

const MODE_LABEL: Record<string, string> = {
  deniz: 'Denizyolu', kara: 'Karayolu', demiryolu: 'Demiryolu', hava: 'Havayolu',
};
const MODE_ICON: Record<string, React.ReactNode> = {
  deniz: <Ship className="w-3.5 h-3.5" />,
  kara: <Truck className="w-3.5 h-3.5" />,
  demiryolu: <Train className="w-3.5 h-3.5" />,
  hava: <Plane className="w-3.5 h-3.5" />,
};

export default function GeoCarbonMap() {
  const { request, result } = useAnalysis();
  const [activeWp, setActiveWp] = useState(0);
  const [drawn, setDrawn] = useState(false);

  const transportMode = request?.transport_mode ?? 'deniz';
  const targetCountry = (request?.target_country ?? 'DE') as 'DE' | 'NL' | 'TR';

  const routes = buildRoutes(targetCountry);
  const route = routes[transportMode] ?? routes.deniz;

  useEffect(() => {
    setDrawn(false);
    setActiveWp(0);
    const t = setTimeout(() => setDrawn(true), 80);
    return () => clearTimeout(t);
  }, [transportMode, targetCountry]);

  if (!request || !result) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-56px)] gap-6">
        <p className="text-r2v-charcoal/60">Henüz analiz yapılmadı.</p>
        <Link to="/dashboard" className="flex items-center gap-2 px-6 py-3 bg-r2v-charcoal text-white text-xs font-bold uppercase tracking-widest hover:bg-r2v-charcoal/90 transition-colors">
          Analize Dön <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  const totalCO2 = result.co2_kg;
  const mineCO2   = Math.round(totalCO2 * 0.036);
  const procCO2   = Math.round(totalCO2 * 0.084);
  const transitCO2 = Math.round(totalCO2 * 0.862);
  const lastMileCO2 = Math.round(totalCO2 * 0.018);

  const segments = [
    { label: 'Çıkarım',    kg: mineCO2,    pct: 3.6,  alert: false },
    { label: 'İşleme',     kg: procCO2,    pct: 8.4,  alert: false },
    { label: 'Lojistik',   kg: transitCO2, pct: 86.2, alert: transportMode === 'hava' || transportMode === 'kara' },
    { label: 'Son Mil',    kg: lastMileCO2,pct: 1.8,  alert: false },
  ];

  const activeCity = route.waypoints[activeWp];

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col overflow-hidden bg-r2v-base">

      {/* Header strip */}
      <div className="shrink-0 flex items-center justify-between px-6 py-3 border-b border-r2v-charcoal/10 bg-white">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-bold uppercase tracking-widest text-r2v-charcoal">GeoCarbon Map</h1>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-r2v-charcoal/15 text-[10px] font-bold uppercase tracking-widest text-r2v-charcoal/60">
            {MODE_ICON[transportMode]}
            {MODE_LABEL[transportMode]}
          </div>
          <span className="text-[10px] text-r2v-charcoal/40 font-medium">
            {request.origin_city} → {route.waypoints.at(-1)?.label}
          </span>
        </div>
        <div className="text-right">
          <div className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40">Toplam Scope 3</div>
          <div className="text-lg font-mono font-light text-r2v-charcoal">
            {totalCO2.toLocaleString('tr-TR')} <span className="text-xs font-bold text-r2v-charcoal/50">kg CO₂</span>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden min-h-0">

        {/* SVG Map */}
        <div className="flex-1 relative overflow-hidden bg-[#C4D9EB]">
          <svg
            viewBox="0 0 870 460"
            className="w-full h-full"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <linearGradient id="seaGrad" x1="0%" y1="100%" x2="0%" y2="0%">
                <stop offset="0%" stopColor="#B8D4E8" />
                <stop offset="100%" stopColor="#C8E0F0" />
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
              <marker id="arr" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto">
                <circle cx="3.5" cy="3.5" r="2" fill={route.color} />
              </marker>
            </defs>

            {/* Sea background */}
            <rect width="870" height="460" fill="url(#seaGrad)" />

            {/* Subtle grid */}
            {[100,200,300,400,500,600,700,800].map(gx => (
              <line key={`gx${gx}`} x1={gx} y1="0" x2={gx} y2="460" stroke="rgba(0,0,0,0.04)" strokeWidth="1" />
            ))}
            {[100,200,300,400].map(gy => (
              <line key={`gy${gy}`} x1="0" y1={gy} x2="870" y2={gy} stroke="rgba(0,0,0,0.04)" strokeWidth="1" />
            ))}

            {/* Land masses */}
            <polygon points={EUROPE}   fill="#E5DECE" stroke="#D4CBBA" strokeWidth="1.2" />
            <polygon points={ITALY}    fill="#DEDAD0" stroke="#D4CBBA" strokeWidth="1" />
            <polygon points={TURKEY}   fill="#E0D8C6" stroke="#D4CBBA" strokeWidth="1.2" />

            {/* Sea labels */}
            <text x="155" y="375" fontSize="9" fill="#5A8FA8" opacity="0.8" fontStyle="italic">Akdeniz</text>
            <text x="500" y="448" fontSize="9" fill="#5A8FA8" opacity="0.7" fontStyle="italic">Ege Denizi</text>
            <text x="630" y="220" fontSize="9" fill="#5A8FA8" opacity="0.7" fontStyle="italic">Karadeniz</text>
            <text x="35" y="60"  fontSize="9" fill="#5A8FA8" opacity="0.7" fontStyle="italic">Kuzey Denizi</text>

            {/* Kapadokya region label */}
            <text x={C.nevsehir.x - 30} y={C.nevsehir.y + 25} fontSize="8" fill="#7A6652" opacity="0.8" fontStyle="italic">
              Kapadokya
            </text>

            {/* Pre-path (truck to port, dotted) */}
            {route.prePath && (
              <path
                d={route.prePath}
                fill="none"
                stroke={route.color}
                strokeWidth="2"
                strokeDasharray="5 4"
                opacity="0.65"
              />
            )}

            {/* Route glow */}
            <path
              d={route.mainPath}
              fill="none"
              stroke={route.color}
              strokeWidth="9"
              opacity="0.12"
              strokeLinecap="round"
            />

            {/* Animated route line */}
            <path
              d={route.mainPath}
              fill="none"
              stroke={route.color}
              strokeWidth={transportMode === 'demiryolu' ? 2.5 : 2.5}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={transportMode === 'demiryolu' ? '10 5' : transportMode === 'hava' ? '8 6' : 'none'}
              style={{
                strokeDashoffset: drawn ? 0 : 3000,
                transition: drawn ? 'stroke-dashoffset 2.4s ease-out' : 'none',
              }}
            />
            {/* Solid overlay for non-dashed modes */}
            {transportMode !== 'demiryolu' && transportMode !== 'hava' && (
              <path
                d={route.mainPath}
                fill="none"
                stroke={route.color}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{
                  strokeDasharray: 3000,
                  strokeDashoffset: drawn ? 0 : 3000,
                  transition: drawn ? 'stroke-dashoffset 2.4s ease-out' : 'none',
                }}
              />
            )}

            {/* Waypoints */}
            {route.waypoints.map((wp, i) => {
              const isOrigin = i === 0;
              const isDest   = i === route.waypoints.length - 1;
              const isActive = activeWp === i;
              const isMinor  = !isOrigin && !isDest;
              const r = isActive ? 9 : isOrigin || isDest ? 7 : 4;
              const labelY = wp.y - r - 6;

              return (
                <g key={i} onClick={() => setActiveWp(i)} className="cursor-pointer" style={{ transition: 'opacity 0.2s' }}>
                  {/* Pulse ring */}
                  {(isOrigin || isDest) && (
                    <circle cx={wp.x} cy={wp.y} r={r + 6} fill="none" stroke={route.color} strokeWidth="1.2" opacity={isActive ? 0.5 : 0.25} />
                  )}
                  {/* Dot */}
                  <circle
                    cx={wp.x} cy={wp.y} r={r}
                    fill={isOrigin ? '#2C2C2A' : isDest ? route.color : isActive ? route.color : 'white'}
                    stroke={route.color}
                    strokeWidth={isMinor ? 1.5 : 2.5}
                    style={{ transition: 'r 0.2s, fill 0.2s' }}
                  />
                  {/* Label - only for origin, destination and active */}
                  {(isOrigin || isDest || isActive) && (
                    <>
                      <text x={wp.x} y={labelY} textAnchor="middle" fontSize="8.5" fontWeight="700" fill="#2C2C2A" fontFamily="system-ui, sans-serif">
                        {wp.label.toUpperCase()}
                      </text>
                      <text x={wp.x} y={labelY + 9} textAnchor="middle" fontSize="7" fill="#6B6B5A" fontFamily="system-ui, sans-serif">
                        {wp.sub}
                      </text>
                    </>
                  )}
                </g>
              );
            })}

            {/* CO2 annotation on route midpoint */}
            <text
              x={Math.round((C.nevsehir.x + route.waypoints.at(-1)!.x) / 2)}
              y={transportMode === 'hava' ? 110 : 395}
              textAnchor="middle"
              fontSize="9.5"
              fontWeight="700"
              fill={route.color}
              opacity="0.85"
              fontFamily="monospace"
            >
              {transitCO2.toLocaleString('tr-TR')} kg CO₂
            </text>

            {/* Transport badge */}
            <rect x="8" y="8" rx="4" ry="4" width="130" height="20" fill="white" opacity="0.9" />
            <text x="64" y="21" textAnchor="middle" fontSize="8.5" fontWeight="700" fill="#2C2C2A" fontFamily="system-ui, sans-serif">
              {MODE_LABEL[transportMode].toUpperCase()} ROTASI
            </text>
          </svg>

          {/* Floating active-waypoint tooltip */}
          {activeCity && (
            <div className="absolute bottom-4 left-4 bg-white/95 border border-r2v-charcoal/10 rounded-lg px-4 py-2.5 shadow-md max-w-[180px]">
              <div className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 mb-0.5">Seçili Nokta</div>
              <div className="text-sm font-bold text-r2v-charcoal">{activeCity.label}</div>
              <div className="text-[10px] text-r2v-charcoal/50">{activeCity.sub}</div>
            </div>
          )}
        </div>

        {/* Right panel — CO2 breakdown + tips */}
        <div className="w-72 xl:w-80 shrink-0 border-l border-r2v-charcoal/10 overflow-y-auto bg-white flex flex-col">

          {/* CO2 Breakdown */}
          <div className="p-5 border-b border-r2v-charcoal/10">
            <h2 className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 mb-4">Emisyon Dağılımı</h2>
            <div className="space-y-4">
              {segments.map(({ label, kg, pct, alert }) => (
                <div key={label}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs font-medium text-r2v-charcoal flex items-center gap-1.5">
                      {alert && <AlertTriangle className="w-3 h-3 text-r2v-terracotta" />}
                      {label}
                    </span>
                    <span className="font-mono text-xs text-r2v-charcoal font-bold">{kg.toLocaleString('tr-TR')} kg</span>
                  </div>
                  <div className="h-1.5 bg-r2v-charcoal/8 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${alert ? 'bg-r2v-terracotta' : 'bg-r2v-green/70'}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <div className="text-[9px] text-r2v-charcoal/40 mt-0.5">%{pct.toFixed(1)} toplam</div>
                </div>
              ))}
            </div>
          </div>

          {/* Mode comparison */}
          <div className="p-5 border-b border-r2v-charcoal/10">
            <h2 className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 mb-3">Mod Karşılaştırması</h2>
            {[
              { mode: 'deniz',      factor: 0.015, label: 'Deniz',  icon: Ship },
              { mode: 'demiryolu', factor: 0.030, label: 'Demir',  icon: Train },
              { mode: 'kara',      factor: 0.100, label: 'Kara',   icon: Truck },
              { mode: 'hava',      factor: 0.500, label: 'Hava',   icon: Plane },
            ].map(({ mode, factor, label, icon: Icon }) => {
              const isCurrent = mode === transportMode;
              const barW = (factor / 0.5) * 100;
              return (
                <div key={mode} className={`flex items-center gap-2 py-1.5 ${isCurrent ? 'opacity-100' : 'opacity-50'}`}>
                  <Icon className="w-3 h-3 text-r2v-charcoal/60 shrink-0" />
                  <span className="text-[10px] font-bold w-10 text-r2v-charcoal">{label}</span>
                  <div className="flex-1 h-1.5 bg-r2v-charcoal/8 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${isCurrent ? 'bg-r2v-terracotta' : 'bg-r2v-charcoal/30'}`}
                      style={{ width: `${barW}%` }}
                    />
                  </div>
                  <span className="font-mono text-[9px] text-r2v-charcoal/60 w-16 text-right">{factor} kg/t·km</span>
                </div>
              );
            })}
          </div>

          {/* Waypoint list */}
          <div className="p-5 border-b border-r2v-charcoal/10">
            <h2 className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 mb-3">Rota Noktaları</h2>
            <div className="space-y-0">
              {route.waypoints.map((wp, i) => (
                <button
                  key={i}
                  onClick={() => setActiveWp(i)}
                  className={`w-full flex items-center gap-3 py-2 px-2 -mx-2 rounded transition-colors text-left ${activeWp === i ? 'bg-r2v-charcoal/5' : 'hover:bg-r2v-charcoal/3'}`}
                >
                  <div className={`w-5 h-5 rounded-full shrink-0 border-2 flex items-center justify-center ${
                    i === 0 ? 'bg-r2v-charcoal border-r2v-charcoal' :
                    i === route.waypoints.length - 1 ? 'border-current' : 'bg-white border-r2v-charcoal/30'
                  }`} style={{ borderColor: i > 0 && i < route.waypoints.length - 1 ? undefined : route.color }}>
                    <span className="text-[8px] font-mono font-bold text-white">{i === 0 ? '●' : ''}</span>
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-bold text-r2v-charcoal truncate">{wp.label}</div>
                    <div className="text-[9px] text-r2v-charcoal/40">{wp.sub}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Optimization tips */}
          <div className="p-5 flex-1">
            <h2 className="text-[9px] font-bold uppercase tracking-widest text-r2v-charcoal/40 mb-3">Optimizasyon</h2>
            <div className="space-y-4">
              <div className="flex gap-3">
                <Leaf className="w-3.5 h-3.5 text-r2v-green shrink-0 mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-r2v-charcoal">Denizyolu Seç</div>
                  <p className="text-[10px] text-r2v-charcoal/55 mt-0.5">Karayoluna göre %85 daha az CO₂. CBAM maliyetini minimize eder.</p>
                </div>
              </div>
              <div className="flex gap-3">
                <Leaf className="w-3.5 h-3.5 text-r2v-green shrink-0 mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-r2v-charcoal">Toplu Sevkiyat</div>
                  <p className="text-[10px] text-r2v-charcoal/55 mt-0.5">Tonaj artışı lojistik karbonu ton başına orantısız düşürür.</p>
                </div>
              </div>
              {(transportMode === 'hava' || transportMode === 'kara') && (
                <div className="bg-r2v-terracotta/5 border border-r2v-terracotta/20 rounded p-3 flex gap-2">
                  <AlertTriangle className="w-3.5 h-3.5 text-r2v-terracotta shrink-0 mt-0.5" />
                  <div>
                    <div className="text-[10px] font-bold text-r2v-terracotta">Yüksek Emisyon Modu</div>
                    <p className="text-[10px] text-r2v-charcoal/60 mt-0.5">What-if simülatöründe alternatif modları deneyin.</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
