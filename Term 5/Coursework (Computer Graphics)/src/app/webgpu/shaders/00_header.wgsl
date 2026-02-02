// 00_header.wgsl

struct SimUniforms {
  delta_t: f32,
  viscosity: f32,
  diffusion: f32,
  dissipation: f32,

  N: f32,        // assume square grid N x N
  vorticity: f32,
  gravity: f32,
  faucet_dye: f32,
};

@group(0) @binding(0) var<uniform> sim: SimUniforms;

struct Mouse {
  pos: vec2<f32>,
  vel: vec2<f32>,
};
@group(0) @binding(1) var<uniform> mouse: Mouse;

// --------------------
// Sim buffers (SoA)
// --------------------

// Velocity ping-pong
@group(1) @binding(0) var<storage, read>  vel_in  : array<vec2<f32>>;
@group(1) @binding(1) var<storage, read_write> vel_out : array<vec2<f32>>;

// Dye ping-pong (optional but recommended for visualization)
@group(1) @binding(2) var<storage, read>  dye_in  : array<f32>;
@group(1) @binding(3) var<storage, read_write> dye_out : array<f32>;

// Projection buffers
@group(1) @binding(4) var<storage, read_write> divergence : array<f32>;
@group(1) @binding(5) var<storage, read>  p_in  : array<f32>;
@group(1) @binding(6) var<storage, read_write> p_out : array<f32>;

// Helpers
fn N_u32() -> u32 { return u32(sim.N); }

fn idx(x: u32, y: u32) -> u32 { return y * N_u32() + x; }
fn in_bounds(x: u32, y: u32) -> bool { return x < N_u32() && y < N_u32(); }

fn clamp_cell(x: f32) -> f32 {
  return clamp(x, 0.0, sim.N - 1.001);
}

// https://en.wikipedia.org/wiki/Bilinear_interpolation
fn sample_vel_bilinear(px: f32, py: f32) -> vec2<f32> {
  let x = clamp(px, 0.0, sim.N - 1.001);
  let y = clamp(py, 0.0, sim.N - 1.001);

  let x0 = u32(floor(x));
  let y0 = u32(floor(y));
  let x1 = min(x0 + 1u, N_u32() - 1u);
  let y1 = min(y0 + 1u, N_u32() - 1u);

  let sx = x - floor(x);
  let sy = y - floor(y);

  let v00 = vel_in[idx(x0, y0)];
  let v10 = vel_in[idx(x1, y0)];
  let v01 = vel_in[idx(x0, y1)];
  let v11 = vel_in[idx(x1, y1)];

  let vx0 = mix(v00, v10, sx);
  let vx1 = mix(v01, v11, sx);
  return mix(vx0, vx1, sy);
}
