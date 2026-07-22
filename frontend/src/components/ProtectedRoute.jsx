import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function ProtectedRoute({ children }) {
  const { user } = useAuth()
  const location = useLocation()
  const hasToken = Boolean(localStorage.getItem('token'))

  if (!user && !hasToken) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return children
}
