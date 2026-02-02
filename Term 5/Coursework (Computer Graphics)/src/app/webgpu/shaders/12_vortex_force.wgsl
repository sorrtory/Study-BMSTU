// External force: vortex swirl in center
// 13_vortex_force.wgsl
//    vel_in -> vel_out (adds swirl), dye passthrough


@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = gid.x;
  let y = gid.y;
  if (!in_bounds(x,y)) { return; }
  let i = idx(x,y);

  dye_out[i] = dye_in[i];

  var v = vel_in[i];

  let cx = (f32(x) + 0.5) - 0.5 * sim.N;
  let cy = (f32(y) + 0.5) - 0.5 * sim.N;

  // swirl direction = perpendicular to radius
  let r2 = cx*cx + cy*cy + 1e-5;
  let r = sqrt(r2);

  // strength decays with distance
  let strength = sim.vorticity;       // tune 5..50
  let falloff = exp(-r2 / (2.0 * 40.0 * 40.0));

  // tangent unit vector
  let tx = -cy / r;
  let ty =  cx / r;

  v += vec2<f32>(tx, ty) * (strength * falloff) * sim.delta_t;

  // mild damping
  v *= 0.999;

  vel_out[i] = v;
}
