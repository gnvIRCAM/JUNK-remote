import { useState } from 'react'

export function ConnectPage({ onConnect }: { onConnect: (url: string) => void }) {
  const [url, setUrl] = useState('http://127.0.0.1:8000')
  const [error, setError] = useState('')

  const connect = async () => {
    try {
      await fetch(url)
      onConnect(url)
    } catch {
      setError('Cannot reach server')
    }
  }

  return (
    <div className="connect">
      <input value={url} onChange={(e) => setUrl(e.target.value)} />
      <button onClick={connect}>Connect</button>
      {error && <p>{error}</p>}
    </div>
  )
}