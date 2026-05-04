import { create } from 'zustand'
import type { AnalyzeRequest, AnalyzeResponseOut } from '@/types/analyze.types'

interface CockpitState {
  lastResult: AnalyzeResponseOut | null
  lastPayload: AnalyzeRequest | null
  setLastResult: (result: AnalyzeResponseOut, payload?: AnalyzeRequest) => void
  clearResult: () => void
}

export const useCockpitStore = create<CockpitState>((set) => ({
  lastResult: null,
  lastPayload: null,
  setLastResult: (result, payload) =>
    set((s) => ({
      lastResult: result,
      lastPayload: payload ?? s.lastPayload,
    })),
  clearResult: () => set({ lastResult: null, lastPayload: null }),
}))
