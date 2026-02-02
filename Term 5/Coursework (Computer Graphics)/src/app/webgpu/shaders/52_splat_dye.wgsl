// External force
//    dye_in -> dye_out with splatting a circle of dye where the mouse is
// 11_splat_dye.wgsl
// Adds dye to the dye field based on mouse input

@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = gid.x;
  let y = gid.y;
  if (!in_bounds(x,y)) { return; }
  let i = idx(x,y);

  // pass-through velocity unchanged
  vel_out[i] = vel_in[i];

  // keep previous dye with dissipation
  var d = dye_in[i] * sim.dissipation;

  // mouse in cell coords
  let N = sim.N;
  let mx = clamp(mouse.pos.x, 0.0, 0.999999) * N;
  let my = clamp(mouse.pos.y, 0.0, 0.999999) * N;

  let cx = f32(x) + 0.5; // cell center
  let cy = f32(y) + 0.5; // cell center
  let dx = cx - mx;  // distance to mouse
  let dy = cy - my;  // distance to mouse

  let r = 10.0; // radius in cells
  let dist2 = dx*dx + dy*dy; // 

  if (dist2 < r*r) {
    let w = 1.0 - dist2 / (r*r);
    d = max(d, w);          // paint dye
  }

  // // faucet at top-middle
  // let fx = 0.5 * sim.N;
  // let fy = 0.85 * sim.N;
  // let fdx = cx - fx;
  // let fdy = cy - fy;
  // let fr = 3.5;
  // if (fdx*fdx + fdy*fdy < fr*fr) {
  //   d = 1.0;
  // }

  dye_out[i] = d; // write updated dye
}
