// Advection

// 41_advect_vel.wgsl
//      vel_in -> vel_out (semi-Lagrangian)

@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = gid.x;
  let y = gid.y;
  if (!in_bounds(x,y)) { return; }
  let i = idx(x,y);

  // pass-through dye unchanged
  dye_out[i] = dye_in[i];

  // pass through pressure so pinging is safe
  p_out[i] = p_in[i];


  // Center of cell
  let cx = f32(x) + 0.5;
  let cy = f32(y) + 0.5;

  let v = vel_in[i];

  // backtrace in cell coordinates, clamp to domain
  let px = clamp(cx - sim.delta_t * v.x, 0.5, sim.N - 0.5);
  let py = clamp(cy - sim.delta_t * v.y, 0.5, sim.N - 0.5);

  // sample velocity at backtraced position (convert to index coords)
  let vnew = sample_vel_bilinear(px - 0.5, py - 0.5);
  vel_out[i] = vnew * 0.99; // optional mild damping
}
