"use client"

import { useEffect, useRef } from "react"
import GUI from "lil-gui"
import { WebGPUParams } from "../webgpu/main"

export default function GUIComponent({ params }: { params: WebGPUParams }) {
  const guiRef = useRef<GUI | null>(null)
  if (!guiRef) {
    throw new Error("GUI ref is null")
  }

  useEffect(() => {
    const gui = new GUI()
    guiRef.current = gui

    // Dynamic simulation parameter sliders (ranges chosen per comments / sensible defaults)
    // DT: allow ~1/240 .. 1/3
    gui
      .add(params, "dt", 1.0 / 240.0, 1.0 / 3.0, 1.0 / 600.0)
      .name("Delta Time (dt)")

    // VISCOSITY: typical 1e-8 .. 1e-2, step small to allow fine tuning
    gui.add(params, "viscosity", 0, 1e-2, 1e-8).name("Viscosity")

    // DIFFUSION: typical 1e-8 .. 1e-3, keep small to preserve sharp color
    // gui.add(params, "diffusion", 1e-8, 1e-3, 1e-8).name("Diffusion")

    // DISSIPATION: dye fade factor per step (slightly <1 is common). constrain to [0.9, 1.0] for stability
    gui.add(params, "dissipation", 0.95, 1, 0.001).name("Dissipation")

    // VORTICITY: typical 0 .. 100
    gui.add(params, "vorticity", 0.0, 100.0, 1.0).name("Vorticity Strength")
    // GRAVITY: typical -100 .. 100
    gui.add(params, "gravity", -100.0, 100.0, 1.0).name("Gravity Strength")
    // FAUCET_DYE: typical 0 .. 50
    gui.add(params, "faucet_dye", 0.0, 500.0, 1.0).name("Faucet Dye Amount")

    return () => {
      gui.destroy()
      guiRef.current = null
    }
    // we intentionally only run this once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return <div className="gui-overlay" />
}
