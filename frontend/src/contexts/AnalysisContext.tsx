import { createContext, useContext, useState, type ReactNode } from 'react';
import type { AnalyzeRequest, AnalyzeResponse } from '../lib/types';

// Geriye dönük uyumluluk: eski isim ile alias.
type AnalyzeResponseOut = AnalyzeResponse;

interface AnalysisState {
  request: AnalyzeRequest | null;
  result: AnalyzeResponseOut | null;
}

interface AnalysisContextValue extends AnalysisState {
  setAnalysis: (req: AnalyzeRequest, res: AnalyzeResponseOut) => void;
  clearAnalysis: () => void;
}

const AnalysisContext = createContext<AnalysisContextValue | null>(null);

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AnalysisState>({ request: null, result: null });

  const setAnalysis = (request: AnalyzeRequest, result: AnalyzeResponseOut) =>
    setState({ request, result });

  const clearAnalysis = () => setState({ request: null, result: null });

  return (
    <AnalysisContext.Provider value={{ ...state, setAnalysis, clearAnalysis }}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis(): AnalysisContextValue {
  const ctx = useContext(AnalysisContext);
  if (!ctx) throw new Error('useAnalysis must be used within AnalysisProvider');
  return ctx;
}
