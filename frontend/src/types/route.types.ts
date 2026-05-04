export interface RoutePoint {
  lat: number
  lon: number
}

export interface RouteRequest {
  points: RoutePoint[]
  transport_mode: 'kara' | 'deniz' | 'demiryolu' | 'hava'
}

export interface RouteResponse {
  coordinates: number[][] // [[lon, lat], ...]
  distance_m: number
  duration_s: number
  source: 'ors_directions' | 'fallback_straight'
}
