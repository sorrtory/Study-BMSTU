// Projection

// 32_pressure.wgsl
//  divergence + p_in -> p_out (one Jacobi iteration)

fn p_at(x: i32, y: i32) -> f32 {
  let N = i32(N_u32());
  let xi = clamp(x, 0, N - 1);
  let yi = clamp(y, 0, N - 1);
  return p_in[idx(u32(xi), u32(yi))];
}

@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = i32(gid.x);
  let y = i32(gid.y);
  if (x < 0 || y < 0 || x >= i32(N_u32()) || y >= i32(N_u32())) { return; }

  let i = idx(u32(x), u32(y));

  // pass-through vel/dye so pinging pressure iterations doesn't scramble them
  vel_out[i] = vel_in[i];
  dye_out[i] = dye_in[i];

  let pl = p_at(x - 1, y);
  let pr = p_at(x + 1, y);
  let pb = p_at(x, y - 1);
  let pt = p_at(x, y + 1);

  let div = divergence[i];

  p_out[i] = (pl + pr + pb + pt - div) * 0.25;
}
