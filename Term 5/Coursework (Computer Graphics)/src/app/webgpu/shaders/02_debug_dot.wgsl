@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = gid.x;
  let y = gid.y;
  if (!in_bounds(x,y)) { return; }
  let i = idx(x,y);

  // pass-through dye
  dye_out[i] = dye_in[i];
  
  // pass-through velocity
  vel_out[i] = vel_in[i];

  // pass-through pressure
  p_out[i] = p_in[i];

  // set center cell
  let mid = N_u32() / 2u;
  if (x == mid && y == mid) {
    dye_out[i] = 1.0;
  }

  // // Set border
  // if (x == 0u || y == 0u || x == N_u32() - 1u || y == N_u32() - 1u) {
  //   dye_out[i] = 1.0;
  // }
}
