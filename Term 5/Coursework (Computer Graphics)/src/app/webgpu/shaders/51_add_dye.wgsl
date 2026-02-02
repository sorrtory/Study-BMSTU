// External dye
// 10_add_dye.wgsl
//    dye_in -> dye_out  AND  vel_in -> vel_out
// continuous emitter in the center

@compute @workgroup_size(16,16,1)
fn cs_main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let x = gid.x;
  let y = gid.y;
  if (!in_bounds(x,y)) { return; }
  let i = idx(x,y);

  // default pass-through + dissipation
  var d = dye_in[i] * sim.dissipation;
  var v = vel_in[i] * 0.999; // mild damping

  // center in cell coords
  let Nf = f32(N_u32());
  let cx = (f32(x) + 0.5) - 0.5 * Nf;
  let cy = (f32(y) + 0.5) - 0.5 * Nf;

  // emitter radius (cells)
  let r = 20.0;
  let r2 = r * r;
  let dist2 = cx*cx + cy*cy;

  if (dist2 < r2) {
    // smooth weight 1 at center -> 0 at edge
    let w = 1.0 - dist2 / r2;

    // dye injection
    d = 1.0;

    // jet direction (pick one)
    // upward jet:
    let dir = vec2<f32>(1.0, 0.5);

    // jet strength in cells/sec (tune 10..200)
    let jet = sim.faucet_dye;
    
    // inject momentum; scale by dt so it is frame-rate independent
    v += dir * (jet * w) * sim.delta_t;
  }

  dye_out[i] = d;
  vel_out[i] = v;
}
