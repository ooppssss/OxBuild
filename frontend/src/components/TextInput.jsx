import { useState } from 'react'

export default function TextInput({ onIngest, loading }) {
  const [text, setText] = useState('')
  const [docId, setDocId] = useState('')

  async function handleSubmit() {
    if (!text.trim()) return
    await onIngest('/ingest/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, doc_id: docId || undefined }),
    })
    setText('')
  }

  return (
    <div style={{ marginBottom: '24px' }}>
      <label style={labelStyle}>Doc label (optional)</label>
      <input
        value={docId}
        onChange={e => setDocId(e.target.value)}
        placeholder="e.g. article_1"
        style={inputStyle}
      />
      <label style={labelStyle}>Paste text</label>
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Paste any text here..."
        rows={5}
        style={{ ...inputStyle, resize: 'vertical' }}
      />
      <button
        onClick={handleSubmit}
        disabled={loading || !text.trim()}
        style={btnStyle(loading || !text.trim())}
      >
        {loading ? 'Processing...' : 'Extract Graph'}
      </button>
    </div>
  )
}

const labelStyle = {
  display: 'block',
  fontSize: '11px',
  color: '#888',
  marginBottom: '6px',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
}

const inputStyle = {
  width: '100%',
  background: '#0f0f13',
  border: '1px solid #2a2a3a',
  borderRadius: '8px',
  padding: '10px',
  color: '#e2e2e2',
  fontSize: '13px',
  marginBottom: '12px',
  outline: 'none',
}

const btnStyle = (disabled) => ({
  width: '100%',
  padding: '10px',
  background: disabled ? '#2a2a3a' : '#7c6fff',
  color: disabled ? '#555' : '#fff',
  border: 'none',
  borderRadius: '8px',
  fontSize: '13px',
  cursor: disabled ? 'not-allowed' : 'pointer',
  transition: 'background 0.2s',
})