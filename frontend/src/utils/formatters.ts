export const formatTRY = (value: number | null | undefined): string =>
  value == null
    ? '—'
    : new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY',
        maximumFractionDigits: 0,
      }).format(value)

export const formatCO2 = (kg: number | null | undefined): string => {
  if (kg == null) return '—'
  if (kg >= 1000) return `${(kg / 1000).toFixed(2)} t CO2`
  return `${kg.toFixed(1)} kg CO2`
}

export const formatPct = (
  value: number | null | undefined,
  signed = false,
): string => {
  if (value == null) return '—'
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

export const formatNumber = (value: number | null | undefined): string =>
  value == null ? '—' : new Intl.NumberFormat('tr-TR').format(value)
