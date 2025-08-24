import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import math

# Vertex shader (for cube vertices)
vertex_shader = """
#version 330
layout(location = 0) in vec3 position;
uniform mat4 projection;
uniform mat4 model_view;
void main()
{
    gl_Position = projection * model_view * vec4(position, 1.0);
}
"""

# Fragment shader (simple color)
fragment_shader = """
#version 330
out vec4 FragColor;
void main()
{
    FragColor = vec4(0.0, 0.0, 1.0, 1.0);  // Light blue color
}
"""

# Cube vertices
cube_vertices = np.array([
    # Front face
    -0.5, -0.5,  0.5,
     0.5, -0.5,  0.5,
     0.5,  0.5,  0.5,
    -0.5,  0.5,  0.5,
    # Back face
    -0.5, -0.5, -0.5,
     0.5, -0.5, -0.5,
     0.5,  0.5, -0.5,
    -0.5,  0.5, -0.5,
], dtype=np.float32)

# Cube indices (for drawing cube faces)
cube_indices = np.array([
    0, 1, 2, 2, 3, 0,  # Front face
    4, 5, 6, 6, 7, 4,  # Back face
    0, 1, 5, 5, 4, 0,  # Bottom face
    3, 2, 6, 6, 7, 3,  # Top face
    0, 3, 7, 7, 4, 0,  # Left face
    1, 2, 6, 6, 5, 1   # Right face
], dtype=np.uint32)

def create_projection_matrix():
    """ Isometric projection matrix """
    angle = math.radians(35.264)  # Isometric angle (35.264°)
    scale = 1.0 / math.sqrt(2)  # Isometric scaling factor
    return np.array([
        [scale, 0, -scale, 0],
        [0, 1, 0, 0],
        [scale, 0, scale, 0],
        [0, 0, 0, 1],
    ], dtype=np.float32)

def create_model_view_matrix(rotate_x, rotate_y, scale):
    """ Apply model-view transformations: rotation, scaling """
    cos_rx, sin_rx = math.cos(rotate_x), math.sin(rotate_x)
    cos_ry, sin_ry = math.cos(rotate_y), math.sin(rotate_y)

    rotation_x = np.array([
        [1, 0, 0, 0],
        [0, cos_rx, -sin_rx, 0],
        [0, sin_rx, cos_rx, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    rotation_y = np.array([
        [cos_ry, 0, sin_ry, 0],
        [0, 1, 0, 0],
        [-sin_ry, 0, cos_ry, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    scaling = np.array([
        [scale, 0, 0, 0],
        [0, scale, 0, 0],
        [0, 0, scale, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    return scaling @ rotation_y @ rotation_x

def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Isometric Cube", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Compile shaders
    shader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                            compileShader(fragment_shader, GL_FRAGMENT_SHADER))
    glUseProgram(shader)

    # VAO and VBO setup
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, cube_indices.nbytes, cube_indices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * cube_vertices.itemsize, None)
    glEnableVertexAttribArray(0)

    # Set polygon mode (start in solid mode)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Enable depth testing
    glEnable(GL_DEPTH_TEST)

    rotate_x = 0.3
    rotate_y = 0.3
    scale = 1.0
    is_wireframe = True
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if is_wireframe else GL_FILL)

    # Loop until window closed
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Handle input
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            rotate_x -= 0.02
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            rotate_x += 0.02
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            rotate_y -= 0.02
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            rotate_y += 0.02
        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
            scale += 0.02
        if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
            scale -= 0.02
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            is_wireframe = not is_wireframe
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if is_wireframe else GL_FILL)

        # Create projection and model-view matrices
        projection = create_projection_matrix()
        model_view = create_model_view_matrix(rotate_x, rotate_y, scale)

        # Send matrices to shaders
        proj_loc = glGetUniformLocation(shader, "projection")
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

        mv_loc = glGetUniformLocation(shader, "model_view")
        glUniformMatrix4fv(mv_loc, 1, GL_FALSE, model_view)

        # Draw cube
        glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)

        # Swap buffers and poll for events
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
