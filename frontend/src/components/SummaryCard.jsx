import { Link } from 'react-router-dom'

export default function SummaryCard({ summary, onTagClick }) {
  return (
    <div className="summary-card">
      <div>
        <Link to={`/summaries/${summary.id}`}>
          <h3>{summary.title}</h3>
        </Link>
        <div className="by">
          by {summary.author} · {summary.created_by}
        </div>
      </div>
      {!summary.is_published && <span className="badge draft">Draft</span>}
      <div className="card-tags">
        {summary.tags.map((t) => (
          <span
            key={t.id}
            className="tag-pill"
            onClick={(e) => {
              e.preventDefault()
              onTagClick?.(t.slug)
            }}
          >
            #{t.name}
          </span>
        ))}
      </div>
    </div>
  )
}
