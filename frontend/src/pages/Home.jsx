import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import SearchBar from '../components/SearchBar.jsx'
import SummaryCard from '../components/SummaryCard.jsx'
import TagChips from '../components/TagChips.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { useSummaries } from '../hooks/useSummaries.js'

export default function Home() {
  const { user } = useAuth()
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [tag, setTag] = useState('')
  const [page, setPage] = useState(1)

  // Debounce the search box so we don't hit the API on every keystroke.
  useEffect(() => {
    const t = setTimeout(() => {
      setSearch(searchInput)
      setPage(1)
    }, 350)
    return () => clearTimeout(t)
  }, [searchInput])

  const { results, count, next, previous, loading, error } = useSummaries({
    search,
    tag,
    page,
  })

  const selectTag = (slug) => {
    setTag(slug)
    setPage(1)
  }

  const pageSize = 10
  const totalPages = Math.max(1, Math.ceil(count / pageSize))

  return (
    <div>
      <div className="page-header">
        <h1>Book Summaries</h1>
        {user && (
          <Link to="/new" className="btn">
            + New Summary
          </Link>
        )}
      </div>

      <div className="toolbar">
        <SearchBar value={searchInput} onChange={setSearchInput} />
        <TagChips active={tag} onSelect={selectTag} />
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="loading">Loading…</div>
      ) : results.length === 0 ? (
        <div className="empty-state">No summaries found.</div>
      ) : (
        <>
          <div className="summary-grid">
            {results.map((s) => (
              <SummaryCard key={s.id} summary={s} onTagClick={selectTag} />
            ))}
          </div>
          <div className="pagination">
            <button
              className="btn secondary small"
              disabled={!previous}
              onClick={() => setPage((p) => p - 1)}
            >
              ← Prev
            </button>
            <span className="muted">
              Page {page} of {totalPages} · {count} total
            </span>
            <button
              className="btn secondary small"
              disabled={!next}
              onClick={() => setPage((p) => p + 1)}
            >
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  )
}
