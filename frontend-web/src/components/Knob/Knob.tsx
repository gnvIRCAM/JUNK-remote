import { useRef, useState, type PointerEvent } from 'react'

type Props = { 
  label: string; 
  value?: number;
  onChange?: (value: number, delta: number) => void }

export function Knob({ label, value: controlled, onChange }: Props) {
  const [inner, setInner] = useState(0)
  const dragging = useRef(false)
  const value = dragging.current ? inner : controlled ?? inner
  const lastY = useRef(0)

  const down = (e: PointerEvent) => {
    e.currentTarget.setPointerCapture(e.pointerId)
    lastY.current = e.clientY
    dragging.current = true
    setInner(controlled ?? inner)
  }

  const up = () => { dragging.current = false }

  const move = (e: PointerEvent) => {
    if (!e.currentTarget.hasPointerCapture(e.pointerId)) return
    const delta = (lastY.current - e.clientY) / 150
    lastY.current = e.clientY
    if (delta === 0) return
    const next = Math.min(1, Math.max(0, value + delta))
    setInner(next)
    onChange?.(next, delta)
  }

  return (
    <div className="knob">
      <div
        className="dial"
        style={{ transform: `rotate(${-135 + value * 270}deg)` }}
        onPointerDown={down}
        onPointerMove={move}
        onPointerUp={up}
        onPointerCancel={up}
      />
      <span>{label}</span>
    </div>
  )
}