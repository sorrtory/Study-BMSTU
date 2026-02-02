import { MAX_SPEED, N_CELLS } from "./init"
import { MouseInfo } from "./main"

// Utility to create a render loop using requestAnimationFrame
export function createLoop(render: (t: number) => void) {
    let rafId: number | null = null

    const frame = (t: number) => {
        render(t)
        rafId = requestAnimationFrame(frame)
    }

    return {
        start() {
            if (rafId != null) return
            rafId = requestAnimationFrame(frame)
        },
        stop() {
            if (rafId == null) return
            cancelAnimationFrame(rafId)
            rafId = null
        },
        get running() {
            return rafId != null
        }
    }
}

function getMouseUV(canvas: HTMLCanvasElement, e: MouseEvent) {
    const rect = canvas.getBoundingClientRect()

    const u = (e.clientX - rect.left) / rect.width
    const v = (e.clientY - rect.top) / rect.height

    // clamp position only
    const clamp01 = (x: number) => Math.min(1, Math.max(0, x))
    return [clamp01(u), clamp01(v)] as const
}

function updateMouse(
    canvas: HTMLCanvasElement,
    mouseInfo: MouseInfo,
    e: MouseEvent
) {
    const now = performance.now()
    const dt = mouseInfo.last_t ? (now - mouseInfo.last_t) / 1000 : 0
    mouseInfo.last_t = now

    const [u, vDown] = getMouseUV(canvas, e)
    const vUp = 1 - vDown

    mouseInfo.prev_pos = [...mouseInfo.current_pos]
    mouseInfo.current_pos = [u, vUp]

    if (dt > 0) {
        // uv/sec
        let vx = (mouseInfo.current_pos[0] - mouseInfo.prev_pos[0]) / dt
        let vy = (mouseInfo.current_pos[1] - mouseInfo.prev_pos[1]) / dt

        // -> cells/sec
        vx *= N_CELLS.x
        vy *= N_CELLS.y

        // clamp
        const maxSpeed = MAX_SPEED // cells/sec
        const sp = Math.hypot(vx, vy)
        if (sp > maxSpeed) {
            const s = maxSpeed / sp
            vx *= s
            vy *= s
        }

        mouseInfo.velocity = [vx, vy]
    } else {
        mouseInfo.velocity = [0, 0]
    }
}

// Mouse onchange listener that updates MouseInfo structure
export function setupMouseListener(
    canvas: HTMLCanvasElement,
    mouseInfo: MouseInfo
) {
    canvas.addEventListener("mousedown", (e) => {
        mouseInfo.is_pressed = true
        // updateMouse(canvas, mouseInfo, e);

        console.log(
            "Mouse down at:",
            mouseInfo.current_pos,
            "with velocity",
            mouseInfo.velocity
        )
    })

    canvas.addEventListener("mouseup", () => {
        mouseInfo.is_pressed = false
        // mouseInfo.velocity = [0, 0]
    })

    canvas.addEventListener("mousemove", (e) => {
        updateMouse(canvas, mouseInfo, e)
    })
}
