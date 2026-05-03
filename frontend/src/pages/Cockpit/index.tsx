import { useLocation } from 'react-router-dom'
import AnalysisForm from './AnalysisForm'
import ResultPanel from './ResultPanel'
import WhatIfPanel from './WhatIfPanel'

export default function Cockpit() {
  const { pathname } = useLocation()
  const isWhatIf = pathname.includes('what-if')

  return (
    <div className="h-[calc(100vh-3.5rem)] flex bg-slate-50">
      <div className="w-[40%] min-w-[340px] z-10 overflow-hidden shadow-xl shadow-slate-200/20">
        <AnalysisForm />
      </div>
      <div className="flex-1 overflow-hidden relative">
        {isWhatIf ? <WhatIfPanel /> : <ResultPanel />}
      </div>
    </div>
  )
}
