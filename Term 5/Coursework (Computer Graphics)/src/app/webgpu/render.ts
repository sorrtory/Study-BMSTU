import {
    BindGroupsResult,
    InitUniformsResult,
    N_CELLS,
    PipelinesResult,
    PRESSURE_ITERATIONS,
    VISCOSITY_ITERATIONS,
    WORKGROUP_SIZE
} from "./init"
import { WebGPUParams } from "./main"

function writeBufferUniforms(
    device: GPUDevice,
    uniformBuffer: GPUBuffer,
    params: WebGPUParams
) {
    // See 00_header.wgsl for struct layout
    // and init.ts:InitUniforms for buffer size

    // Each buffer in WGSL must be aligned to 16 bytes
    // But the stucts may not use all the bytes
    // So we just write the used data at the start of the buffer
    // and leave the rest as padding

    // Check out [uniformBuffer] for the layout
    const data = new Float32Array([
        params.dt,
        params.viscosity,
        params.diffusion,
        params.dissipation,
        N_CELLS.x, //
        params.vorticity,
        params.gravity,
        params.faucet_dye
    ])
    device.queue.writeBuffer(uniformBuffer, 0, data.buffer)
}

function writeBufferMouse(
    device: GPUDevice,
    mouseBuffer: GPUBuffer,
    params: WebGPUParams
) {
    /*
    struct Mouse {
      pos: vec2<f32>,
      vel: vec2<f32>,
    }
    */

    const data = new Float32Array([
        // vec2<f32> + padding
        params.mouse.current_pos[0],
        params.mouse.current_pos[1],
        // vec2<f32> + padding
        params.mouse.velocity[0],
        params.mouse.velocity[1]
    ])
    device.queue.writeBuffer(mouseBuffer, 0, data.buffer)
}

export function Render(
    context: GPUCanvasContext,
    device: GPUDevice,
    pipelines: PipelinesResult,
    bindGroups: BindGroupsResult,
    uniformBuffers: InitUniformsResult,
    params: WebGPUParams,
    ping: number
): number {
    let p = ping

    // 0) Update uniforms
    writeBufferUniforms(device, uniformBuffers.uniformBuffer, params)
    writeBufferMouse(device, uniformBuffers.mouseBuffer, params)

    const encoder = device.createCommandEncoder()

    const wx = Math.ceil(N_CELLS.x / WORKGROUP_SIZE)
    const wy = Math.ceil(N_CELLS.y / WORKGROUP_SIZE)

    const cpass = encoder.beginComputePass()

    // ============================================================
    // Stam velocity step:
    //   w0 --(add force)--> w1 --(advect)--> w2 --(diffuse)--> w3 --(project)--> w4
    // ============================================================

    // ------------------------
    // 1) ADD FORCES  (w0 -> w1)
    // ------------------------
    // 12) add force to velocity
    cpass.setPipeline(pipelines.addForcePipeline)
    cpass.setBindGroup(0, bindGroups.uniformBG)
    cpass.setBindGroup(1, bindGroups.simBG[p])
    cpass.dispatchWorkgroups(wx, wy)
    p ^= 1

    // 13) add vortex force to velocity
    cpass.setPipeline(pipelines.vortexForcePipeline)
    cpass.setBindGroup(1, bindGroups.simBG[p])
    cpass.dispatchWorkgroups(wx, wy)
    p ^= 1

    // 14) add gravity force to velocity
    cpass.setPipeline(pipelines.gravityPipeline)
    cpass.setBindGroup(1, bindGroups.simBG[p])
    cpass.dispatchWorkgroups(wx, wy)
    p ^= 1

    // ------------------------
    // 2) ADVECT VELOCITY (w1 -> w2)
    // ------------------------
    cpass.setPipeline(pipelines.advectVelPipeline)
    cpass.setBindGroup(1, bindGroups.simBG[p])
    cpass.dispatchWorkgroups(wx, wy)
    p ^= 1

    // ------------------------
    // 3) DIFFUSE VELOCITY / VISCOSITY (w2 -> w3)
    // ------------------------
    for (let k = 0; k < VISCOSITY_ITERATIONS; k++) {
        cpass.setPipeline(pipelines.viscosityPipeline)
        cpass.setBindGroup(1, bindGroups.simBG[p])
        cpass.dispatchWorkgroups(wx, wy)
        p ^= 1
    }

    // ------------------------
    // 4) PROJECT (w3 -> w4)
    //    Make velocity divergence-free:
    //      - clear pressure
    //      - compute divergence
    //      - pressure solve (Jacobi)
    //      - subtract gradient
    //
    // CRITICAL: You MUST NOT flip `p` inside the pressure solve
    // unless your shaders pass-through vel/dye each iter.
    // However, we DO. Be careful flipping p correctly.
    // ------------------------

    // 30) clear pressure field
    // If this shader writes ONLY pressure/div and does NOT produce a full new sim-state,
    // do NOT flip p.
    cpass.setPipeline(pipelines.clearPressurePipeline)
    cpass.setBindGroup(1, bindGroups.simBG[p])
    cpass.dispatchWorkgroups(wx, wy)
    p ^= 1 // IMPORTANT: now the cleared pressure lives in p_in of the new state

    // 31) divergence (writes div)
    cpass.setPipeline(pipelines.divergePipeline)
    cpass.setBindGroup(1, bindGroups.simBG[p])
    cpass.dispatchWorkgroups(wx, wy)
    // p stays the same

    // 32) pressure solve (Jacobi)
    for (let k = 0; k < PRESSURE_ITERATIONS; k++) {
        cpass.setPipeline(pipelines.pressurePipeline)
        cpass.setBindGroup(1, bindGroups.simBG[p])
        cpass.dispatchWorkgroups(wx, wy)
        p ^= 1 // CRITICAL: swaps p_in/p_out so next iter reads the new pressure
    }

    // 33) subtract gradient (updates velocity using pressure)
    cpass.setPipeline(pipelines.gradientPipeline)
    cpass.setBindGroup(1, bindGroups.simBG[p])
    cpass.dispatchWorkgroups(wx, wy)
    p ^= 1 // this one typically *does* output a new vel_out, so we flip

    // ============================================================
    // Dye step (separate from Stam's velocity flow)
    // ============================================================

    // ------------------------
    // 5) DYE SOURCES (add/splat)
    // ------------------------
    // 10) add dye from faucet
    cpass.setPipeline(pipelines.addDyePipeline)
    cpass.setBindGroup(1, bindGroups.simBG[p])
    cpass.dispatchWorkgroups(wx, wy)
    p ^= 1

    // 11) splat dye
    cpass.setPipeline(pipelines.splatPipeline)
    cpass.setBindGroup(1, bindGroups.simBG[p])
    cpass.dispatchWorkgroups(wx, wy)
    p ^= 1

    // ------------------------
    // 6) ADVECT DYE (using latest projected velocity)
    // ------------------------
    cpass.setPipeline(pipelines.advectDyePipeline)
    cpass.setBindGroup(1, bindGroups.simBG[p])
    cpass.dispatchWorkgroups(wx, wy)
    p ^= 1

    cpass.end()

    // Render
    const view = context.getCurrentTexture().createView()
    const rpass = encoder.beginRenderPass({
        colorAttachments: [
            {
                view,
                loadOp: "clear",
                storeOp: "store",
                clearValue: { r: 0.05, g: 0.05, b: 0.1, a: 1 }
            }
        ]
    })

    rpass.setPipeline(pipelines.renderPipeline)
    rpass.setBindGroup(0, bindGroups.uniformBG)
    rpass.setBindGroup(1, bindGroups.simBG[p])
    rpass.draw(3, 1, 0, 0)
    rpass.end()

    device.queue.submit([encoder.finish()])
    return p
}
