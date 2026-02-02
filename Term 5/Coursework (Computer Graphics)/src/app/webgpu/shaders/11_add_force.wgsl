// External force
//   vel_in -> vel_out with added force where the mouse is
// 12_add_force.wgsl
// Adds force to velocity field based on mouse input

@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = gid.x;
  let y = gid.y;
  if (!in_bounds(x,y)) { return; }
  let i = idx(x,y);

  // pass-through dye unchanged
  dye_out[i] = dye_in[i];

  var v = vel_in[i];

  let N = f32(N_u32());
  let mx = clamp(mouse.pos.x, 0.0, 0.999999) * N;
  let my = clamp(mouse.pos.y, 0.0, 0.999999) * N;

  let cx = f32(x) + 0.5;
  let cy = f32(y) + 0.5;
  let dx = cx - mx;
  let dy = cy - my;

  let r = 6.0;
  let dist2 = dx*dx + dy*dy;

  if (dist2 < r*r) {
    let w = 1.0 - dist2 / (r*r);

    // mouse.vel is in normalized units per frame; scale it up
    // Convert normalized -> cells and apply gain
    let gain = 1.0; // tune
    let impulse = mouse.vel * gain * w;

    v += impulse;
  }

  // slight damping so it doesn't explode
  v *= 0.99;

  vel_out[i] = v;
}
