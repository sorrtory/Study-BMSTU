import {
    CreateLayouts,
    InitUniforms,
    CreateBindGroups,
    InitSimBuffers,
    CreatePipelines
} from "./init"
import { Render } from "./render"
import { createLoop as CreateLoop } from "./common"

export type WebGPUParams = {
    viscosity: number
    diffusion: number
    dissipation: number
    dt: number
    vorticity: number
    gravity: number
    faucet_dye: number

    mouse: MouseInfo
}

export type MouseInfo = {
    current_pos: [number, number]
    prev_pos: [number, number]
    is_pressed: boolean
    velocity: [number, number]
    last_t?: number
}

export async function main(
    canvas: HTMLCanvasElement,
    params: WebGPUParams
): Promise<() => void> {
    // Get WebGPU access: start
    if (!("gpu" in navigator)) {
        throw new Error("WebGPU is not supported in this browser.")
    }

    const adapter = await navigator.gpu.requestAdapter()
    if (!adapter) {
        throw new Error("Failed to get GPU adapter.")
    }

    const device = await adapter.requestDevice()
    if (!device) {
        throw new Error("Failed to get GPU device.")
    }

    // Hardcode canvas format for simplicity
    const context = canvas.getContext("webgpu") as GPUCanvasContext | null
    if (!context) {
        throw new Error("Failed to get WebGPU canvas context.")
    }

    const format = navigator.gpu.getPreferredCanvasFormat()
    if (!format) {
        throw new Error("Failed to get preferred canvas format.")
    }

    context.configure({
        device,
        format,
        alphaMode: "premultiplied"
    })
    // Get WebGPU access: end

    // Create uniform buffer
    const uniformBuffers = InitUniforms(device)
    if (!uniformBuffers) {
        throw new Error("Failed to create uniform buffer.")
    }

    // Create simulation buffers (velocity, etc.)
    const buffers = InitSimBuffers(device)
    if (!buffers) {
        throw new Error("Failed to create simulation buffers.")
    }

    // Attach @group(x)
    const bindGroupLayouts = CreateLayouts(device)
    if (!bindGroupLayouts) {
        throw new Error("Failed to create bind group layouts.")
    }

    // Attach @binding(x)
    const bindGroups = CreateBindGroups(
        device,
        bindGroupLayouts,
        uniformBuffers,
        buffers
    )
    if (!bindGroups) {
        throw new Error("Failed to create bind groups.")
    }

    // Create pipeline layout
    const pipelineLayout = device.createPipelineLayout({
        bindGroupLayouts: [bindGroupLayouts.uniformBGL, bindGroupLayouts.simBGL]
    })

    // Create pipelines
    const pipelines = CreatePipelines(device, pipelineLayout, format)
    if (!pipelines) {
        throw new Error("Failed to create pipelines.")
    }

    // Render loop
    let ping = 0
    const loop = CreateLoop((t: number) => {
        // Can be easily changed to use other render loop mechanisms
        ping = Render(
            context,
            device,
            pipelines,
            bindGroups,
            uniformBuffers,
            params,
            ping
        )
        // ping ^= 1 // we moved this into Render()
    })
    loop.start()

    return () => {
        loop.stop()
        // add more cleanup (buffers, etc.) if needed later
    }
}
