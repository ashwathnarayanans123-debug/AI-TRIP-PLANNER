import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Landing from './pages/Landing'
import Planner from './pages/Planner'
import History from './pages/History'
import TripDetail from './pages/TripDetail'

/**
 * Root application shell with routing.
 */
export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/planner" element={<Planner />} />
          <Route path="/history" element={<History />} />
          <Route path="/trip/:id" element={<TripDetail />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
