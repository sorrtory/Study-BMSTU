// Projection
// 33_gradient.wgsl
//   vel_in + p_in -> vel_out
// Pressure gradient subtraction

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

  // pass-through dye
  dye_out[i] = dye_in[i];

  // pass through pressure so pinging is safe
  p_out[i] = p_in[i];

  let pl = p_at(x - 1, y);
  let pr = p_at(x + 1, y);
  let pb = p_at(x, y - 1);
  let pt = p_at(x, y + 1);

  // dx = 1 cell
  let grad = 0.5 * vec2<f32>(pr - pl, pt - pb);

  vel_out[i] = vel_in[i] - grad;
}
