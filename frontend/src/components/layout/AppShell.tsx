import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopBar from './TopBar'

export default function AppShell() {
  return (
    <div className="min-h-screen bg-parchment">
      <Sidebar />
      <TopBar />
      <main className="ml-16 pt-14 min-h-screen">
        <Outlet />
      </main>
    </div>
  )
}
