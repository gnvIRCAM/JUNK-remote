import { useEffect, useState } from 'react'
import { Knob } from '../../components/Knob/Knob'

const BUTTONS = ['Load', 'Write', 'Layer', 'Rand.']
const KNOBS = Array.from({ length: 8 }, (_, i) => i)
const NUM_PRESETS = 16

type State = { preset: number; knobs: number[], layer: 'A' | 'B' }
type Props = { server: string; onBack: () => void }

export function ControlPage({ server, onBack }: Props) {
  const [preset, setPreset] = useState<number>(0)
  const [values, setValues] = useState<number[]>(Array(KNOBS.length).fill(0))
  const [layer, setLayer] = useState<'A' | 'B'>('A')
  
  const refresh = async () => {
  try {
    const res = await fetch(`${server}/state`)
    if (!res.ok) throw new Error(`state: ${res.status}`)
    const state: State = await res.json()
    setPreset(state.preset)
    setValues(KNOBS.map((i) => state.knobs[i] ?? 0))
    setLayer(state.layer)
  } catch (e) {
    console.error(e)
  }
  }

  useEffect(() => { refresh() }, [])

  const click = async (idx: number) => {
    await fetch(`${server}/action/button/${idx}/click`)
    if (idx===0 && preset===-1) {onBack()} // Back to menu
    await refresh() // Load / Rand. change values on the server
  }

  const wheel = (value: number) => {
    const p = Math.ceil(value * NUM_PRESETS) - 1
    setPreset(p)
    return fetch(`${server}/action/wheel/turn`, 
      { method: 'POST', 
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({index: 0, value: value})
      })
  }

  const turn = (idx: number, value: number) => {
    setValues((v) => v.map((x, i) => (i === idx ? value : x)))
    return fetch(`${server}/action/knob/${idx}/turn`, 
      { method: 'POST', 
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({index: idx, value: value})
       })
  }

  return (
    <div className="control">
      <div className="top">
        <Knob
          label={preset === -1 ? 'Menu' : `Preset ${preset+1}`}
          value={(preset + 1) / NUM_PRESETS}
          onChange={(value) => wheel(value)}
        />
        <button key={'Load'} onClick={() => click(0)}>{BUTTONS[0]}</button>
        <button key={'Write'} onClick={() => click(1)}>{BUTTONS[1]}</button>
        <button key={'Layer'} onClick={() => click(2)}>{BUTTONS[2]} {layer}</button>
        <button key={'Rand.'} onClick={() => click(3)}>{BUTTONS[3]}</button>
      </div>
      <div className="grid">
        {KNOBS.map((id) => (
          <Knob
            key={id}
            label={values[id].toFixed(2)}
            value={values[id]}
            onChange={(value) => turn(id, value)}
          />
        ))}
      </div>
    </div>
  )
}