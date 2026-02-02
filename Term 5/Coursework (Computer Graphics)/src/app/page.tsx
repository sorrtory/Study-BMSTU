"use client"

import GitHubBadge from "./components/Badge"
import GUIComponent from "./components/GUI"
import WebGPUCanvas from "./components/WebGPUCanvas"
import { MouseInfo, WebGPUParams } from "./webgpu/main"
import {
  VISCOSITY,
  DIFFUSION,
  DISSIPATION,
  DELTA_T,
  FAUCET_DYE,
  GRAVITY,
  VORTEX_STRENGTH
} from "./webgpu/init"

const CANVAS_WIDTH = 750
const CANVAS_HEIGHT = 750

const mouseInfo: MouseInfo = {
  current_pos: [CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2],
  prev_pos: [CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2],
  is_pressed: false,
  velocity: [0, 0]
}

const params: WebGPUParams = {
  viscosity: VISCOSITY,
  diffusion: DIFFUSION,
  dissipation: DISSIPATION,
  dt: DELTA_T,
  vorticity: VORTEX_STRENGTH,
  gravity: GRAVITY,
  faucet_dye: FAUCET_DYE,

  mouse: mouseInfo
}

// This parameters can be changed at runtime via the lil-gui interface
export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="py-1 text-center text-white font-sans">
        <GitHubBadge />
        <h1 className="inline-block min-w-min">WebGPU Triangle Example</h1>
      </header>

      <aside>
        <GUIComponent params={params} />
      </aside>

      <main className="my-auto flex items-center justify-center">
        <WebGPUCanvas
          params={params}
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
        />
      </main>
    </div>
  )
}
