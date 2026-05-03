export const MATERIALS = [
  { value: 'pomza', label: 'Pomza' },
  { value: 'perlit', label: 'Perlit' },
  { value: 'kabak_cekirdegi', label: 'Kabak Çekirdeği' },
] as const

export const QUALITY_GRADES = [
  { value: 'A', label: 'A' },
  { value: 'B', label: 'B' },
  { value: 'C', label: 'C' },
  { value: 'unknown', label: 'Bilinmiyor' },
] as const

export const TRANSPORT_MODES = [
  { value: 'kara', label: 'Kara', co2Hint: '0.100 kg CO₂/ton-km' },
  { value: 'deniz', label: 'Deniz', co2Hint: '0.015 kg CO₂/ton-km' },
  { value: 'demiryolu', label: 'Demiryolu', co2Hint: '0.030 kg CO₂/ton-km' },
  { value: 'hava', label: 'Hava', co2Hint: '0.500 kg CO₂/ton-km' },
] as const

export const TARGET_COUNTRIES = [
  { value: 'TR', label: 'Türkiye' },
  { value: 'DE', label: 'Almanya' },
  { value: 'NL', label: 'Hollanda' },
] as const

export const PRIORITIES = [
  { value: 'max_profit', label: 'Max Kâr' },
  { value: 'low_carbon', label: 'Düşük Karbon' },
  { value: 'fast_delivery', label: 'Hızlı Teslimat' },
] as const

export const NEVŞEHIR_COORDS = { lat: 37.9738, lon: 34.6565 }

// Demo akışında kullanılan büyük şehir koordinatları — harita çiziminde
// origin/destination noktası için fallback.
export const CITY_COORDS: Record<string, { lat: number; lon: number }> = {
  // TR
  nevsehir: { lat: 38.6939, lon: 34.6857 },
  acigol: { lat: 38.5478, lon: 34.5028 },
  istanbul: { lat: 41.0082, lon: 28.9784 },
  izmir: { lat: 38.4192, lon: 27.1287 },
  ankara: { lat: 39.9334, lon: 32.8597 },
  // DE
  hamburg: { lat: 53.5511, lon: 9.9937 },
  berlin: { lat: 52.52, lon: 13.405 },
  // NL
  rotterdam: { lat: 51.9244, lon: 4.4777 },
  amsterdam: { lat: 52.3676, lon: 4.9041 },
}

export const COUNTRY_DEFAULT_CITY: Record<string, string> = {
  TR: 'istanbul',
  DE: 'hamburg',
  NL: 'rotterdam',
}

const turkishMap: Record<string, string> = {
  'ç': 'c', 'Ç': 'c', 'ğ': 'g', 'Ğ': 'g', 'ı': 'i', 'I': 'i', 'İ': 'i',
  'ö': 'o', 'Ö': 'o', 'ş': 's', 'Ş': 's', 'ü': 'u', 'Ü': 'u',
}

export function normalizeCityKey(name: string | null | undefined): string {
  if (!name) return ''
  return name
    .toLowerCase()
    .split('')
    .map((c) => turkishMap[c] ?? c)
    .join('')
    .replace(/[^a-z]/g, '')
}

export function lookupCityCoords(name: string | null | undefined):
  | { lat: number; lon: number }
  | null {
  const key = normalizeCityKey(name)
  return CITY_COORDS[key] ?? null
}
