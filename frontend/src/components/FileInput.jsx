import { useRef, useState } from 'react'

export default function FileInput({ onIngest, loading }) {
  const pdfRef = useRef()
  const imgRef = useRef()
  const [pdfName, setPdfName] = useState('')
  const [imgName, setImgName] = useState('')

  async function handleFile(ref, endpoint, setName) {
    const file = ref.current.files[0]
    if (!file) return
    setName(file.name)
    const form = new FormData()
    form.append('file', file)
    await onIngest(endpoint, { method: 'POST', body: form })
  }

  return (
    <div style={{ marginBottom: '24px' }}>

      <label style={labelStyle}>PDF upload</label>
      <div
        style={dropStyle}
        onClick={() => pdfRef.current.click()}
      >
        <input
          ref={pdfRef}
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={() => handleFile(pdfRef, '/ingest/pdf', setPdfName)}
        />
        <span style={{ fontSize: '20px' }}>📄</span>
        <span style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
          {pdfName || 'Click to upload PDF'}
        </span>
      </div>

      <label style={{ ...labelStyle, marginTop: '12px' }}>Image upload</label>
      <div
        style={dropStyle}
        onClick={() => imgRef.current.click()}
      >
        <input
          ref={imgRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={() => handleFile(imgRef, '/ingest/image', setImgName)}
        />
        <span style={{ fontSize: '20px' }}>🖼️</span>
        <span style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
          {imgName || 'Click to upload image'}
        </span>
      </div>

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

const dropStyle = {
  width: '100%',
  border: '1px dashed #3a3a52',
  borderRadius: '8px',
  padding: '16px',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  cursor: 'pointer',
  transition: 'border-color 0.2s',
  background: '#0f0f13',
}