export const formatTRY = (value: number): string =>
  new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    maximumFractionDigits: 0,
  }).format(value)

export const formatCO2 = (kg: number): string => {
  if (kg >= 1000) return `${(kg / 1000).toFixed(2)} t CO₂`
  return `${kg.toFixed(1)} kg CO₂`
}

export const formatPct = (value: number, signed = false): string => {
  const pct = (value * 100).toFixed(1)
  return signed && value > 0 ? `+${pct}%` : `${pct}%`
}

export const formatDate = (iso: string): string =>
  new Intl.DateTimeFormat('tr-TR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(iso))

export const formatNumber = (value: number): string =>
  new Intl.NumberFormat('tr-TR').format(value)
