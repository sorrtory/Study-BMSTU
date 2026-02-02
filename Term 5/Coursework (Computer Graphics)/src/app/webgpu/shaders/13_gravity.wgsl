// External force: gravity downward
// 14_gravity.wgsl
//    vel_in -> vel_out (adds gravity), dye passthrough

@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = gid.x; let y = gid.y;
  if (!in_bounds(x,y)) { return; }
  let i = idx(x,y);

  // passthrough dye
  dye_out[i] = dye_in[i];

  var v = vel_in[i];
  let g = sim.gravity; // (cells/sec^2)
  v.y += g * sim.delta_t;

  vel_out[i] = v;
}
