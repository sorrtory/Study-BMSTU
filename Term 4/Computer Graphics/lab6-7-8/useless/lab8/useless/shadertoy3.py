# https://stackoverflow.com/questions/39645910/how-to-port-shadertoy-to-standalone-opengl

# https://www.shadertoy.com/view/XXyGzh

import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

vertex_shader_source = """
#version 330 core
layout (location = 0) in vec2 position;            
layout (location = 1) in vec2 inTexCoord;

out vec2 texCoord;
void main() {
    texCoord = inTexCoord;
    gl_Position = vec4(position.x, position.y, 0.0f, 1.0f);
}
"""

fragment_shader_source = """
#version 330 core
in vec2 texCoord;
uniform vec2 iMouse;
uniform vec2 iResolution;
uniform float iTime;
out vec4 fragColor;
vec2 fragCoord = gl_FragCoord.xy;
#define PI 3.14159265359
#define TWOPI 6.28318530718

void mainImage( out vec4 o, vec2 u )
{
    vec2 v = iResolution.xy;
         u = .2*(u+u-v)/v.y;    
         
    vec4 z = o = vec4(1,2,3,0);
     
    for (float a = .5, t = iTime, i; 
         ++i < 19.; 
         o += (1. + cos(z+t)) 
            / length((1.+i*dot(v,v)) 
                   * sin(1.5*u/(.5-dot(u,u)) - 9.*u.yx + t))
         )  
        v = cos(++t - 7.*u*pow(a += .03, i)) - 5.*u, 
        // use stanh here if shader has black artifacts
        //   vvvv
        u += tanh(40. * dot(u *= mat2(cos(i + .02*t - vec4(0,11,33,0)))
                           ,u)
                      * cos(1e2*u.yx + t)) / 2e2
           + .2 * a * u
           + cos(4./exp(dot(o,o)/1e2) + t) / 3e2;
              
     o = 25.6 / (min(o, 13.) + 164. / o) 
       - dot(u, u) / 250.;
}

void main() {
    vec2 uv = fragCoord;
    mainImage(fragColor, uv);
}
"""

def main():
    width = 800
    height = 600
    
    if not glfw.init():
        raise Exception("Failed to initialize GLFW")
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    
    window = glfw.create_window(width, height, "PyOpenGL Raytracing", None, None)
    if not window:
        glfw.terminate()
        raise Exception("Failed to create GLFW window")
    
    glfw.make_context_current(window)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    
    # Quad vertices (position + texture coordinates)
    quad_verts = np.array([
        -1.0, -1.0, 0.0, 0.0,
        -1.0,  1.0, 0.0, 1.0,
         1.0, -1.0, 1.0, 0.0,
         1.0, -1.0, 1.0, 0.0,
        -1.0,  1.0, 0.0, 1.0,
         1.0,  1.0, 1.0, 1.0
    ], dtype=np.float32)
    
    # Create VAO and VBO
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, quad_verts.nbytes, quad_verts, GL_STATIC_DRAW)
    
    # Position attribute
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    # Texture coordinate attribute
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
    glEnableVertexAttribArray(1)
    
    glBindVertexArray(0)
    
    # Create framebuffer
    framebuffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
    
    # Create texture for framebuffer
    tex_color = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_color)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex_color, 0)
    
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    # Compile shaders
    vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
    shader_program = compileProgram(vertex_shader, fragment_shader)
    
    glUseProgram(shader_program)
    
    # Set resolution uniform
    resolution_loc = glGetUniformLocation(shader_program, "iResolution")
    glUniform2f(resolution_loc, width, height)
    
    # Set default mouse position
    mouse_loc = glGetUniformLocation(shader_program, "iMouse")
    glUniform2f(mouse_loc, 0.0, 0.0)
    
    last_time = glfw.get_time()
    
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time
        
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)
        
        # Update time uniform
        time_loc = glGetUniformLocation(shader_program, "iTime")
        glUniform1f(time_loc, current_time % 60)
        
        # Render to framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Render to default framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glUseProgram(shader_program)
        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    glfw.terminate()

if __name__ == "__main__":
    main()