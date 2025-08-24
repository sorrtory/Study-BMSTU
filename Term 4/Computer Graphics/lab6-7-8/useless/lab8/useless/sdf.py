import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

# Vertex Shader (fullscreen quad)
VERTEX_SHADER = """
#version 330 core
out vec2 uv;
void main() {
    const vec2 pos[4] = vec2[](
        vec2(-1.0, -1.0),
        vec2( 1.0, -1.0),
        vec2(-1.0,  1.0),
        vec2( 1.0,  1.0)
    );
    gl_Position = vec4(pos[gl_VertexID], 0.0, 1.0);
    uv = (pos[gl_VertexID] + 1.0) * 0.5;
}
"""

# Fragment Shader (raymarch SDF sphere)
FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;
in vec2 uv;

uniform vec3 camPos;
uniform mat3 camRot;
uniform float time;

float sdSphere(vec3 p, float s) {
    return length(p) - s;
}

float map(vec3 p) {
    return sdSphere(p, 1.0);
}

vec3 getRayDir(vec2 uv) {
    vec2 screen = uv * 2.0 - 1.0;
    float fov = 1.0;
    return normalize(camRot * vec3(screen * fov, -1.0));
}

vec3 raymarch(vec3 ro, vec3 rd) {
    float t = 0.0;
    for (int i = 0; i < 100; i++) {
        vec3 p = ro + rd * t;
        float d = map(p);
        if (d < 0.001) {
            return vec3(1.0 - t * 0.1);  // Shaded sphere
        }
        t += d;
        if (t > 10.0) break;
    }
    return vec3(0.0);  // Background
}

void main() {
    vec3 ro = camPos;
    vec3 rd = getRayDir(uv);
    vec3 color = raymarch(ro, rd);
    FragColor = vec4(color, 1.0);
}
"""

def main():
    # Init GLFW
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    window = glfw.create_window(800, 600, "SDF Sphere", None, None)
    glfw.make_context_current(window)

    # Compile shaders
    shader = compileProgram(
        compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Uniform locations
    camPosLoc = glGetUniformLocation(shader, "camPos")
    camRotLoc = glGetUniformLocation(shader, "camRot")
    timeLoc = glGetUniformLocation(shader, "time")

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(shader)

        time_val = glfw.get_time()
        cam_pos = np.array([0.0, 0.0, 3.0], dtype=np.float32)

        # angle = time_val * 0.5
        angle = 0
        rot_y = np.array([
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)]
        ], dtype=np.float32)

        glUniform3fv(camPosLoc, 1, cam_pos)
        glUniformMatrix3fv(camRotLoc, 1, GL_TRUE, rot_y)
        glUniform1f(timeLoc, time_val)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
