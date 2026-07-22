import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../api/client'
import MarkdownEditor from '../components/MarkdownEditor.jsx'

export default function SummaryEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const editing = Boolean(id)

  const [title, setTitle] = useState('')
  const [author, setAuthor] = useState('')
  const [body, setBody] = useState('')
  const [tagsInput, setTagsInput] = useState('')
  const [isPublished, setIsPublished] = useState(false)
  const [mediumUrl, setMediumUrl] = useState(null)

  const [loading, setLoading] = useState(editing)
  const [saving, setSaving] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  useEffect(() => {
    if (!editing) return
    api
      .get(`/summaries/${id}`)
      .then((r) => {
        const s = r.data
        setTitle(s.title)
        setAuthor(s.author)
        setBody(s.body)
        setTagsInput(s.tags.map((t) => t.name).join(', '))
        setIsPublished(s.is_published)
        setMediumUrl(s.medium_url)
      })
      .catch(() => setError('Could not load this summary.'))
      .finally(() => setLoading(false))
  }, [id, editing])

  const parseTags = () =>
    tagsInput
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)

  const save = async (e) => {
    e.preventDefault()
    if (!title.trim() || !body.trim()) {
      setError('Title and body are required.')
      return
    }
    setSaving(true)
    setError('')
    setNotice('')
    const payload = { title, author, body, tags: parseTags() }
    try {
      if (editing) {
        await api.put(`/summaries/${id}`, payload)
        setNotice('Saved.')
      } else {
        const { data } = await api.post('/summaries', payload)
        // Go to edit mode for the new summary so it can be published.
        navigate(`/summaries/${data.id}/edit`, { replace: true })
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save.')
    } finally {
      setSaving(false)
    }
  }

  const publish = async () => {
    setPublishing(true)
    setError('')
    setNotice('')
    try {
      const { data } = await api.post(`/summaries/${id}/publish`)
      setIsPublished(true)
      setMediumUrl(data.medium_url)
      setNotice(
        data.medium_url
          ? 'Published and cross-posted to Medium!'
          : 'Published locally (no Medium cross-post).'
      )
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to publish.')
    } finally {
      setPublishing(false)
    }
  }

  if (loading) return <div className="loading">Loading…</div>

  return (
    <div>
      <div className="page-header">
        <h1>{editing ? 'Edit summary' : 'New summary'}</h1>
        {editing && (
          <span className={`badge ${isPublished ? 'published' : 'draft'}`}>
            {isPublished ? 'Published' : 'Draft'}
          </span>
        )}
      </div>

      {error && <div className="error-banner">{error}</div>}
      {notice && (
        <div className="error-banner" style={{ background: '#e6f7ef', borderColor: '#0a7d50', color: '#0a7d50' }}>
          {notice}
        </div>
      )}

      <form onSubmit={save} className="card">
        <div className="field">
          <label htmlFor="title">Book title</label>
          <input id="title" value={title} onChange={(e) => setTitle(e.target.value)} autoFocus />
        </div>
        <div className="field">
          <label htmlFor="author">Book author</label>
          <input id="author" value={author} onChange={(e) => setAuthor(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="tags">Tags (comma-separated)</label>
          <input
            id="tags"
            value={tagsInput}
            onChange={(e) => setTagsInput(e.target.value)}
            placeholder="productivity, psychology"
          />
        </div>
        <div className="field">
          <label>Summary (Markdown)</label>
          <MarkdownEditor value={body} onChange={setBody} />
        </div>

        <div className="row">
          <button className="btn" type="submit" disabled={saving}>
            {saving ? 'Saving…' : editing ? 'Save changes' : 'Create summary'}
          </button>
          {editing && (
            <button
              type="button"
              className="btn accent"
              onClick={publish}
              disabled={publishing}
            >
              {publishing ? 'Publishing…' : isPublished ? 'Re-publish to Medium' : 'Publish to Medium'}
            </button>
          )}
          {mediumUrl && (
            <a className="medium-link" href={mediumUrl} target="_blank" rel="noreferrer">
              ↗ View on Medium
            </a>
          )}
        </div>
      </form>
    </div>
  )
}
