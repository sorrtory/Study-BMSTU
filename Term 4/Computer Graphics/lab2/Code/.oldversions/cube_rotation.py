import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Cube vertices
vertices = [
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),  # front
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)       # back
]

# Cube edges
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # front edges
    (4, 5), (5, 6), (6, 7), (7, 4),  # back edges
    (0, 4), (1, 5), (2, 6), (3, 7)   # connecting edges
]

# Initial rotation angles

rot_x = 0
rot_y = 0

# Function to initialize OpenGL
def initialize_opengl(width, height):
    if not glfw.init():
        return None
    window = glfw.create_window(width, height, "Cube", None, None)
    if not window:
        glfw.terminate()
        return None
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    return window

# Function to draw the cube
def draw_cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

# Function to handle key input for rotation
def key_callback(window, key, scancode, action, mods):
    global rot_x, rot_y

    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_LEFT:
            rot_y -= 5  # Rotate left
        elif key == glfw.KEY_RIGHT:
            rot_y += 5  # Rotate right
        elif key == glfw.KEY_UP:
            rot_x -= 5  # Rotate up
        elif key == glfw.KEY_DOWN:
            rot_x += 5  # Rotate down

# Main function
def main():
    width, height = 800, 600
    window = initialize_opengl(width, height)
    if not window:
        return

    # Set the key callback function
    glfw.set_key_callback(window, key_callback)

    # Main rendering loop
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set up camera
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)

        # Apply rotation based on user input
        glRotatef(rot_x, 1, 0, 0)  # Rotate around the x-axis
        glRotatef(rot_y, 0, 1, 0)  # Rotate around the y-axis

        # Draw the cube
        draw_cube()

        # Swap buffers to display the rendered content
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
