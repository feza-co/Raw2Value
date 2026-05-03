import { useLocation } from 'react-router-dom'
import AnalysisForm from './AnalysisForm'
import ResultPanel from './ResultPanel'
import WhatIfPanel from './WhatIfPanel'

export default function Cockpit() {
  const { pathname } = useLocation()
  const isWhatIf = pathname.includes('what-if')

  return (
    <div className="h-[calc(100vh-3.5rem)] flex">
      <div className="w-[40%] min-w-[340px] border-r border-stone-100 overflow-hidden">
        <AnalysisForm />
      </div>
      <div className="flex-1 overflow-hidden">
        {isWhatIf ? <WhatIfPanel /> : <ResultPanel />}
      </div>
    </div>
  )
}
