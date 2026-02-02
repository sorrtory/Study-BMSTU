// Projection
// 31_diverge.wgsl
//      vel_in -> divergence
// No ping needed

fn vel_at(x: i32, y: i32) -> vec2<f32> {
  let N = i32(N_u32());
  let xi = clamp(x, 0, N - 1);
  let yi = clamp(y, 0, N - 1);
  return vel_in[idx(u32(xi), u32(yi))];
}

@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = i32(gid.x);
  let y = i32(gid.y);
  if (x < 0 || y < 0 || x >= i32(N_u32()) || y >= i32(N_u32())) { return; }

  let i = idx(u32(x), u32(y));

  // pass-through (so ping flips won't destroy state)
  vel_out[i] = vel_in[i];
  dye_out[i] = dye_in[i];
  p_out[i]   = p_in[i];

  let vl = vel_at(x - 1, y);
  let vr = vel_at(x + 1, y);
  let vb = vel_at(x, y - 1);
  let vt = vel_at(x, y + 1);

  // dx = dy = 1 cell
  // divergence = du/dx + dv/dy
  let div = 0.5 * ((vr.x - vl.x) + (vt.y - vb.y));
  
  divergence[i] = div;
}
