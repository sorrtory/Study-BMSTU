from OpenGL.GL import *
import numpy as np
from math import pi, cos, sin

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

void main()
{
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoord = aTexCoord;
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
"""

FRAGMENT_SHADER_SRC = """
#version 330 core
in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D texture1;

uniform vec3 lightPos;
uniform vec3 viewPos;

// === Global light settings ===
uniform vec3 globalAmbient;   // e.g. vec3(0.2, 0.2, 0.2)
uniform vec3 lightColor = vec3(1.0, 1.0, 1.0);      // e.g. vec3(1.0, 1.0, 1.0)

// === Material properties ===
uniform vec4 matAmbient;
uniform vec4 matDiffuse;
uniform vec4 matSpecular;
uniform float shininess;

uniform bool useTexture = true;

void main()
{
    vec3 objectColor;
    if (useTexture) {
        objectColor = texture(texture1, TexCoord).rgb;
    } else {
        objectColor = vec3(1.0, 0.5, 0.31);
    }

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);

    // === Ambient ===
    vec3 ambient = globalAmbient * matAmbient.rgb;

    // === Diffuse ===
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * matDiffuse.rgb * lightColor;

    // === Specular ===
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular = spec * matSpecular.rgb * lightColor;

    vec3 result = (ambient + diffuse + specular) * objectColor;
    FragColor = vec4(result, 1.0);
}

"""


def create_vao(torus):
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Vertex buffer
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    vertex_data = np.hstack([torus.vertices, torus.normals, torus.texcoords])
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    # Element buffer
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, torus.indices.nbytes, torus.indices, GL_STATIC_DRAW)

    stride = (3 + 3 + 2) * 4  # 3 pos + 3 norm + 2 texcoord, each float = 4 bytes

    # Position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Normal
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    # TexCoord
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
    glEnableVertexAttribArray(2)

    glBindVertexArray(0)
    return vao

def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        raise RuntimeError(glGetShaderInfoLog(shader).decode())
    return shader

def create_shader_program():
    vs = compile_shader(VERTEX_SHADER_SRC, GL_VERTEX_SHADER)
    fs = compile_shader(FRAGMENT_SHADER_SRC, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)

    if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
        raise RuntimeError(glGetProgramInfoLog(program).decode())

    glDeleteShader(vs)
    glDeleteShader(fs)
    return program




