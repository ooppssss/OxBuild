export default function InsightsPanel({ insights, loading, onFetch }) {
  return (
    <div>
      <button
        onClick={onFetch}
        disabled={loading}
        style={btnStyle(loading)}
      >
        {loading ? 'Analysing...' : '✦ Find Hidden Links'}
      </button>

      {insights.length === 0 && (
        <p style={{ color: '#444', fontSize: '12px', marginTop: '16px', textAlign: 'center' }}>
          Ingest at least 2 documents then run analysis
        </p>
      )}

      <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {insights.map((ins, i) => (
          <div key={i} style={cardStyle(ins.confidence)}>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '10px', color: confidenceColor(ins.confidence), fontWeight: 600, textTransform: 'uppercase' }}>
                {ins.confidence}
              </span>
              <span style={{ fontSize: '10px', color: '#555' }}>
                {ins.suggested_relation}
              </span>
            </div>

            <p style={{ fontSize: '13px', color: '#e2e2e2', marginBottom: '6px' }}>
              <span style={{ color: '#7c6fff' }}>{ins.from_entity}</span>
              {' → '}
              <span style={{ color: '#ff6b9d' }}>{ins.to_entity}</span>
            </p>

            <p style={{ fontSize: '11px', color: '#888', lineHeight: 1.5 }}>
              {ins.reasoning}
            </p>

          </div>
        ))}
      </div>
    </div>
  )
}

function confidenceColor(c) {
  if (c === 'high')   return '#4ade80'
  if (c === 'medium') return '#facc15'
  return '#f87171'
}

function cardStyle(confidence) {
  return {
    background: '#0f0f13',
    border: `1px solid ${confidenceColor(confidence)}33`,
    borderRadius: '10px',
    padding: '12px',
    animation: 'fadeIn 0.3s ease',
  }
}

const btnStyle = (disabled) => ({
  width: '100%',
  padding: '10px',
  background: disabled ? '#2a2a3a' : 'linear-gradient(135deg, #7c6fff, #ff6b9d)',
  color: disabled ? '#555' : '#fff',
  border: 'none',
  borderRadius: '8px',
  fontSize: '13px',
  cursor: disabled ? 'not-allowed' : 'pointer',
  transition: 'opacity 0.2s',
})