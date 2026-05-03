import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
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
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data} margin={{ top: 12, right: 12, bottom: 12, left: 12 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
        <XAxis dataKey="name" tick={{ fontFamily: 'var(--font-body)', fontSize: 13, fontWeight: 500, fill: '#64748B' }} axisLine={false} tickLine={false} dy={10} />
        <YAxis tickFormatter={(v: number) => `₺${(v / 1_000_000).toFixed(1)}M`} tick={{ fontFamily: 'var(--font-mono)', fontSize: 12, fill: '#94A3B8' }} axisLine={false} tickLine={false} dx={-10} />
        <Tooltip 
          formatter={(v) => formatTRY(Number(v))} 
          contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)', fontFamily: 'var(--font-display)', fontWeight: 600 }}
          cursor={{ fill: '#F1F5F9' }}
        />
        <Bar dataKey="profit" fill="#F59E0B" radius={[6, 6, 0, 0]} barSize={40} />
      </BarChart>
    </ResponsiveContainer>
  )
}
