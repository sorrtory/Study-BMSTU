import glfw
from OpenGL.GL import *
from math import cos, sin, radians

# Parameters for rotation, scaling, translation
angle_x, angle_y = 0, 0
scaleVec = [0.5, 0.5, 0.5]
translateVec = [0, 0, 0]
translateRatio = 0.1
wireframe = False  # Mode switch


# Rotation matrix for isometric projection
def apply_isometric_projection():
    glRotatef(35.264, 1, 0, 0)  # Rotate 35.264 degrees along X-axis
    glRotatef(45, 0, 1, 0)      # Rotate 45 degrees along Y-axis


def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 800, "Isometric Cube", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    glEnable(GL_DEPTH_TEST)

    while not glfw.window_should_close(window):
        display(window)
    glfw.destroy_window(window)
    glfw.terminate()

# Define cube using edges and colors for each face
def draw_cube():
    # Colors for each face
    face_colors = [
        [1.0, 0.0, 0.0],  # Red: back face
        [0.0, 1.0, 0.0],  # Green: front face
        [0.0, 0.0, 1.0],  # Blue: left face
        [1.0, 1.0, 0.0],  # Yellow: right face
        [1.0, 0.0, 1.0],  # Magenta: top face
        [0.0, 1.0, 1.0],  # Cyan: bottom face
    ]

    # Vertices of the cube (edge list)
    vertices = [
        # Back face
        [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
        # Front face
        [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]
    ]

    # Faces of the cube (each face is a set of 4 vertices, with colors)
    faces = [
        [0, 1, 2, 3],  # Back face
        [4, 5, 6, 7],  # Front face
        [0, 4, 7, 3],  # Left face
        [1, 5, 6, 2],  # Right face
        [3, 2, 6, 7],  # Top face
        [0, 1, 5, 4]   # Bottom face
    ]

    if wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Draw the cube
    for i, face in enumerate(faces):
        glBegin(GL_QUADS)
        glColor3fv(face_colors[i])  # Set color for the face
        for vertex in face:
            glVertex3fv(vertices[vertex])
        glEnd()


def display(window):
    global angle_x, angle_y
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # glClearColor(1.0, 1.0, 1.0, 1.0)

    # Draw static cube
    glLoadIdentity()
    apply_isometric_projection()  # Apply isometric projection
    glTranslatef(1, 0, 0)         # Move static cube to the left
    glScalef(*scaleVec)
    draw_cube()

    # Draw rotating cube
    # Apply transformations
    glLoadIdentity()
    glTranslatef(*translateVec)
    glScalef(*scaleVec)
    apply_isometric_projection()  # Apply isometric projection

    glRotatef(angle_x, 1, 0, 0)  # Rotate along X-axis
    glRotatef(angle_y, 0, 1, 0)  # Rotate along Y-axis
    draw_cube()

    glfw.swap_buffers(window)
    glfw.poll_events()


def key_callback(window, key, scancode, action, mods):
    global angle_x, angle_y
    global translateVec, scaleVec, wireframe

    if action == glfw.PRESS or action == glfw.REPEAT:
        # Cube rotation
        if key == glfw.KEY_RIGHT:
            angle_y -= 3
        if key == glfw.KEY_LEFT:
            angle_y += 3
        if key == glfw.KEY_UP:
            angle_x -= 3
        if key == glfw.KEY_DOWN:
            angle_x += 3

        # Translation (Move by X, Y, Z)
        if key == glfw.KEY_W:
            translateVec[1] += translateRatio
        if key == glfw.KEY_S:
            translateVec[1] -= translateRatio
        if key == glfw.KEY_A:
            translateVec[0] -= translateRatio
        if key == glfw.KEY_D:
            translateVec[0] += translateRatio
        if key == glfw.KEY_Q:
            translateVec[2] += translateRatio  # Move forward
        if key == glfw.KEY_E:
            translateVec[2] -= translateRatio  # Move backward

        # Scaling
        if key == glfw.KEY_Z:
            scaleVec[0] += 0.1
            scaleVec[1] += 0.1
            scaleVec[2] += 0.1
        if key == glfw.KEY_X:
            scaleVec[0] -= 0.1
            scaleVec[1] -= 0.1
            scaleVec[2] -= 0.1

        # Toggle between wireframe and solid
        if key == glfw.KEY_M:
            wireframe = not wireframe
            if wireframe:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # Close window
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, 1)


def scroll_callback(window, xoffset, yoffset):
    global scaleVec
    scaleVec[0] += yoffset * 0.1
    scaleVec[1] += yoffset * 0.1
    scaleVec[2] += yoffset * 0.1


if __name__ == "__main__":
    main()
