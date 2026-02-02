// Advection

// 42_advect_dye.wgsl
//      vel_in + dye_in -> dye_out

// easy
fn sample_dye_nearest(px: f32, py: f32) -> f32 {
  let N = f32(N_u32());
  let x = u32(clamp(px, 0.0, N - 1.0));
  let y = u32(clamp(py, 0.0, N - 1.0));
  return dye_in[idx(x,y)];
}

// harder
fn sample_dye_bilinear(px: f32, py: f32) -> f32 {
  let N = f32(N_u32());

  // clamp to valid range of cell centers (0..N-1 in index space)
  let x = clamp(px, 0.0, N - 1.001);
  let y = clamp(py, 0.0, N - 1.001);

  let x0 = u32(floor(x));
  let y0 = u32(floor(y));
  let x1 = min(x0 + 1u, N_u32() - 1u);
  let y1 = min(y0 + 1u, N_u32() - 1u);

  let sx = x - floor(x);
  let sy = y - floor(y);

  let d00 = dye_in[idx(x0, y0)];
  let d10 = dye_in[idx(x1, y0)];
  let d01 = dye_in[idx(x0, y1)];
  let d11 = dye_in[idx(x1, y1)];

  let dx0 = mix(d00, d10, sx);
  let dx1 = mix(d01, d11, sx);
  return mix(dx0, dx1, sy);
}

@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = gid.x;
  let y = gid.y;
  if (!in_bounds(x,y)) { return; }
  let i = idx(x,y);

  // pass-through velocity unchanged
  vel_out[i] = vel_in[i];
  // pass through pressure so pinging is safe
  p_out[i] = p_in[i];

  let cx = f32(x) + 0.5;
  let cy = f32(y) + 0.5;

  var v = vel_in[i];
  // let maxSpeed = 60.0;
  // let sp = length(v);
  // if (sp > maxSpeed) { v = v * (maxSpeed / sp); }

  let Nf = f32(N_u32());
  let px = clamp(cx - sim.delta_t * v.x, 0.5, Nf - 0.5);
  let py = clamp(cy - sim.delta_t * v.y, 0.5, Nf - 0.5);

  let adv = sample_dye_bilinear(px - 0.5, py - 0.5);
  let old = dye_in[i];

  // more like smoke, less like paint
  // dye_out[i] = mix(old, adv, 0.98) * sim.dissipation;
  //   dye_out[i] = adv;   // no mixing
  dye_out[i] = mix(old, adv, sim.dissipation); 
  // dye_out[i] = adv * sim.dissipation; // full replacement
}
