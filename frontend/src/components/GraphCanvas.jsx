import { useRef, useEffect } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

export default function GraphCanvas({ graph, onEdgeClick }) {
  const fgRef = useRef()

  // auto-zoom to fit when graph updates
  useEffect(() => {
    if (fgRef.current && graph.nodes.length > 0) {
      setTimeout(() => fgRef.current.zoomToFit(400, 40), 300)
    }
  }, [graph])

  if (graph.nodes.length === 0) {
    return (
      <div style={emptyStyle}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>🧠</div>
        <p style={{ color: '#444', fontSize: '14px' }}>
          Upload a document to build your graph
        </p>
      </div>
    )
  }

  return (
    <ForceGraph2D
      ref={fgRef}
      graphData={graph}
      backgroundColor="#0f0f13"

      // nodes
      nodeLabel={n => n.label}
      nodeColor={n => nodeColor(n)}
      nodeRelSize={6}
      nodeCanvasObject={(node, ctx, globalScale) => {
        drawNode(node, ctx, globalScale)
      }}

      // links
      linkLabel={l => `${l.relation} — click to see source`}
      linkColor={() => '#3a3a52'}
      linkWidth={1.5}
      linkDirectionalArrowLength={4}
      linkDirectionalArrowRelPos={1}
      linkDirectionalParticles={2}
      linkDirectionalParticleSpeed={0.004}
      linkDirectionalParticleColor={() => '#7c6fff'}
      linkCanvasObjectMode={() => 'after'}
      linkCanvasObject={(link, ctx) => {
        drawLinkLabel(link, ctx)
      }}

      // interactions
      onLinkClick={onEdgeClick}
      onNodeDragEnd={node => {
        node.fx = node.x
        node.fy = node.y
      }}

      // physics
      d3AlphaDecay={0.02}
      d3VelocityDecay={0.3}
      cooldownTicks={100}
    />
  )
}

// ── node color by how many docs it appears in ────────────────────────────────
function nodeColor(node) {
  if (!node.doc_ids) return '#7c6fff'
  return node.doc_ids.length > 1 ? '#ff6b9d' : '#7c6fff'
}

// ── custom node drawing ───────────────────────────────────────────────────────
function drawNode(node, ctx, globalScale) {
  const label = node.label || node.id
  const fontSize = Math.max(10 / globalScale, 4)
  const r = 6

  // glow ring for cross-doc nodes
  if (node.doc_ids?.length > 1) {
    ctx.beginPath()
    ctx.arc(node.x, node.y, r + 3, 0, 2 * Math.PI)
    ctx.fillStyle = 'rgba(255,107,157,0.15)'
    ctx.fill()
  }

  // node circle
  ctx.beginPath()
  ctx.arc(node.x, node.y, r, 0, 2 * Math.PI)
  ctx.fillStyle = nodeColor(node)
  ctx.fill()

  // label below node
  ctx.font = `${fontSize}px Inter`
  ctx.fillStyle = '#e2e2e2'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'top'
  ctx.fillText(label, node.x, node.y + r + 2)
}

// ── relation label on link midpoint ──────────────────────────────────────────
function drawLinkLabel(link, ctx) {
  if (!link.source?.x) return

  const midX = (link.source.x + link.target.x) / 2
  const midY = (link.source.y + link.target.y) / 2

  ctx.font = '3px Inter'
  ctx.fillStyle = '#6a6a8a'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(link.relation, midX, midY)
}

const emptyStyle = {
  width: '100%',
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
}