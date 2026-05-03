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
