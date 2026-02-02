// Render
//  dye_in -> screen

struct VSOut {
    @builtin(position) pos: vec4<f32>,
    @location(0) uv: vec2<f32>,
};

/*
vs_main - Vertex shader producing a full-screen triangle and UVs

Parameters:
- @builtin(vertex_index) vi: u32
    The built-in vertex index (0..2) used to select one of three hard-coded 2D positions.

Behavior:
- Emits a single triangle that covers the entire viewport by using three oversized NDC positions:
        (-1, -1), (3, -1), (-1, 3)
    This avoids using a vertex buffer and guarantees full-screen coverage.
- Sets the clip-space position (out.pos) to vec4(p[vi], 0.0, 1.0) so the rasterizer can produce fragments.
- Computes a 0..1 texture/UV coordinate from NDC: out.uv = 0.5 * (out.pos.xy + vec2(1.0)).
    This maps NDC X/Y in [-1, 1] to UV in [0, 1].

Outputs (expected in VSOut):
- pos: should be annotated as @builtin(position) — clip-space position for rasterization.
- uv: user-defined interpolated texture coordinate for the fragment stage.

Notes:
- The full-screen-triangle technique is more efficient than a quad because it uses fewer vertices and avoids a vertex buffer.
- The computed UV assumes NDC Y-up convention; if your sampling convention differs (e.g., texture origin), you may need to flip Y when sampling.
- Ensure vi is within 0..2; behavior is undefined for other indices.
*/
@vertex
fn vs_main(@builtin(vertex_index) vi: u32) -> VSOut {
    let p = array<vec2<f32>, 3>(
        vec2<f32>(-1.0, -1.0),
        vec2<f32>( 3.0, -1.0),
        vec2<f32>(-1.0,  3.0)
    );
    var out: VSOut;
    out.pos = vec4<f32>(p[vi], 0.0, 1.0);
    out.uv = 0.5 * (out.pos.xy + vec2<f32>(1.0));
    return out;
}

fn h_at(xi: i32, yi: i32) -> f32 {
  let N = i32(N_u32());
  let x = clamp(xi, 0, N - 1);
  let y = clamp(yi, 0, N - 1);
  return clamp(dye_in[idx(u32(x), u32(y))], 0.0, 1.0);
}

@fragment
fn fs_main(in: VSOut) -> @location(0) vec4<f32> {
  let u = clamp(in.uv.x, 0.0, 0.999999);
  let v = clamp(in.uv.y, 0.0, 0.999999);

  let N = i32(N_u32());
  let x = i32(u32(u * f32(N)));
  let y = i32(u32(v * f32(N)));

  // "height" from dye
  let h  = h_at(x, y);

  // Surface mask
  let surface = smoothstep(0.05, 0.20, h);

  // Gradient -> normal
  let hx = 0.5 * (h_at(x + 1, y) - h_at(x - 1, y));
  let hy = 0.5 * (h_at(x, y + 1) - h_at(x, y - 1));

  // Tune this: larger = steeper waves
  let normalStrength = 20.0;

  let n = normalize(vec3<f32>(-hx * normalStrength, -hy * normalStrength, 1.0));

  // Lighting
  let lightDir = normalize(vec3<f32>(0.3, 0.6, 1.0));
  let viewDir  = vec3<f32>(0.0, 0.0, 1.0);

  let diff = clamp(dot(n, lightDir), 0.0, 1.0);

  // Specular highlight (shiny water)
  let halfDir = normalize(lightDir + viewDir);
  let spec = pow(clamp(dot(n, halfDir), 0.0, 1.0), 80.0);

  // Base water color
  let deep = vec3<f32>(0.02, 0.10, 0.25);
  let shallow = vec3<f32>(0.05, 0.35, 0.9);

  // Deeper where h is larger
  let waterCol = mix(deep, shallow, clamp(h * 1.5, 0.0, 1.0));

  // Foam from speed (optional)
  let i = idx(u32(x), u32(y));
  let speed = length(vel_in[i]);
  let foam = smoothstep(15.0, 40.0, speed) * surface; // tune thresholds
  let foamCol = vec3<f32>(0.85, 0.93, 1.0);

  // Combine
  var col = waterCol * (0.25 + 0.75 * diff);
  col += spec * 1.2;
  col = mix(col, foamCol, foam);

  // Composite against background
  let bg = vec3<f32>(0.03, 0.03, 0.05);
  col = mix(bg, col, surface);

  return vec4<f32>(col, 1.0);
}

// Helper visualizations (set in init.ts:InitPipelines:renderPipeline)

//  --------- Shader: dye_simple ---------

@fragment
fn fs_dye_simple(in: VSOut) -> @location(0) vec4<f32> {
    let u = clamp(in.uv.x, 0.0, 0.999999);
    // We invert Y in TS already, so no need to do it here:
    let v = clamp(in.uv.y, 0.0, 0.999999);

    let N = N_u32();
    let x = u32(u * f32(N));
    let y = u32(v * f32(N));
    let i = idx(x, y);

    // sample dye field (grayscale)
    let d = clamp(dye_in[i], 0.0, 1.0);
    let water = vec3<f32>(1.0, 1.0, 1.0);
    return vec4<f32>(water * d, 1.0);
}

//  --------- Shader: dye_with_foam ---------

@fragment
fn fs_dye_with_foam(in: VSOut) -> @location(0) vec4<f32> {
    let u = clamp(in.uv.x, 0.0, 0.999999);
    let v = clamp(in.uv.y, 0.0, 0.999999);

    let N = N_u32();
    let x = u32(u * f32(N));
    let y = u32(v * f32(N));
    let i = idx(x, y);

    let d = clamp(dye_in[i], 0.0, 1.0);

    // Basic water/foam blend
    let base = vec3<f32>(0.05, 0.25, 0.9);   // water color
    let foam = vec3<f32>(0.8, 0.9, 1.0);

    let foamAmt = smoothstep(0.02, 0.08, length(vel_in[i]) * 0.02);
    let color = mix(base, foam, foamAmt);

    // use dye as modulation / alpha-like
    let alpha = smoothstep(0.2, 0.6, d);
    return vec4<f32>(color * alpha, 1.0);
}

//  --------- Shader: dye_simple_lighting ---------

@fragment
fn fs_dye_simple_lighting(in: VSOut) -> @location(0) vec4<f32> {
    let u = clamp(in.uv.x, 0.0, 0.999999);
    let v = clamp(in.uv.y, 0.0, 0.999999);

    let N = N_u32();
    let x = u32(u * f32(N));
    let y = u32(v * f32(N));
    let i = idx(x, y);

    // ------- DYE WITH SIMPLE LIGHTING -------
    let base = vec3<f32>(0.05, 0.25, 0.9);
    let dx = dye_in[idx(min(x+1u,N-1u),y)] - dye_in[idx(max(x-1u,0u),y)];
    let dy = dye_in[idx(x,min(y+1u,N-1u))] - dye_in[idx(x,max(y-1u,0u))];
    let n = normalize(vec3<f32>(-dx, -dy, 1.0));
    let light = normalize(vec3<f32>(0.4, 0.6, 1.0));
    let lambert = clamp(dot(n, light), 0.0, 1.0);
    return vec4<f32>(base * (0.3 + 0.7*lambert), 1.0);
}

//  --------- Shader: velocity_magnitude ---------
@fragment
fn fs_velocity_magnitude(in: VSOut) -> @location(0) vec4<f32> {
    let u = clamp(in.uv.x, 0.0, 0.999999);
    let v = clamp(in.uv.y, 0.0, 0.999999);

    let N = N_u32();
    let x = u32(u * f32(N));
    let y = u32(v * f32(N));
    let i = idx(x, y);

    // visualize velocity magnitude (grayscale)
    let m = clamp(length(vel_in[i]) * 0.05, 0.0, 1.0);
    return vec4<f32>(m, m, m, 1.0);
}

//  --------- Shader: pressure_map ---------
@fragment
fn fs_pressure(in: VSOut) -> @location(0) vec4<f32> {
    let u = clamp(in.uv.x, 0.0, 0.999999);
    let v = clamp(in.uv.y, 0.0, 0.999999);

    let N = N_u32();
    let x = u32(u * f32(N));
    let y = u32(v * f32(N));
    let i = idx(x, y);

    // visualize pressure with an extended multi-stop palette
    let p = p_in[i];

    // choose a scale that makes structure visible
    let scale = 0.02;                 // tune; start 0.01..0.1 depending on your div magnitude
    let t = clamp(p / scale, -1.0, 1.0);

    // map t (-1..1) to 0..1
    let s01 = clamp((t + 1.0) * 0.5, 0.0, 1.0);

    // palette: purple -> blue -> cyan -> green -> yellow -> orange -> red
    const PALETTE: array<vec3<f32>, 7> = array<vec3<f32>, 7>(
        vec3<f32>(0.30, 0.10, 0.70), // purple
        vec3<f32>(0.10, 0.30, 1.00), // blue
        vec3<f32>(0.10, 0.90, 0.90), // cyan
        vec3<f32>(0.20, 0.90, 0.30), // green
        vec3<f32>(1.00, 0.90, 0.10), // yellow
        vec3<f32>(1.00, 0.50, 0.00), // orange
        vec3<f32>(1.00, 0.20, 0.10)  // red
    );

    let stops = 7u;
    let idxf = s01 * f32(stops - 1u);
    let i0 = u32(floor(idxf));
    let i1 = min(i0 + 1u, stops - 1u);
    let f = idxf - f32(i0);

    let c0 = PALETTE[i0];
    let c1 = PALETTE[i1];
    let color = mix(c0, c1, f);

    return vec4<f32>(color, 1.0);
}

//  --------- Shader: dye_plus_velocity ---------
@fragment
fn fs_dye_plus_velocity(in: VSOut) -> @location(0) vec4<f32> {
    let u = clamp(in.uv.x, 0.0, 0.999999);
    let v = clamp(in.uv.y, 0.0, 0.999999);

    let N = N_u32();
    let x = u32(u * f32(N));
    let y = u32(v * f32(N));
    let i = idx(x, y);

    let d = clamp(dye_in[i], 0.0, 1.0);
    let m = clamp(length(vel_in[i]) * 0.05, 0.0, 1.0);

    // visualize dye and velocity magnitude together
    return vec4<f32>(d + m, d * 0.5, m, 1.0);
}
