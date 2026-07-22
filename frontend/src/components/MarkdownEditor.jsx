import MDEditor from '@uiw/react-md-editor'

export default function MarkdownEditor({ value, onChange }) {
  return (
    <div data-color-mode="light">
      <MDEditor
        value={value}
        onChange={(v) => onChange(v ?? '')}
        height={420}
        preview="live"
      />
    </div>
  )
}
