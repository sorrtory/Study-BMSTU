import glfw
from OpenGL.GL import *
import numpy as np
import math
import ctypes

# Vertex shader source
VERTEX_SHADER_SRC = """
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    // gl_Position = vec4(0,0,0, 1.);

}
"""

# Fragment shader source
FRAGMENT_SHADER_SRC = """
#version 330 core
out vec4 FragColor;

void main() {

    FragColor = vec4(1.0, 0.4, 0.2, 1.0); 
}
"""

# Cube vertex data
vertices = np.array([
    -0.5, -0.5, -0.5,  # 0
     0.5, -0.5, -0.5,  # 1
     0.5,  0.5, -0.5,  # 2
    -0.5,  0.5, -0.5,  # 3
    -0.5, -0.5,  0.5,  # 4
     0.5, -0.5,  0.5,  # 5
     0.5,  0.5,  0.5,  # 6
    -0.5,  0.5,  0.5   # 7
], dtype=np.float32)

indices = np.array([
    0, 1, 2, 2, 3, 0,
    4, 5, 6, 6, 7, 4,
    0, 1, 5, 5, 4, 0,
    2, 3, 7, 7, 6, 2,
    0, 3, 7, 7, 4, 0,
    1, 2, 6, 6, 5, 1
], dtype=np.uint32)

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader).decode())
    return shader

def create_shader_program():
    vs = compile_shader(VERTEX_SHADER_SRC, GL_VERTEX_SHADER)
    fs = compile_shader(FRAGMENT_SHADER_SRC, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(program).decode())
    glDeleteShader(vs)
    glDeleteShader(fs)
    return program

def perspective(fovy, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fovy) / 2)
    proj = np.zeros((4, 4), dtype=np.float32)
    proj[0, 0] = f / aspect
    proj[1, 1] = f
    proj[2, 2] = (far + near) / (near - far)
    proj[2, 3] = (2 * far * near) / (near - far)
    proj[3, 2] = -1
    return proj

def look_at(eye, center, up):
    eye = np.array(eye, dtype=np.float32)
    center = np.array(center, dtype=np.float32)
    up = np.array(up, dtype=np.float32)

    f = center - eye
    f /= np.linalg.norm(f)
    s = np.cross(f, up)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)

    m = np.identity(4, dtype=np.float32)
    m[0, :3] = s
    m[1, :3] = u
    m[2, :3] = -f
    m[0, 3] = -np.dot(s, eye)
    m[1, 3] = -np.dot(u, eye)
    m[2, 3] = np.dot(f, eye)
    return m

def rotate_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1]
    ], dtype=np.float32)

# Setup window
glfw.init()
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
window = glfw.create_window(800, 600, "Rotating Cube (GLFW + Shaders)", None, None)
glfw.make_context_current(window)

# Prepare buffers
vao = glGenVertexArrays(1)
vbo = glGenBuffers(1)
ebo = glGenBuffers(1)
glBindVertexArray(vao)

glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))

shader = create_shader_program()
glUseProgram(shader)

glEnable(GL_DEPTH_TEST)

while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    angle = glfw.get_time()
    model = rotate_y(angle)
    view = look_at([2, 2, 2], [0, 0, 0], [0, 1, 0])
    projection = perspective(45, 800/600, 0.1, 100)

    glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_TRUE, model)
    glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_TRUE, view)
    glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_TRUE, projection)

    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
    glfw.swap_buffers(window)

glfw.terminate()
 