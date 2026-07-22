import { useTags } from '../hooks/useTags.js'

export default function TagChips({ active, onSelect }) {
  const tags = useTags()

  return (
    <div className="chips">
      <span
        className={`chip ${!active ? 'active' : ''}`}
        onClick={() => onSelect('')}
      >
        All
      </span>
      {tags.map((tag) => (
        <span
          key={tag.id}
          className={`chip ${active === tag.slug ? 'active' : ''}`}
          onClick={() => onSelect(tag.slug)}
        >
          #{tag.name}
          {typeof tag.summary_count === 'number' && (
            <span className="count">({tag.summary_count})</span>
          )}
        </span>
      ))}
    </div>
  )
}
