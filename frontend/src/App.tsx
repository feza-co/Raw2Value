import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { RequireAuth, useAuth } from './lib/auth';
import { AppShell } from './components/AppShell';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { MaterialAnalyzerPage } from './pages/MaterialAnalyzerPage';
import { AIDecisionCockpitPage } from './pages/AIDecisionCockpitPage';
import { GeoCarbonMapPage } from './pages/GeoCarbonMapPage';
import { WhatIfSimulatorPage } from './pages/WhatIfSimulatorPage';
import { OfferBuilderPage } from './pages/OfferBuilderPage';
import { RawMaterialPassportPage } from './pages/RawMaterialPassportPage';
import { AIEvidencePage } from './pages/AIEvidencePage';
import { AdminPage } from './pages/AdminPage';

function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.32, ease: [0.2, 0.7, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}

function Protected({ children }: { children: React.ReactNode }) {
  return (
    <RequireAuth>
      <AppShell>
        <PageTransition>{children}</PageTransition>
      </AppShell>
    </RequireAuth>
  );
}

export default function App() {
  const { token, loading } = useAuth();
  const loc = useLocation();

  if (loading && token) {
    return <div className="empty">atlas yükleniyor…</div>;
  }

  return (
    <AnimatePresence mode="wait">
      <Routes location={loc} key={loc.pathname}>
        <Route path="/" element={
          token ? <Navigate to="/dashboard" replace /> : <PageTransition><LoginPage /></PageTransition>
        } />
        <Route path="/dashboard" element={<Protected><DashboardPage /></Protected>} />
        <Route path="/analyzer"  element={<Protected><MaterialAnalyzerPage /></Protected>} />
        <Route path="/cockpit"   element={<Protected><AIDecisionCockpitPage /></Protected>} />
        <Route path="/geo"       element={<Protected><GeoCarbonMapPage /></Protected>} />
        <Route path="/whatif"    element={<Protected><WhatIfSimulatorPage /></Protected>} />
        <Route path="/offer"     element={<Protected><OfferBuilderPage /></Protected>} />
        <Route path="/passport"  element={<Protected><RawMaterialPassportPage /></Protected>} />
        <Route path="/evidence"  element={<Protected><AIEvidencePage /></Protected>} />
        <Route path="/admin"     element={<Protected><AdminPage /></Protected>} />
        <Route path="*" element={<Navigate to={token ? '/dashboard' : '/'} replace />} />
      </Routes>
    </AnimatePresence>
  );
}
