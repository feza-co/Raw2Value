import { z } from 'zod'

export const analyzeSchema = z.object({
  raw_material: z.enum(['pomza', 'perlit', 'kabak_cekirdegi']),
  tonnage: z.number().min(0.1).max(100000),
  quality: z.enum(['A', 'B', 'C', 'unknown']),
  origin_city: z.string().min(1),
  target_country: z.enum(['TR', 'DE', 'NL']),
  target_city: z.string().optional(),
  transport_mode: z.enum(['kara', 'deniz', 'demiryolu', 'hava']),
  priority: z.enum(['max_profit', 'low_carbon', 'fast_delivery']).default('max_profit'),
  input_mode: z.enum(['basic', 'advanced']).default('basic'),
  moisture_pct: z.number().min(0).max(100).optional(),
  purity_pct: z.number().min(0).max(100).optional(),
  particle_size_class: z.string().optional(),
  fx_scenario_pct: z.number().min(-0.2).max(0.2).default(0),
  cost_scenario_pct: z.number().min(-0.2).max(0.2).default(0),
})

export const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

export const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  full_name: z.string().optional(),
})

export type AnalyzeFormValues = z.infer<typeof analyzeSchema>
export type LoginFormValues = z.infer<typeof loginSchema>
export type RegisterFormValues = z.infer<typeof registerSchema>
