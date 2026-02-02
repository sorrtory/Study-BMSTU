// Diffuse velocity — Jacobi iteration
// vel_in  = current iterate
// vel_out = next iterate

fn vel_at(x: i32, y: i32) -> vec2<f32> {
  let N = i32(N_u32());
  let xi = clamp(x, 0, N - 1);
  let yi = clamp(y, 0, N - 1);
  return vel_in[idx(u32(xi), u32(yi))];
}

@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = gid.x;
  let y = gid.y;
  if (!in_bounds(x,y)) { return; }

  let i = idx(x,y);

  let Nf = f32(N_u32());
  let dx = 1.0 / Nf;
  let a  = sim.viscosity * sim.delta_t / (dx * dx);

  let vC = vel_in[i];
  let vL = vel_at(i32(x)-1, i32(y));
  let vR = vel_at(i32(x)+1, i32(y));
  let vB = vel_at(i32(x),   i32(y)-1);
  let vT = vel_at(i32(x),   i32(y)+1);

  vel_out[i] = (vC + a * (vL + vR + vB + vT)) / (1.0 + 4.0 * a);
}
