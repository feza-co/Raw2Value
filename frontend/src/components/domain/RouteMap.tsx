import { useMemo } from 'react'
import Map, { Marker, Source, Layer, NavigationControl } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { NearbyProcessor } from '@/types/processor.types'

interface Coord {
  lat: number
  lon: number
  label: string
  kind: 'origin' | 'processor' | 'destination'
}

interface Props {
  origin: { lat: number; lon: number; label: string } | null
  destination: { lat: number; lon: number; label: string } | null
  processors: NearbyProcessor[]
  selectedProcessor?: NearbyProcessor | null
}

const mapStyle = {
  version: 8,
  sources: {
    carto: {
      type: 'raster',
      tiles: [
        'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
        'https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
        'https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
      ],
      tileSize: 256,
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    },
  },
  layers: [
    { id: 'carto', type: 'raster', source: 'carto', minzoom: 0, maxzoom: 22 },
  ],
}

const PIN_COLORS: Record<Coord['kind'], string> = {
  origin: 'bg-emerald-600',
  processor: 'bg-amber-600',
  destination: 'bg-rose-600',
}

const PIN_LABELS: Record<Coord['kind'], string> = {
  origin: 'Çıkış',
  processor: 'İşleyici',
  destination: 'Hedef',
}

export default function RouteMap({ origin, destination, processors, selectedProcessor }: Props) {
  const coords: Coord[] = useMemo(() => {
    const out: Coord[] = []
    if (origin) out.push({ ...origin, kind: 'origin' })
    if (selectedProcessor) {
      out.push({
        lat: selectedProcessor.lat,
        lon: selectedProcessor.lon,
        label: selectedProcessor.name,
        kind: 'processor',
      })
    }
    if (destination) out.push({ ...destination, kind: 'destination' })
    return out
  }, [origin, destination, selectedProcessor])

  const initialViewState = useMemo(() => {
    const points = coords.length > 0 ? coords : [{ lat: 39, lon: 35 }]
    const lats = points.map((p) => p.lat)
    const lons = points.map((p) => p.lon)
    const minLat = Math.min(...lats)
    const maxLat = Math.max(...lats)
    const minLon = Math.min(...lons)
    const maxLon = Math.max(...lons)
    const centerLat = (minLat + maxLat) / 2
    const centerLon = (minLon + maxLon) / 2
    const span = Math.max(maxLat - minLat, maxLon - minLon, 0.5)
    const zoom = span > 20 ? 3 : span > 10 ? 4 : span > 5 ? 5 : span > 2 ? 6 : 7
    return { longitude: centerLon, latitude: centerLat, zoom }
  }, [coords])

  // Path: origin → processor → destination (varsa)
  const pathCoords = coords.map((c) => [c.lon, c.lat])
  const pathFeature = pathCoords.length >= 2 ? {
    type: 'Feature' as const,
    geometry: { type: 'LineString' as const, coordinates: pathCoords },
    properties: {},
  } : null

  return (
    <div className="relative h-[420px] w-full overflow-hidden rounded-3xl border border-slate-200">
      <Map
        initialViewState={initialViewState}
        mapStyle={mapStyle as never}
        style={{ width: '100%', height: '100%' }}
        interactive={true}
        maxZoom={18}
      >
        <NavigationControl position="bottom-right" />

        {pathFeature && (
          <Source id="route-path" type="geojson" data={pathFeature}>
            <Layer
              id="route-path-line"
              type="line"
              paint={{
                'line-color': '#d97706',
                'line-width': 3,
                'line-dasharray': [2, 2],
                'line-opacity': 0.85,
              }}
            />
          </Source>
        )}

        {/* Yakındaki işleyici noktaları (seçilmemiş) */}
        {processors
          .filter((p) => !selectedProcessor || p.id !== selectedProcessor.id)
          .map((p) => (
            <Marker key={p.id} latitude={p.lat} longitude={p.lon} anchor="bottom">
              <div className="w-5 h-5 rounded-full bg-amber-300 border-2 border-white shadow-md" title={p.name} />
            </Marker>
          ))}

        {/* Origin / processor / destination */}
        {coords.map((c, i) => (
          <Marker key={`${c.kind}-${i}`} latitude={c.lat} longitude={c.lon} anchor="bottom">
            <div className="flex flex-col items-center pointer-events-none">
              <div className="px-2 py-1 mb-1 rounded-md bg-white shadow-sm border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap">
                {PIN_LABELS[c.kind]}: {c.label}
              </div>
              <div className={`w-7 h-7 rounded-full ${PIN_COLORS[c.kind]} border-2 border-white shadow-lg flex items-center justify-center`}>
                <div className="w-2 h-2 bg-white rounded-full" />
              </div>
            </div>
          </Marker>
        ))}
      </Map>

      <div className="absolute top-3 left-3 z-10 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-xl shadow-sm border border-white/60 text-xs font-medium text-slate-700 flex items-center gap-3">
        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-600" /> Çıkış</span>
        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-600" /> İşleyici</span>
        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-rose-600" /> Hedef</span>
      </div>
    </div>
  )
}
