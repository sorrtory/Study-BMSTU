import glfw
from OpenGL.GL import *
import numpy as np

# Vertex shader source code
VERTEX_SHADER_SOURCE = """
#version 330 core
layout (location = 0) in vec3 aPos;
void main()
{
    gl_Position = vec4(aPos, 1.0);
}
"""

# Fragment shader source code
FRAGMENT_SHADER_SOURCE = """
#version 330 core
out vec4 FragColor;
void main()
{
    FragColor = vec4(1.0, 0.5, 0.2, 1.0);
}
"""

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        print(glGetShaderInfoLog(shader).decode('utf-8'))
        raise RuntimeError("Shader compilation failed")
    return shader

def create_shader_program():
    vertex_shader = compile_shader(VERTEX_SHADER_SOURCE, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(FRAGMENT_SHADER_SOURCE, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        print(glGetProgramInfoLog(program).decode('utf-8'))
        raise RuntimeError("Shader linking failed")
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    return program

def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)

def main():
    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")
    
    window = glfw.create_window(800, 800, "Hello Triangle", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")
    
    glfw.make_context_current(window)
    # Query the actual framebuffer size
    width, height = glfw.get_framebuffer_size(window)
    glViewport(0, 0, width, height)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    
    vertices = np.array([
        -0.5, -0.5, 0.0,
         0.5, -0.5, 0.0,
         0.0,  0.5, 0.0
    ], dtype=np.float32)
    
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * vertices.itemsize, None)
    glEnableVertexAttribArray(0)
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    
    shader_program = create_shader_program()
    
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        
        glUseProgram(shader_program)
        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteProgram(shader_program)
    
    glfw.terminate()

if __name__ == "__main__":
    main()
