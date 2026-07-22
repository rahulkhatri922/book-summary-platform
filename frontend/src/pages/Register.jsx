import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await register(form.username, form.email, form.password)
      navigate('/', { replace: true })
    } catch (err) {
      const data = err.response?.data
      const msg =
        data?.username?.[0] || data?.password?.[0] || data?.email?.[0] || 'Registration failed'
      setError(msg)
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="card">
        <h1>Create account</h1>
        <form onSubmit={submit}>
          {error && <div className="error-banner">{error}</div>}
          <div className="field">
            <label htmlFor="username">Username</label>
            <input id="username" value={form.username} onChange={update('username')} autoFocus />
          </div>
          <div className="field">
            <label htmlFor="email">Email (optional)</label>
            <input id="email" type="email" value={form.email} onChange={update('email')} />
          </div>
          <div className="field">
            <label htmlFor="password">Password (min 6 chars)</label>
            <input
              id="password"
              type="password"
              value={form.password}
              onChange={update('password')}
            />
          </div>
          <button className="btn" type="submit" disabled={loading} style={{ width: '100%' }}>
            {loading ? 'Creating…' : 'Register'}
          </button>
        </form>
        <div className="switch">
          Already registered? <Link to="/login">Log in</Link>
        </div>
      </div>
    </div>
  )
}
