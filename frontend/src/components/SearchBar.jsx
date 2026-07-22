export default function SearchBar({ value, onChange }) {
  return (
    <input
      type="search"
      placeholder="Search summaries by title or body…"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      aria-label="Search summaries"
    />
  )
}
