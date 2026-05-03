import { create } from 'zustand'
import type { AnalyzeResponseOut } from '@/types/analyze.types'

interface CockpitState {
  lastResult: AnalyzeResponseOut | null
  setLastResult: (result: AnalyzeResponseOut) => void
  clearResult: () => void
}

export const useCockpitStore = create<CockpitState>((set) => ({
  lastResult: null,
  setLastResult: (result) => set({ lastResult: result }),
  clearResult: () => set({ lastResult: null }),
}))
