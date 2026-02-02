// Projection
// 30_clear_pressure.wgsl
//   -> p_out = 0.0
// Clears pressure field to zero before pressure solve
// Then visualization is more stable

@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = gid.x;
  let y = gid.y;
  if (!in_bounds(x,y)) { return; }
  let i = idx(x,y);

  // preserve vel/dye so pinging is safe
  vel_out[i] = vel_in[i];
  dye_out[i] = dye_in[i];

  p_out[i] = 0.0;
}