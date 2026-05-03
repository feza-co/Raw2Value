import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AnalysisProvider } from './contexts/AnalysisContext';
import TopNav from './components/TopNav';
import UnifiedDashboard from './pages/UnifiedDashboard';
import GeoCarbonMap from './pages/GeoCarbonMap';
import LandingPage from './pages/LandingPage';
import type { ReactNode } from 'react';

function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <>
      <TopNav />
      <div className="pt-14">{children}</div>
    </>
  );
}

function App() {
  return (
    <AnalysisProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />

          <Route path="/dashboard" element={
            <DashboardShell><UnifiedDashboard /></DashboardShell>
          } />

          <Route path="/dashboard/geo" element={
            <DashboardShell><GeoCarbonMap /></DashboardShell>
          } />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AnalysisProvider>
  );
}

export default App;
