struct Uniforms {
    angle : f32,
    _pad1 : f32,
    _pad2 : f32,
    _pad3 : f32,
};

@group(0) @binding(0) var<uniform> uniforms : Uniforms;

struct VSOutput {
    @builtin(position) position : vec4f,
};

@vertex
fn vs_main(@builtin(vertex_index) VertexIndex : u32) -> VSOutput {
    var out : VSOutput;

    let basePositions = array<vec2f, 3>(
        vec2f(0.0, 0.5),
        vec2f(-0.5, -0.5),
        vec2f(0.5, -0.5)
    );

    let pos = basePositions[VertexIndex];

    let c = cos(uniforms.angle);
    let s = sin(uniforms.angle);

    // 2D rotation matrix
    let rotated = vec2f(
        pos.x * c - pos.y * s,
        pos.x * s + pos.y * c
    );

    out.position = vec4f(rotated, 0.0, 1.0);
    return out;
}

@fragment
fn fs_main(in: VSOutput) -> @location(0) vec4f {
    // simple constant color
    return vec4f(0, 0.2, 0.9, 1.0);
}
