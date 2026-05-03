import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { WhatIfResultItem } from '@/types/analyze.types'
import { formatTRY } from '@/utils/formatters'

interface Props { results: WhatIfResultItem[] }

export default function WhatIfChart({ results }: Props) {
  const data = results.map((r) => ({
    name: r.scenario,
    profit: r.expected_profit_try,
    co2: r.co2_kg,
  }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
        <XAxis dataKey="name" tick={{ fontFamily: 'var(--font-body)', fontSize: 11 }} />
        <YAxis tickFormatter={(v: number) => `₺${(v / 1_000_000).toFixed(1)}M`} tick={{ fontFamily: 'var(--font-mono)', fontSize: 10 }} />
        <Tooltip formatter={(v) => formatTRY(Number(v))} />
        <Bar dataKey="profit" fill="#C8973A" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
