import { useEffect, useRef } from 'react';
import L from 'leaflet';

// Fix Leaflet default marker icon path broken by bundlers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// City coordinates
const COORDS: Record<string, [number, number]> = {
  // Turkey origins
  nevşehir:  [38.62, 34.72],
  acıgöl:    [38.55, 34.50],
  ankara:    [39.93, 32.86],
  istanbul:  [41.01, 28.97],
  izmir:     [38.42, 27.14],
  mersin:    [36.80, 34.63],
  konya:     [37.87, 32.49],
  kayseri:   [38.73, 35.49],
  // Destinations
  hamburg:   [53.55, 9.99],
  rotterdam: [51.90, 4.47],
  istanbul_port: [41.00, 29.00],
  amsterdam: [52.37, 4.90],
  berlin:    [52.52, 13.40],
};

function resolveCoord(city: string): [number, number] {
  const key = city.toLowerCase().replace(/[^a-zğüşıöç]/g, '');
  for (const [k, v] of Object.entries(COORDS)) {
    if (k.replace(/[^a-zğüşıöç]/g, '') === key) return v;
  }
  // Fallback: Nevşehir
  return [38.62, 34.72];
}

function makeIcon(color: string, size = 12) {
  return L.divIcon({
    html: `<div style="
      width:${size}px; height:${size}px;
      background:${color}; border:2.5px solid #0a0a0a;
      border-radius:50%;
      box-shadow:0 1px 4px rgba(0,0,0,0.35);
    "></div>`,
    className: '',
    iconAnchor: [size / 2, size / 2],
  });
}

function makeSquareIcon(color: string, size = 12) {
  return L.divIcon({
    html: `<div style="
      width:${size}px; height:${size}px;
      background:${color}; border:2.5px solid #0a0a0a;
      box-shadow:0 1px 4px rgba(0,0,0,0.35);
    "></div>`,
    className: '',
    iconAnchor: [size / 2, size / 2],
  });
}

interface Props {
  originCity: string;
  destCountry: 'DE' | 'NL' | 'TR';
  processorName?: string | null;
  transportMode: string;
  co2Tonnes?: number;
  className?: string;
}

const DEST_CITY: Record<string, string> = { DE: 'hamburg', NL: 'rotterdam', TR: 'istanbul' };
const DEST_LABEL: Record<string, string> = { DE: 'Hamburg, DE', NL: 'Rotterdam, NL', TR: 'İstanbul, TR' };
const MODE_COLOR: Record<string, string> = {
  kara: '#d6342a', deniz: '#1d4fd6', demiryolu: '#1f7a3a', hava: '#c97a17',
};

export default function RouteMap({ originCity, destCountry, processorName, transportMode, co2Tonnes, className = '' }: Props) {
  const mapRef    = useRef<HTMLDivElement>(null);
  const instanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Destroy previous instance if re-rendering
    if (instanceRef.current) {
      instanceRef.current.remove();
      instanceRef.current = null;
    }

    const originCoord    = resolveCoord(originCity);
    const destKey        = DEST_CITY[destCountry] ?? 'hamburg';
    const destCoord      = COORDS[destKey] ?? [53.55, 9.99];
    const processorCoord: [number, number] = [38.55, 34.50]; // Acıgöl / Genper konumu

    // Fit bounds center
    const allPoints: [number, number][] = [originCoord, processorCoord, destCoord];
    const bounds = L.latLngBounds(allPoints.map((c) => L.latLng(c[0], c[1])));

    const map = L.map(mapRef.current, {
      zoomControl: false,
      attributionControl: false,
      scrollWheelZoom: false,
      dragging: true,
      doubleClickZoom: false,
    });
    instanceRef.current = map;

    // OSM tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
    }).addTo(map);

    // Attribution — minimal
    L.control.attribution({ prefix: '© OSM' }).addTo(map);

    map.fitBounds(bounds, { padding: [36, 36] });

    const routeColor = MODE_COLOR[transportMode] ?? '#d6342a';

    // ── Route polyline (curved via intermediate point) ──
    const midLat = (originCoord[0] + destCoord[0]) / 2 + 3;
    const midLon = (originCoord[1] + destCoord[1]) / 2;
    const curve: [number, number][] = [originCoord, processorCoord, [midLat, midLon], destCoord];

    L.polyline(curve, {
      color: routeColor,
      weight: 3,
      opacity: 0.85,
      dashArray: transportMode === 'deniz' ? '8 5' : undefined,
    }).addTo(map);

    // ── Markers ──
    // Origin (red square)
    L.marker(originCoord, { icon: makeSquareIcon('#d6342a', 14) })
      .bindTooltip(`<b>${originCity}</b><br><span style="font-size:10px;color:#6b6b6b">Menşei</span>`, { direction: 'top', offset: [0, -8] })
      .addTo(map);

    // Processor (blue dot)
    if (processorName) {
      L.marker(processorCoord, { icon: makeIcon('#1d4fd6', 12) })
        .bindTooltip(`<b>${processorName}</b><br><span style="font-size:10px;color:#6b6b6b">İşleyici · Acıgöl</span>`, { direction: 'top', offset: [0, -8] })
        .addTo(map);
    }

    // Destination (green square)
    L.marker(destCoord, { icon: makeSquareIcon('#1f7a3a', 14) })
      .bindTooltip(`<b>${DEST_LABEL[destCountry]}</b><br><span style="font-size:10px;color:#6b6b6b">Alıcı Limanı</span>`, { direction: 'top', offset: [0, -8] })
      .addTo(map);

    // ── CO₂ overlay (bottom-left corner) ──
    if (co2Tonnes != null) {
      const info = L.control({ position: 'bottomleft' });
      info.onAdd = () => {
        const div = L.DomUtil.create('div');
        div.innerHTML = `
          <div style="
            background:white; border:2px solid #0a0a0a; padding:6px 10px;
            font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700;
            color:#1f7a3a; letter-spacing:0.05em; line-height:1.4;
          ">
            🌿 ${co2Tonnes.toFixed(2)} ton CO₂
          </div>`;
        return div;
      };
      info.addTo(map);
    }

    return () => {
      map.remove();
      instanceRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [originCity, destCountry, transportMode, co2Tonnes]);

  return (
    <div
      ref={mapRef}
      className={className}
      style={{ background: '#f0f0f0' }}
    />
  );
}
