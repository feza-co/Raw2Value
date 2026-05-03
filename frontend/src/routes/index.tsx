import { lazy, Suspense } from 'react'
import { createBrowserRouter, Outlet } from 'react-router-dom'
import { ProtectedRoute, PublicOnlyRoute } from './guards'
import PublicShell from '@/components/layout/PublicShell'
import AppShell from '@/components/layout/AppShell'

const Landing = lazy(() => import('@/pages/Landing'))
const Login = lazy(() => import('@/pages/Login'))
const Register = lazy(() => import('@/pages/Register'))
const Evidence = lazy(() => import('@/pages/Evidence'))
const Cockpit = lazy(() => import('@/pages/Cockpit'))
const History = lazy(() => import('@/pages/History'))
const Processors = lazy(() => import('@/pages/Processors'))
const Org = lazy(() => import('@/pages/Org'))
const Settings = lazy(() => import('@/pages/Settings'))

const wrap = (el: React.ReactNode) => (
  <Suspense fallback={null}>{el}</Suspense>
)

export const router = createBrowserRouter([
  {
    element: <PublicShell />,
    children: [
      { path: '/', element: wrap(<Landing />) },
      { path: '/evidence', element: wrap(<Evidence />) },
      {
        element: <PublicOnlyRoute><Outlet /></PublicOnlyRoute>,
        children: [
          { path: '/login', element: wrap(<Login />) },
          { path: '/register', element: wrap(<Register />) },
        ],
      },
    ],
  },
  {
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      { path: '/cockpit', element: wrap(<Cockpit />) },
      { path: '/cockpit/what-if', element: wrap(<Cockpit />) },
      { path: '/history', element: wrap(<History />) },
      { path: '/processors', element: wrap(<Processors />) },
      { path: '/org', element: wrap(<Org />) },
      { path: '/settings', element: wrap(<Settings />) },
    ],
  },
])
