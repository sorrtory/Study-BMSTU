"use client"

import { useEffect, useRef } from "react"
import { main, type WebGPUParams } from "../webgpu/main"
import { setupMouseListener } from "../webgpu/common"

export default function WebGPUCanvas({
  params,
  width,
  height
}: {
  params: WebGPUParams
  width: number
  height: number
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  if (!canvasRef) {
    throw new Error("Canvas ref is null")
  }

  // Run WebGPU main function once the component is mounted
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    setupMouseListener(canvas, params.mouse)

    // This will hold the cleanup function returned by main()
    let cleanup: (() => void) | undefined

    main(canvas, params)
      .then((c) => {
        // Store the cleanup function for later
        cleanup = c
      })
      .catch((err) => {
        console.error(err)
        if (canvasRef.current) {
          canvasRef.current.className = "outline outline-8 outline-red-500"
          const gui = document.querySelector(".lil-gui")
          if (gui) {
            gui.remove()
          }

          const parent = canvasRef.current.parentElement!
          parent.style.display = "flex"
          parent.style.flexDirection = "column"
          parent.style.alignItems = "center"
          parent.style.justifyContent = "center"
          parent.innerText = `WebGPU is not supported or failed to initialize.`

          const link_to_github = document.createElement(
            "a"
          ) as HTMLAnchorElement
          link_to_github.href =
            "https://github.com/sorrtory-vercel/stable-fluids-webgpu?tab=readme-ov-file#%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0-%D0%B1%D1%80%D0%B0%D1%83%D0%B7%D0%B5%D1%80%D0%B0"
          link_to_github.innerText = "Check the GitHub README for more info."
          link_to_github.style.display = "block"
          link_to_github.style.marginTop = "16px"
          link_to_github.target = "_blank"
          link_to_github.rel = "noopener noreferrer"

          parent.appendChild(link_to_github)
        }
      })

    return () => {
      if (cleanup) cleanup()
    }
  }, []) // only initialize WebGPU once

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="outline outline-8 outline-blue-100"
    />
  )
}
