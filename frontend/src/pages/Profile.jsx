import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/client'
import SummaryCard from '../components/SummaryCard.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export default function Profile() {
  const { id } = useParams()
  const { user } = useAuth()
  const isOwn = user && String(user.id) === String(id)

  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Own-profile settings form
  const [settings, setSettings] = useState({ bio: '', avatar_url: '', medium_token: '' })
  const [hasToken, setHasToken] = useState(false)
  const [savingSettings, setSavingSettings] = useState(false)
  const [settingsNotice, setSettingsNotice] = useState('')

  useEffect(() => {
    setLoading(true)
    api
      .get(`/users/${id}/profile`)
      .then((r) => {
        setProfile(r.data)
        setSettings((s) => ({ ...s, bio: r.data.bio || '', avatar_url: r.data.avatar_url || '' }))
      })
      .catch(() => setError('Profile not found.'))
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (!isOwn) return
    api
      .get('/profile/me')
      .then((r) => setHasToken(r.data.has_medium_token))
      .catch(() => {})
  }, [isOwn])

  const saveSettings = async (e) => {
    e.preventDefault()
    setSavingSettings(true)
    setSettingsNotice('')
    try {
      const payload = { bio: settings.bio, avatar_url: settings.avatar_url }
      if (settings.medium_token) payload.medium_token = settings.medium_token
      const { data } = await api.patch('/profile/me', payload)
      setHasToken(data.has_medium_token)
      setProfile((p) => ({ ...p, bio: data.bio, avatar_url: data.avatar_url }))
      setSettings((s) => ({ ...s, medium_token: '' }))
      setSettingsNotice('Profile updated.')
    } catch {
      setSettingsNotice('Failed to update profile.')
    } finally {
      setSavingSettings(false)
    }
  }

  if (loading) return <div className="loading">Loading…</div>
  if (error) return <div className="error-banner">{error}</div>
  if (!profile) return null

  return (
    <div>
      <div className="page-header">
        <div className="row">
          {profile.avatar_url && (
            <img
              src={profile.avatar_url}
              alt=""
              width={56}
              height={56}
              style={{ borderRadius: '50%', objectFit: 'cover' }}
            />
          )}
          <div>
            <h1 style={{ margin: 0 }}>{profile.username}</h1>
            {profile.bio && <div className="muted">{profile.bio}</div>}
          </div>
        </div>
      </div>

      {isOwn && (
        <form className="card" onSubmit={saveSettings} style={{ marginBottom: 24 }}>
          <h3 style={{ marginTop: 0 }}>Profile settings</h3>
          {settingsNotice && <div className="muted">{settingsNotice}</div>}
          <div className="field">
            <label htmlFor="bio">Bio</label>
            <textarea
              id="bio"
              rows={2}
              value={settings.bio}
              onChange={(e) => setSettings({ ...settings, bio: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="avatar">Avatar URL</label>
            <input
              id="avatar"
              value={settings.avatar_url}
              onChange={(e) => setSettings({ ...settings, avatar_url: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="mt">
              Medium integration token {hasToken && <span className="badge published">set</span>}
            </label>
            <input
              id="mt"
              type="password"
              placeholder={hasToken ? '•••••••• (leave blank to keep)' : 'Paste to enable cross-posting'}
              value={settings.medium_token}
              onChange={(e) => setSettings({ ...settings, medium_token: e.target.value })}
            />
          </div>
          <button className="btn" type="submit" disabled={savingSettings}>
            {savingSettings ? 'Saving…' : 'Save settings'}
          </button>
        </form>
      )}

      <h2 style={{ fontSize: '1.2rem' }}>Summaries</h2>
      {profile.summaries.length === 0 ? (
        <div className="empty-state">No published summaries yet.</div>
      ) : (
        <div className="summary-grid">
          {profile.summaries.map((s) => (
            <SummaryCard key={s.id} summary={s} />
          ))}
        </div>
      )}
    </div>
  )
}
