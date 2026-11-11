import { useState } from 'react'
import { ConnectPage } from './pages/ConnectPage/ConnectPage'
import { MenuPage } from './pages/MenuPage/MenuPage'
import { ControlPage } from './pages/ControlPage/ControlPage'
import './App.css'

type Page = 'menu' | 'control'

export default function App() {
  const [server, setServer] = useState<string>()
  const [page, setPage] = useState<Page>('menu')

  const connect = async (url: string) => {
    const s = await (await fetch(`${url}/state`)).json()
    setPage(s.page === 'patch' ? 'control' : 'menu')
    setServer(url)
  }

  if (!server) return <ConnectPage onConnect={connect} />

  return page === 'menu'
    ? <MenuPage server={server} onLoad={() => setPage('control')} />
    : <ControlPage server={server} onBack={() => setPage('menu')} />
}