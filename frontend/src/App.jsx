import { useState } from 'react'
import TextInput from './components/TextInput'
import FileInput from './components/FileInput'
import GraphCanvas from './components/GraphCanvas'
import InsightsPanel from './components/InsightsPanel'

export default function App() {
  const [graph, setGraph] = useState({ nodes: [], links: [] })
  const [loading, setLoading] = useState(false)
  const [selectedEdge, setSelectedEdge] = useState(null)
  const [insights, setInsights] = useState([])

  async function handleIngest(endpoint, options){
    setLoading(true)
    try{
        const res = await fetch(`http://localhost:8000${endpoint}`, options)
        const data = await res.json()

        setGraph({
            nodes: data.graph.nodes.map(n => ({ id: n.id, label: n.label, doc_ids: n.doc_ids })),
            links: data.graph.edges.map(e => ({
            source: e.source.toLowerCase(),
            target: e.target.toLowerCase(),
            relation: e.relation,
            source_text: e.source_text,
            doc_id: e.doc_id,
            })),
        })
    } catch(err){
        console.error('Ingest error: ', err)
    } finally{
        setLoading(false)
    }
  }

  async function handleInsights() {
    setLoading(true)
    try {
        const res = await fetch('http://localhost:8000/inference')
        const data = await res.json()
        setInsights(data.insights)
    } catch (err) {
        console.error('Inference error:', err)
    } finally {
        setLoading(false)
    }
    }


  return (
    <div style={{ display: 'flex', height: '100vh' }}>

      {/* Left panel — inputs */}
      <div style={{
        width: '320px',
        background: '#1a1a24',
        borderRight: '1px solid #2a2a3a',
        padding: '20px',
        overflowY: 'auto',
        flexShrink: 0,
      }}>
        <h2 style={{ color: '#7c6fff', marginBottom: '6px', fontSize: '18px' }}>
          GraphMind
        </h2>
        <p style={{ color: '#666', fontSize: '12px', marginBottom: '24px' }}>
          Structured Intelligence System
        </p>

        <TextInput onIngest={handleIngest} loading={loading} />
        <FileInput onIngest={handleIngest} loading={loading} />
      </div>

      {/* Centre — graph canvas */}
      <div style={{ flex: 1, position: 'relative', background: '#0f0f13' }}>
        <GraphCanvas
        graph={graph}
        onEdgeClick={edge => setSelectedEdge(edge)}
        />
        {selectedEdge && (
        <div style={{
            position: 'absolute',
            bottom: '24px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#1a1a24',
            border: '1px solid #7c6fff',
            borderRadius: '12px',
            padding: '16px 20px',
            maxWidth: '500px',
            width: '90%',
            zIndex: 10,
            animation: 'fadeIn 0.2s ease',
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: '#7c6fff', fontSize: '12px', fontWeight: 600 }}>
                {selectedEdge.source?.label || selectedEdge.source} →{' '}
                {selectedEdge.relation} →{' '}
                {selectedEdge.target?.label || selectedEdge.target}
            </span>
            <span
                onClick={() => setSelectedEdge(null)}
                style={{ color: '#666', cursor: 'pointer', fontSize: '16px' }}
            >×</span>
            </div>
            <p style={{ color: '#ccc', fontSize: '13px', lineHeight: 1.6 }}>
            "{selectedEdge.source_text}"
            </p>
            <p style={{ color: '#555', fontSize: '11px', marginTop: '8px' }}>
            from {selectedEdge.doc_id}
            </p>
        </div>
        )}
      </div>

      {/* Right panel — insights */}
      <div style={{
        width: '280px',
        background: '#1a1a24',
        borderLeft: '1px solid #2a2a3a',
        padding: '20px',
        overflowY: 'auto',
        flexShrink: 0,
      }}>
        <h3 style={{ color: '#7c6fff', marginBottom: '16px', fontSize: '14px' }}>
          Insights
        </h3>
        <InsightsPanel
            insights={insights}
            loading={loading}
            onFetch={handleInsights}
        />
      </div>

    </div>
  )
}