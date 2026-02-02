import headerWGSL from "./shaders/00_header.wgsl"
import renderWGSL from "./shaders/01_render.wgsl"
import debugDotWGSL from "./shaders/02_debug_dot.wgsl"
import addForceWGSL from "./shaders/11_add_force.wgsl"
import vortexForceWGSL from "./shaders/12_vortex_force.wgsl"
import gravityWGSL from "./shaders/13_gravity.wgsl"
import advectVelWGSL from "./shaders/21_advect_vel.wgsl"
import viscosityWGSL from "./shaders/31_viscosity.wgsl"
import clearPressureWGSL from "./shaders/41_clear_pressure.wgsl"
import divergeWGSL from "./shaders/42_divergence.wgsl"
import pressureWGSL from "./shaders/43_pressure_jacobi.wgsl"
import gradientWGSL from "./shaders/44_subtract_gradient.wgsl"
import addDyeWGSL from "./shaders/51_add_dye.wgsl"
import splatWGSL from "./shaders/52_splat_dye.wgsl"
import advectDyeWGSL from "./shaders/53_advect_dye.wgsl"

// ###################
// # Data structures #
// ###################

export class Vec {
    x: number
    y: number

    constructor(x: number, y: number) {
        this.x = x
        this.y = y
    }
}

// #############
// # Constants #
// #############

// Follow Stam's "Stable Fluids" paper. Chapter 3: Our solver
// https://pages.cs.wisc.edu/~chaol/data/cs777/stam-stable_fluids.pdf

export const NDIM = 2 // number of dimensions

export const ORIGIN: Vec = new Vec(0, 0) // O: origin coords of the domain
export const LENGTH: Vec = new Vec(750, 750) // L: physical size of the domain
export const N = 250
export const N_CELLS: Vec = new Vec(N, N) // N: number of cells in each dimension
export const CELL_SIZE: Vec = new Vec(
    LENGTH.x / N_CELLS.x,
    LENGTH.y / N_CELLS.y
) // D: cell size, we assume a uniform grid

// Dynamic simulation parameters (tuned for visually pleasing, stable behavior)
// Notes:
//  - DELTA_T: timestep in seconds (~1/60 for smooth animation)
//  - VISCOSITY: larger -> smoother/slower motion (typical 1e-6 ... 1e-2). 5e-4 is a good middle-ground.
//  - DIFFUSION: dye diffusion (typical 1e-8 ... 1e-3). Keep small to preserve sharp color, e.g. 1e-5.
//  - DISSIPATION: dye fade factor per step (0..1). Slightly <1 fades dye slowly.
//  - VORTEX_STRENGTH: strength of the vortex force in the center. Tune to get more or less swirling motion.
//  - GRAVITY: strength of the downward gravity force.
//  - FAUCET_DYE: amount of dye added by the faucet each step.
export const DELTA_T = 1.0 / 60.0 // ~0.0166667
export const VISCOSITY = 0.005
export const DIFFUSION = 0.98 // unused
export const DISSIPATION = 0.999
export const VORTEX_STRENGTH = 25.0 // strength of the vortex force in the center
export const GRAVITY = -20.0 // gravity force strength (added to velocity.y each step)
export const FAUCET_DYE = 200.0 // amount of dye added by the blob each step

//  - PRESSURE_ITERATIONS: more iterations -> more accurate incompressibility, but slower. 20 is a good trade-off.
//  - VISCOSITY_ITERATIONS: more iterations -> more accurate viscosity solve, but slower. 10 is usually sufficient.
export const PRESSURE_ITERATIONS = 20 // number of Jacobi iterations to solve for pressure
export const VISCOSITY_ITERATIONS = 10 // number of Jacobi iterations for viscosity solve

// Other constants
export const WORKGROUP_SIZE = 16 // compute shader workgroup size (16x16=256 threads)
export const MAX_SPEED = 10 // max mouse speed in cells/sec (used for TS mouse input clamping)

// ########################
// # Uniforms init helper #
// ########################

// https://webgpufundamentals.org/webgpu/lessons/webgpu-uniforms.html

export type InitUniformsResult = {
    uniformBuffer: GPUBuffer
    mouseBuffer: GPUBuffer
}

export function InitUniforms(device: GPUDevice): InitUniformsResult {
    // struct Uniforms. See 00_header.wgsl
    const uniformBufferSize = 4 * 4 + 4 * 4 + 4 * 4
    const uniformBuffer = device.createBuffer({
        size: uniformBufferSize,
        usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST
    })

    // struct Mouse
    const mouseBufferSize = 4 * 4 // pos: vec2<f32> + vel: vec2<f32> -> 4 floats total = 16 bytes
    const mouseBuffer = device.createBuffer({
        size: mouseBufferSize,
        usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST
    })

    return {
        uniformBuffer,
        mouseBuffer
    }
}

// ######################
// # Buffer init helper #
// ######################

export type InitSimBuffersResult = {
    vel0: GPUBuffer // ping-pong velocity buffers
    vel1: GPUBuffer
    dye0: GPUBuffer // ping-pong dye (scalar) buffers
    dye1: GPUBuffer
    p0: GPUBuffer // ping-pong pressure buffers
    p1: GPUBuffer
    div: GPUBuffer // divergence buffer
}

export function InitSimBuffers(device: GPUDevice): InitSimBuffersResult {
    // To reprsent a vector field we use Marker And Cell (MAC) collocated (not staggered) grid.
    // The vector is defined at the center of each cell

    const cellCount = N_CELLS.x * N_CELLS.y

    const velBytes = cellCount * 2 * 4 // vec2<f32>
    const scalarBytes = cellCount * 4 // f32

    const common =
        GPUBufferUsage.STORAGE |
        GPUBufferUsage.COPY_SRC |
        GPUBufferUsage.COPY_DST

    const vel0 = device.createBuffer({
        label: "vel0",
        size: velBytes,
        usage: common
    })
    const vel1 = device.createBuffer({
        label: "vel1",
        size: velBytes,
        usage: common
    })

    const dye0 = device.createBuffer({
        label: "dye0",
        size: scalarBytes,
        usage: common
    })
    const dye1 = device.createBuffer({
        label: "dye1",
        size: scalarBytes,
        usage: common
    })

    const div = device.createBuffer({
        label: "div",
        size: scalarBytes,
        usage: common
    })

    const p0 = device.createBuffer({
        label: "p0",
        size: scalarBytes,
        usage: common
    })
    const p1 = device.createBuffer({
        label: "p1",
        size: scalarBytes,
        usage: common
    })

    // Optional: clear them to zero once (WebGPU buffers are not guaranteed to be zeroed)
    device.queue.writeBuffer(vel0, 0, new Float32Array(cellCount * 2))
    device.queue.writeBuffer(vel1, 0, new Float32Array(cellCount * 2))
    device.queue.writeBuffer(dye0, 0, new Float32Array(cellCount))
    device.queue.writeBuffer(dye1, 0, new Float32Array(cellCount))
    device.queue.writeBuffer(div, 0, new Float32Array(cellCount))
    device.queue.writeBuffer(p0, 0, new Float32Array(cellCount))
    device.queue.writeBuffer(p1, 0, new Float32Array(cellCount))

    return { vel0, vel1, dye0, dye1, div, p0, p1 }
}

// #######################
// # Bind group layouts  #
// #######################

export type BindGroupLayoutsResult = {
    uniformBGL: GPUBindGroupLayout
    simBGL: GPUBindGroupLayout
}

export function CreateLayouts(device: GPUDevice): BindGroupLayoutsResult {
    // group(0): uniforms (used by compute and/or render)
    const uniformBGL = device.createBindGroupLayout({
        label: "BGL uniforms",
        entries: [
            // struct Uniforms
            {
                binding: 0,
                visibility:
                    GPUShaderStage.COMPUTE |
                    GPUShaderStage.VERTEX |
                    GPUShaderStage.FRAGMENT,
                buffer: { type: "uniform" }
            },
            // struct Mouse
            {
                binding: 1,
                visibility:
                    GPUShaderStage.COMPUTE |
                    GPUShaderStage.VERTEX |
                    GPUShaderStage.FRAGMENT,
                buffer: { type: "uniform" }
            }
        ]
    })

    // group(1): sim buffers (ping-pong)
    const simBGL = device.createBindGroupLayout({
        label: "BGL sim SoA",
        entries: [
            {
                binding: 0,
                visibility: GPUShaderStage.COMPUTE | GPUShaderStage.FRAGMENT,
                buffer: { type: "read-only-storage" }
            }, // vel_in
            {
                binding: 1,
                visibility: GPUShaderStage.COMPUTE | GPUShaderStage.FRAGMENT,
                buffer: { type: "storage" }
            }, // vel_out

            {
                binding: 2,
                visibility: GPUShaderStage.COMPUTE | GPUShaderStage.FRAGMENT,
                buffer: { type: "read-only-storage" }
            }, // dye_in
            {
                binding: 3,
                visibility: GPUShaderStage.COMPUTE | GPUShaderStage.FRAGMENT,
                buffer: { type: "storage" }
            }, // dye_out

            {
                binding: 4,
                visibility: GPUShaderStage.COMPUTE,
                buffer: { type: "storage" }
            }, // divergence (written in compute)
            {
                binding: 5,
                visibility: GPUShaderStage.COMPUTE | GPUShaderStage.FRAGMENT,
                buffer: { type: "read-only-storage" }
            }, // p_in
            {
                binding: 6,
                visibility: GPUShaderStage.COMPUTE | GPUShaderStage.FRAGMENT,
                buffer: { type: "storage" }
            } // p_out
        ]
    })
    return { uniformBGL, simBGL }
}

// ###############
// # Bind groups #
// ###############

export type BindGroupsResult = {
    uniformBG: GPUBindGroup
    simBG: readonly [GPUBindGroup, GPUBindGroup]
}

export function CreateBindGroups(
    device: GPUDevice,
    layouts: { uniformBGL: GPUBindGroupLayout; simBGL: GPUBindGroupLayout },
    uniformBuffers: InitUniformsResult,
    simBuffers: InitSimBuffersResult
): BindGroupsResult {
    const uniformBG = device.createBindGroup({
        label: "BG uniforms",
        layout: layouts.uniformBGL,
        entries: [
            // struct Uniforms
            { binding: 0, resource: { buffer: uniformBuffers.uniformBuffer } },
            // struct Mouse
            { binding: 1, resource: { buffer: uniformBuffers.mouseBuffer } }
        ]
    })

    // ping=0: in=0 out=1
    const simBG0 = device.createBindGroup({
        label: "BG sim ping0",
        layout: layouts.simBGL,
        entries: [
            { binding: 0, resource: { buffer: simBuffers.vel0 } },
            { binding: 1, resource: { buffer: simBuffers.vel1 } },

            { binding: 2, resource: { buffer: simBuffers.dye0 } },
            { binding: 3, resource: { buffer: simBuffers.dye1 } },

            { binding: 4, resource: { buffer: simBuffers.div } },

            { binding: 5, resource: { buffer: simBuffers.p0 } },
            { binding: 6, resource: { buffer: simBuffers.p1 } }
        ]
    })

    // ping=1: in=1 out=0
    const simBG1 = device.createBindGroup({
        label: "BG sim ping1",
        layout: layouts.simBGL,
        entries: [
            { binding: 0, resource: { buffer: simBuffers.vel1 } },
            { binding: 1, resource: { buffer: simBuffers.vel0 } },

            { binding: 2, resource: { buffer: simBuffers.dye1 } },
            { binding: 3, resource: { buffer: simBuffers.dye0 } },

            { binding: 4, resource: { buffer: simBuffers.div } },

            { binding: 5, resource: { buffer: simBuffers.p1 } },
            { binding: 6, resource: { buffer: simBuffers.p0 } }
        ]
    })

    return { uniformBG, simBG: [simBG0, simBG1] as const }
}

// ##############
// # Pipelines  #
// ##############

export type PipelinesResult = {
    // 01: render - vertex/fragment pipeline to render dye to the screen
    renderPipeline: GPURenderPipeline
    // 02: debug dot - small utility compute shader for debugging / probes
    debugDotPipeline: GPUComputePipeline
    // 11: add force - inject momentum (velocity) into the velocity field
    addForcePipeline: GPUComputePipeline
    // 12: vortex force - add swirling vortex force in center
    vortexForcePipeline: GPUComputePipeline
    // 13: gravity - add downward gravity force
    gravityPipeline: GPUComputePipeline
    // 21: advect velocity - advect velocity field (semi-Lagrangian)
    advectVelPipeline: GPUComputePipeline
    // 31: viscosity - apply viscosity (diffusion) step to velocity
    viscosityPipeline: GPUComputePipeline
    // 41: clear pressure - clear pressure field to zero before pressure solve
    clearPressurePipeline: GPUComputePipeline
    // 42: diverge - compute divergence of the velocity field into div buffer
    divergePipeline: GPUComputePipeline
    // 43: pressure - Jacobi iterations to solve Poisson equation for pressure
    pressurePipeline: GPUComputePipeline
    // 44: gradient - subtract pressure gradient from velocity to enforce incompressibility
    gradientPipeline: GPUComputePipeline
    // 51: add dye - add faucet dye into simulation at a position
    addDyePipeline: GPUComputePipeline
    // 52: splat dye - add dye (scalar) into simulation at a position
    splatPipeline: GPUComputePipeline
    // 53: advect dye - advect scalar dye with the velocity field
    advectDyePipeline: GPUComputePipeline
}

export function CreatePipelines(
    device: GPUDevice,
    pipelineLayout: GPUPipelineLayout,
    format: GPUTextureFormat
): PipelinesResult {
    // 01_render: render pipeline to draw dye to a swapchain texture
    const renderShaderModule = device.createShaderModule({
        label: "01_render",
        code: headerWGSL + renderWGSL
    })

    const renderPipeline = device.createRenderPipeline({
        layout: pipelineLayout,
        vertex: {
            module: renderShaderModule,
            entryPoint: "vs_main"
        },
        fragment: {
            module: renderShaderModule,
            entryPoint: "fs_main",
            // fs_main
            // fs_dye_simple
            // fs_dye_with_foam
            // fs_velocity_magnitude
            // fs_pressure
            // fs_dye_plus_velocity
            targets: [{ format }]
        },
        primitive: {
            topology: "triangle-list"
        }
    })

    // 02_debug_dot: small debugging/probe compute shader
    const debugDotModule = device.createShaderModule({
        label: "02_debug_dot",
        code: headerWGSL + debugDotWGSL
    })
    const debugDotPipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: debugDotModule, entryPoint: "cs_main" }
    })

    // 11_add_force: inject force/momentum into velocity buffer
    const addForceModule = device.createShaderModule({
        label: "11_add_force",
        code: headerWGSL + addForceWGSL
    })
    const addForcePipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: addForceModule, entryPoint: "cs_main" }
    })

    // 12_vortex_force: add swirling vortex force in center
    const vortexForceModule = device.createShaderModule({
        label: "12_vortex_force",
        code: headerWGSL + vortexForceWGSL
    })
    const vortexForcePipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: vortexForceModule, entryPoint: "cs_main" }
    })

    // 13_gravity: add downward gravity force
    const gravityModule = device.createShaderModule({
        label: "13_gravity",
        code: headerWGSL + gravityWGSL
    })
    const gravityPipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: gravityModule, entryPoint: "cs_main" }
    })

    // 21_advect_vel: advect velocity field (semi-Lagrangian)
    const advectVelModule = device.createShaderModule({
        label: "21_advect_vel",
        code: headerWGSL + advectVelWGSL
    })
    const advectVelPipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: advectVelModule, entryPoint: "cs_main" }
    })

    // 31_viscosity: apply viscosity (diffusion) step to velocity
    const viscosityModule = device.createShaderModule({
        label: "31_viscosity",
        code: headerWGSL + viscosityWGSL
    })
    const viscosityPipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: viscosityModule, entryPoint: "cs_main" }
    })

    // 41_clear_pressure: clear pressure field to zero before pressure solve
    const clearPressureModule = device.createShaderModule({
        label: "41_clear_pressure",
        code: headerWGSL + clearPressureWGSL
    })
    const clearPressurePipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: clearPressureModule, entryPoint: "cs_main" }
    })

    // 42_divergence: compute divergence of the velocity field into div buffer
    const divergeModule = device.createShaderModule({
        label: "42_divergence",
        code: headerWGSL + divergeWGSL
    })
    const divergePipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: divergeModule, entryPoint: "cs_main" }
    })

    // 43_pressure_jacobi: Jacobi pressure solve step (iterative Poisson solve)
    const pressureModule = device.createShaderModule({
        label: "43_pressure_jacobi",
        code: headerWGSL + pressureWGSL
    })
    const pressurePipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: pressureModule, entryPoint: "cs_main" }
    })

    // 44_subtract_gradient: subtract pressure gradient from velocity to enforce incompressibility
    const gradientModule = device.createShaderModule({
        label: "44_subtract_gradient",
        code: headerWGSL + gradientWGSL
    })
    const gradientPipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: gradientModule, entryPoint: "cs_main" }
    })

    // 51_add_dye: add faucet dye into scalar dye buffer
    const addDyeModule = device.createShaderModule({
        label: "51_add_dye",
        code: headerWGSL + addDyeWGSL
    })
    const addDyePipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: addDyeModule, entryPoint: "cs_main" }
    })

    // 52_splat_dye: add dye blob into scalar dye buffer
    const splatModule = device.createShaderModule({
        label: "52_splat_dye",
        code: headerWGSL + splatWGSL
    })
    const splatPipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: splatModule, entryPoint: "cs_main" }
    })

    // 53_advect_dye: advect scalar dye with the velocity field
    const advectDyeModule = device.createShaderModule({
        label: "53_advect_dye",
        code: headerWGSL + advectDyeWGSL
    })
    const advectDyePipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: { module: advectDyeModule, entryPoint: "cs_main" }
    })

    const pipelines: PipelinesResult = {
        // 0
        renderPipeline: renderPipeline,
        debugDotPipeline: debugDotPipeline,
        // 1
        addForcePipeline: addForcePipeline,
        vortexForcePipeline: vortexForcePipeline,
        gravityPipeline: gravityPipeline,
        // 2
        advectVelPipeline: advectVelPipeline,
        // 3
        viscosityPipeline: viscosityPipeline,
        // 4
        clearPressurePipeline: clearPressurePipeline,
        divergePipeline: divergePipeline,
        pressurePipeline: pressurePipeline,
        gradientPipeline: gradientPipeline,
        // 5
        addDyePipeline: addDyePipeline,
        splatPipeline: splatPipeline,
        advectDyePipeline: advectDyePipeline
    }

    return pipelines
}
