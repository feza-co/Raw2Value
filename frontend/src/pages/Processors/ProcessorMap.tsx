import { useState, useMemo } from 'react'
import Map, { Marker, Popup, NavigationControl } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { NearbyProcessor } from '@/types/processor.types'

interface Props { processors: NearbyProcessor[] }

const mapStyle = {
  version: 8,
  sources: {
    carto: {
      type: 'raster',
      tiles: [
        'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
        'https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
        'https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png'
      ],
      tileSize: 256,
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
    }
  },
  layers: [
    {
      id: 'carto',
      type: 'raster',
      source: 'carto',
      minzoom: 0,
      maxzoom: 22
    }
  ]
}

export default function ProcessorMap({ processors }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const initialViewState = useMemo(() => {
    if (processors.length === 0) return { longitude: 35.0, latitude: 39.0, zoom: 5 }
    
    // Calculate center based on processors
    const sumLat = processors.reduce((acc, p) => acc + p.lat, 0)
    const sumLon = processors.reduce((acc, p) => acc + p.lon, 0)
    return {
      latitude: sumLat / processors.length,
      longitude: sumLon / processors.length,
      zoom: 6,
      pitch: 45
    }
  }, [processors])

  const selectedProcessor = processors.find(p => p.id === selectedId)

  return (
    <div className="bg-slate-50 border-b border-slate-100 flex flex-col h-[500px] relative overflow-hidden">
      <Map
        initialViewState={initialViewState}
        mapStyle={mapStyle as any}
        style={{ width: '100%', height: '100%' }}
        interactive={true}
        maxZoom={18}
      >
        <NavigationControl position="bottom-right" />
        
        {processors.map((p) => (
          <Marker
            key={p.id}
            latitude={p.lat}
            longitude={p.lon}
            anchor="bottom"
            onClick={(e) => {
              e.originalEvent.stopPropagation();
              setSelectedId(p.id)
            }}
          >
            <div className="w-8 h-8 flex items-center justify-center cursor-pointer transition-transform duration-200 hover:scale-125 hover:-translate-y-2 group">
              <div className="absolute w-8 h-8 bg-amber-500 rounded-full opacity-30 animate-ping group-hover:animate-none"></div>
              <div className="w-6 h-6 bg-amber-600 border-2 border-white rounded-full shadow-lg z-10 flex items-center justify-center text-white">
                <div className="w-2 h-2 bg-white rounded-full"></div>
              </div>
            </div>
          </Marker>
        ))}

        {selectedProcessor && (
          <Popup
            latitude={selectedProcessor.lat}
            longitude={selectedProcessor.lon}
            anchor="bottom"
            offset={32}
            onClose={() => setSelectedId(null)}
            className="rounded-2xl overflow-hidden shadow-xl z-50"
            closeButton={false}
          >
            <div className="p-4 w-64 font-body">
              <h3 className="font-display font-bold text-slate-900 mb-1 leading-tight">{selectedProcessor.name}</h3>
              <p className="text-xs text-slate-500 mb-3">{selectedProcessor.city}, {selectedProcessor.district}</p>
              
              <div className="flex gap-2 mb-3">
                {selectedProcessor.capabilities.can_process_material && (
                  <span className="px-2 py-0.5 bg-green-50 text-green-700 rounded-md text-[10px] font-bold uppercase tracking-wider">İşleme</span>
                )}
                {selectedProcessor.capabilities.has_storage && (
                  <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-md text-[10px] font-bold uppercase tracking-wider">Depo</span>
                )}
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-xs border-t border-slate-100 pt-3 mt-3">
                <div>
                  <p className="text-slate-400 font-medium">Uzaklık</p>
                  <p className="font-bold text-slate-800">{selectedProcessor.distance_km.toFixed(1)} km</p>
                </div>
                <div>
                  <p className="text-slate-400 font-medium">Kapasite</p>
                  <p className="font-bold text-slate-800">{selectedProcessor.capacity_ton_year ? `${selectedProcessor.capacity_ton_year.toLocaleString('tr-TR')} ton` : 'Bilinmiyor'}</p>
                </div>
              </div>
            </div>
          </Popup>
        )}
      </Map>
      
      {/* Overlay details */}
      <div className="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur-md px-4 py-3 rounded-2xl shadow-sm border border-white/50 pointer-events-none">
        <p className="font-body font-semibold text-slate-800 text-sm flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          {processors.length} Tesis Bulundu
        </p>
      </div>
    </div>
  )
}
