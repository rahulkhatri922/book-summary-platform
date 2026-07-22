import { Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Home from './pages/Home.jsx'
import Login from './pages/Login.jsx'
import Profile from './pages/Profile.jsx'
import Register from './pages/Register.jsx'
import SummaryDetail from './pages/SummaryDetail.jsx'
import SummaryEdit from './pages/SummaryEdit.jsx'

export default function App() {
  return (
    <>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/summaries/:id" element={<SummaryDetail />} />
          <Route path="/users/:id/profile" element={<Profile />} />
          <Route
            path="/new"
            element={
              <ProtectedRoute>
                <SummaryEdit />
              </ProtectedRoute>
            }
          />
          <Route
            path="/summaries/:id/edit"
            element={
              <ProtectedRoute>
                <SummaryEdit />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </>
  )
}
