import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="brand">
          📚 BookSummaries
        </Link>
        <span className="spacer" />
        <Link to="/">Home</Link>
        {user && <Link to="/new">New Summary</Link>}
        {user && <Link to={`/users/${user.id}/profile`}>My Profile</Link>}
        {user ? (
          <>
            <span className="muted">{user.username}</span>
            <button className="btn small secondary" onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  )
}
