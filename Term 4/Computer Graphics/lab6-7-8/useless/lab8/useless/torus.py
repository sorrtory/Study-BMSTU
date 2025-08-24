import glfw
from OpenGL.GL import *
import numpy as np
from math import sin, cos, pi
from PIL import Image

# -------- Torus Mesh --------
class Torus:
    def __init__(self, R, r, num_major=40, num_minor=20):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.indices = []

        for i in range(num_major):
            for j in range(num_minor):
                theta = 2 * pi * i / num_major
                phi = 2 * pi * j / num_minor
                cos_theta, sin_theta = cos(theta), sin(theta)
                cos_phi, sin_phi = cos(phi), sin(phi)

                x = (R + r * cos_phi) * cos_theta
                y = (R + r * cos_phi) * sin_theta
                z = r * sin_phi

                nx = cos_theta * cos_phi
                ny = sin_theta * cos_phi
                nz = sin_phi

                u = i / num_major
                v = j / num_minor

                self.vertices.append((x, y, z))
                self.normals.append((nx, ny, nz))
                self.texcoords.append((u, v))

        for i in range(num_major):
            for j in range(num_minor):
                i1 = i * num_minor + j
                i2 = ((i + 1) % num_major) * num_minor + j
                i3 = ((i + 1) % num_major) * num_minor + (j + 1) % num_minor
                i4 = i * num_minor + (j + 1) % num_minor
                self.indices += [i1, i2, i4, i2, i3, i4]

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.normals = np.array(self.normals, dtype=np.float32)
        self.texcoords = np.array(self.texcoords, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)

# -------- Shader Compilation --------
def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader).decode())
    return shader

def create_shader_program(vs_src, fs_src):
    vs = compile_shader(vs_src, GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(program).decode())
    glDeleteShader(vs)
    glDeleteShader(fs)
    return program

# -------- VAO Setup --------
def create_vao(torus):
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    vertex_data = np.hstack([torus.vertices, torus.normals, torus.texcoords])
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, torus.indices.nbytes, torus.indices, GL_STATIC_DRAW)

    stride = (3 + 3 + 2) * 4
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
    glEnableVertexAttribArray(2)

    glBindVertexArray(0)
    return vao, len(torus.indices)

# -------- Texture --------
def load_texture(path):
    img = Image.open(path).convert('RGB')
    img_data = np.array(img, dtype=np.uint8)

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return tex

# -------- Matrices --------
def perspective(fov, aspect, near, far):
    f = 1.0 / np.tan(fov / 2)
    return np.array([
        [f/aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
        [0, 0, -1, 0]
    ], dtype=np.float32)

def lookAt(eye, center, up):
    f = center - eye
    f /= np.linalg.norm(f)
    s = np.cross(f, up)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)

    result = np.identity(4, dtype=np.float32)
    result[:3, 0] = s
    result[:3, 1] = u
    result[:3, 2] = -f
    result[:3, 3] = -np.dot(result[:3, :3], eye)
    return result.T

# -------- Main Program --------
VERTEX_SHADER_SRC = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec2 aTexCoord;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoord = aTexCoord;
    // gl_Position = projection * view * vec4(FragPos, 1.0);
    gl_Position = vec4(aPos, 1.0);
    //gl_Position = vec4(0,0,0, 1.);
}
"""

FRAGMENT_SHADER_SRC = """
#version 330 core
in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

out vec4 FragColor;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform sampler2D texture1;

void main() {
    vec3 lightColor = vec3(1.0);
    vec3 objectColor = texture(texture1, TexCoord).rgb;

    vec3 ambient = 0.2 * lightColor;
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    vec3 specular = 0.5 * spec * lightColor;

    vec3 result = (ambient + diffuse + specular) * objectColor;
    //FragColor = vec4(result, 1.0);
    FragColor = vec4(1.0, 0.0, 0.0, 1.0); // solid red
}
"""

def main():
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    window = glfw.create_window(800, 600, "Textured Torus (VAO + Shader)", None, None)
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)

    torus = Torus(1.0, 0.4, 50, 25)
    vao, index_count = create_vao(torus)
    program = create_shader_program(VERTEX_SHADER_SRC, FRAGMENT_SHADER_SRC)
    tex_id = load_texture("texture.jpg")  # Place a JPG texture in same folder

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClearColor(0.1, 0.1, 0.1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(program)

        # Animate rotation
        t = glfw.get_time()
        model = np.identity(4, dtype=np.float32)
        rotation_y = np.array([
            [cos(t), 0, sin(t), 0],
            [0,     1, 0,     0],
            [-sin(t), 0, cos(t), 0],
            [0,     0, 0,     1]
        ], dtype=np.float32)
        model = rotation_y

        view = lookAt(
            eye=np.array([0, 0, 3], dtype=np.float32),
            center=np.array([0, 0, 0], dtype=np.float32),
            up=np.array([0, 1, 0], dtype=np.float32)
        )
        proj = perspective(np.radians(45.0), 800/600, 0.1, 100.0)

        glUniformMatrix4fv(glGetUniformLocation(program, "model"), 1, GL_FALSE, model)
        glUniformMatrix4fv(glGetUniformLocation(program, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(program, "projection"), 1, GL_FALSE, proj)

        glUniform3f(glGetUniformLocation(program, "lightPos"), 2.0, 2.0, 2.0)
        glUniform3f(glGetUniformLocation(program, "viewPos"), 0.0, 0.0, 3.0)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glUniform1i(glGetUniformLocation(program, "texture1"), 0)

        glBindVertexArray(vao)
        glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, None)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
