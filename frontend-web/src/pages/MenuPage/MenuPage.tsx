import { Knob } from '../../components/Knob/Knob'
import {useEffect, useState} from 'react';   

type Props = { server: string; onLoad: () => void }

export function MenuPage({ server, onLoad }: Props) {
  const [patchName, setPatchName] = useState<string>(""); 
  const [value, setValue] = useState<number>(0); 

  useEffect(() => {
    let fetchPatchName = async () => {
      let patch_name = ""
      try {
        let request = await fetch(`${server}/get_patch_name`); 
        let json = await request.json(); 
        patch_name = json["patch_name"]; 
      }
      catch (error) {
        console.log(error)
      } 
      setPatchName(patch_name); 

    }
    fetchPatchName(); 
  }, 
  [value])

  const click = async () => {
    await fetch(`${server}/action/button/0/click`)
    onLoad()
  }

  const wheel = (value_: number) => {
    setValue(value_); 
    fetch(`${server}/action/wheel/turn`, 
      { method: 'POST', 
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({index: 0, value: value_})
      })
  }

  return (
    <div className="control">
      <div className="top">
        <Knob label={patchName} onChange={(value, _) => wheel(value)} />
        <button onClick={click}>Load</button>
      </div>
    </div>
  )
}