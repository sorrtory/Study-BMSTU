import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import math
from pyrr import Matrix44, Vector3

# Vertex shader source code
VERTEX_SHADER = """
#version 330 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_color;

out vec3 v_color;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);
    v_color = a_color;
}
"""

# Fragment shader source code
FRAGMENT_SHADER = """
#version 330 core

in vec3 v_color;
out vec4 frag_color;

void main()
{
    frag_color = vec4(v_color, 1.0);
}
"""

class SphereInCubeSimulation:
    def __init__(self):
        # Initialize GLFW
        if not glfw.init():
            raise Exception("GLFW can't be initialized")

        # Window settings
        self.width = 800
        self.height = 600
        self.title = "Sphere Flying Inside Cube"

        # Create window
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("GLFW window can't be created")

        glfw.make_context_current(self.window)
        glfw.set_window_size_callback(self.window, self._resize_callback)

        # OpenGL settings
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)

        # Shader program
        self.shader = self._create_shader()
        glUseProgram(self.shader)

        # Get uniform locations
        self.model_loc = glGetUniformLocation(self.shader, "model")
        self.view_loc = glGetUniformLocation(self.shader, "view")
        self.projection_loc = glGetUniformLocation(self.shader, "projection")

        # Camera settings
        self.camera_pos = Vector3([0.0, 0.0, 5.0])
        self.camera_front = Vector3([0.0, 0.0, -1.0])
        self.camera_up = Vector3([0.0, 1.0, 0.0])

        # Cube settings
        self.cube_size = 3.0
        self.cube_vertices, self.cube_colors, self.cube_indices = self._create_cube()

        # Sphere settings
        self.sphere_radius = 0.3
        self.sphere_pos = Vector3([0.0, 0.0, 0.0])
        self.sphere_velocity = Vector3([0.03, 0.02, 0.04])
        self.sphere_vertices, self.sphere_colors, self.sphere_indices = self._create_sphere(20, 20)

        # Setup VAOs and VBOs
        self._setup_buffers()

        # Projection matrix
        self.projection = Matrix44.perspective_projection(45.0, self.width / self.height, 0.1, 100.0)
        glUniformMatrix4fv(self.projection_loc, 1, GL_FALSE, self.projection)

    def _create_shader(self):
        # Compile shaders
        vertex_shader = compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
        fragment_shader = compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        
        # Create shader program
        shader = compileProgram(vertex_shader, fragment_shader)
        return shader

    def _create_cube(self):
        # Cube vertices (8 vertices)
        s = self.cube_size / 2
        vertices = [
            # Front face
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s],
            # Back face
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s]
        ]
        
        # Cube colors (each face has different color)
        colors = [
            # Front face (red)
            [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0],
            # Back face (green)
            [0.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0],
            # Left face (blue)
            [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0],
            # Right face (yellow)
            [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0],
            # Top face (cyan)
            [0.0, 1.0, 1.0], [0.0, 1.0, 1.0], [0.0, 1.0, 1.0], [0.0, 1.0, 1.0],
            # Bottom face (magenta)
            [1.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 0.0, 1.0]
        ]
        
        # Cube indices (12 triangles)
        indices = [
            # Front face
            0, 1, 2, 2, 3, 0,
            # Back face
            4, 5, 6, 6, 7, 4,
            # Left face
            4, 0, 3, 3, 7, 4,
            # Right face
            1, 5, 6, 6, 2, 1,
            # Top face
            3, 2, 6, 6, 7, 3,
            # Bottom face
            4, 5, 1, 1, 0, 4
        ]
        
        return np.array(vertices, dtype=np.float32), np.array(colors, dtype=np.float32), np.array(indices, dtype=np.uint32)

    def _create_sphere(self, stacks, sectors):
        vertices = []
        colors = []
        indices = []
        
        # Generate vertices
        for i in range(stacks + 1):
            phi = math.pi * i / stacks
            for j in range(sectors):
                theta = 2.0 * math.pi * j / sectors
                
                x = self.sphere_radius * math.sin(phi) * math.cos(theta)
                y = self.sphere_radius * math.sin(phi) * math.sin(theta)
                z = self.sphere_radius * math.cos(phi)
                
                vertices.append([x, y, z])
                colors.append([0.8, 0.8, 0.8])  # Light gray color
        
        # Generate indices
        for i in range(stacks):
            for j in range(sectors):
                first = i * sectors + j
                second = first + sectors
                
                indices.append(first)
                indices.append(second)
                indices.append((first + 1) % sectors + i * sectors)
                
                indices.append(second)
                indices.append((second + 1) % sectors + i * sectors)
                indices.append((first + 1) % sectors + i * sectors)
        
        return np.array(vertices, dtype=np.float32), np.array(colors, dtype=np.float32), np.array(indices, dtype=np.uint32)

    def _setup_buffers(self):
        # Cube VAO and VBO
        self.cube_vao = glGenVertexArrays(1)
        glBindVertexArray(self.cube_vao)
        
        # Vertex VBO
        self.cube_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.cube_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.cube_vertices.nbytes, self.cube_vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        # Color VBO
        self.cube_color_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.cube_color_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.cube_colors.nbytes, self.cube_colors, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        # EBO
        self.cube_ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.cube_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.cube_indices.nbytes, self.cube_indices, GL_STATIC_DRAW)
        
        # Sphere VAO and VBO
        self.sphere_vao = glGenVertexArrays(1)
        glBindVertexArray(self.sphere_vao)
        
        # Vertex VBO
        self.sphere_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.sphere_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.sphere_vertices.nbytes, self.sphere_vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        # Color VBO
        self.sphere_color_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.sphere_color_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.sphere_colors.nbytes, self.sphere_colors, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        # EBO
        self.sphere_ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.sphere_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.sphere_indices.nbytes, self.sphere_indices, GL_STATIC_DRAW)
        
        # Unbind
        glBindVertexArray(0)

    def _resize_callback(self, window, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        self.projection = Matrix44.perspective_projection(45.0, width / height, 0.1, 100.0)
        glUniformMatrix4fv(self.projection_loc, 1, GL_FALSE, self.projection)

    def _update_sphere_position(self):
        # Update sphere position
        self.sphere_pos += self.sphere_velocity
        
        # Check for collisions with cube boundaries
        cube_half_size = self.cube_size / 2
        for i in range(3):
            if abs(self.sphere_pos[i]) + self.sphere_radius > cube_half_size:
                self.sphere_velocity[i] *= -1  # Reverse velocity on collision
                
                # Adjust position to prevent sticking
                if self.sphere_pos[i] > 0:
                    self.sphere_pos[i] = cube_half_size - self.sphere_radius
                else:
                    self.sphere_pos[i] = -cube_half_size + self.sphere_radius

    def run(self):
        last_time = glfw.get_time()
        
        while not glfw.window_should_close(self.window):
            # Calculate delta time
            current_time = glfw.get_time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # Process input
            glfw.poll_events()
            
            # Update
            self._update_sphere_position()
            
            # Render
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # View matrix (camera)
            view = Matrix44.look_at(
                self.camera_pos,
                self.camera_pos + self.camera_front,
                self.camera_up
            )
            glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, view)
            
            # Draw cube
            cube_model = Matrix44.identity()
            glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, cube_model)
            glBindVertexArray(self.cube_vao)
            glDrawElements(GL_TRIANGLES, len(self.cube_indices), GL_UNSIGNED_INT, None)
            
            # Draw sphere
            sphere_model = Matrix44.from_translation(self.sphere_pos)
            glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, sphere_model)
            glBindVertexArray(self.sphere_vao)
            glDrawElements(GL_TRIANGLES, len(self.sphere_indices), GL_UNSIGNED_INT, None)
            
            # Swap buffers
            glfw.swap_buffers(self.window)

    def __del__(self):
        glfw.terminate()

if __name__ == "__main__":
    simulation = SphereInCubeSimulation()
    simulation.run()