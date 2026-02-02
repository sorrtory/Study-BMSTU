// next.config.ts
import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  turbopack: {
    rules: {
      // All *.wgsl files -> run through raw-loader
      "*.wgsl": {
        loaders: ["raw-loader"],
        as: "*.js" // loader output is JS module
      }
    }
  }
}

export default nextConfig
