import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/AuthContext.jsx'

export default function SummaryDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    api
      .get(`/summaries/${id}`)
      .then((r) => setSummary(r.data))
      .catch((e) =>
        setError(e.response?.status === 404 ? 'Summary not found.' : 'Failed to load.')
      )
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="loading">Loading…</div>
  if (error) return <div className="error-banner">{error}</div>
  if (!summary) return null

  const isOwner = user && user.id === summary.created_by_id

  return (
    <article>
      <div className="page-header">
        <div>
          <h1 style={{ marginBottom: 4 }}>{summary.title}</h1>
          <div className="muted">
            by {summary.author} ·{' '}
            <Link to={`/users/${summary.created_by_id}/profile`}>
              {summary.created_by}
            </Link>{' '}
            · {summary.is_published ? (
              <span className="badge published">Published</span>
            ) : (
              <span className="badge draft">Draft</span>
            )}
          </div>
        </div>
        {isOwner && (
          <button className="btn secondary" onClick={() => navigate(`/summaries/${id}/edit`)}>
            Edit
          </button>
        )}
      </div>

      <div className="row" style={{ marginBottom: 16 }}>
        {summary.tags.map((t) => (
          <span key={t.id} className="tag-pill">
            #{t.name}
          </span>
        ))}
        {summary.medium_url && (
          <a
            className="medium-link"
            href={summary.medium_url}
            target="_blank"
            rel="noreferrer"
          >
            ↗ View on Medium
          </a>
        )}
      </div>

      <div className="markdown-body">
        <ReactMarkdown>{summary.body}</ReactMarkdown>
      </div>
    </article>
  )
}
