import glfw
from OpenGL.GL import *
from math import cos, sin, radians

# Parameters for rotation, scaling, translation
delta = 0.1
old_delta = 0
angle_x, angle_y = 0, 0
scaleVec = [1, 1, 1]
scaleRatio = 0.1
translateVec = [0, 0, 0]  # Start with translation along Z-axis (for perspective)
translateRatio = 0.1
wireframe = False  # Mode switch

# Rotation matrix for isometric projection
def apply_isometric_projection():
    glRotatef(35.264, 1, 0, 0)  # Rotate 35.264 degrees along X-axis
    glRotatef(45, 0, 1, 0)      # Rotate 45 degrees along Y-axis

def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 600, "Isometric Cube", None, None)
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

def draw_cube():
    # Colors for each face
    face_colors = [
        [1.0, 0.0, 0.0],  # Red: back face
        [0.0, 1.0, 0.0],  # Green: front face (with hole)
        [0.0, 0.0, 1.0],  # Blue: left face
        [1.0, 1.0, 0.0],  # Yellow: right face
        [1.0, 0.0, 1.0],  # Magenta: top face
        [0.0, 1.0, 1.0],  # Cyan: bottom face
    ]
    
    # Vertices of the cube
    vertices = [
        [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5], # Back face
        [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]    # Front face
    ]
    
    if wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Back face (red)
    glBegin(GL_QUADS)
    glColor3fv(face_colors[0])
    glVertex3fv(vertices[0])
    glVertex3fv(vertices[1])
    glVertex3fv(vertices[2])
    glVertex3fv(vertices[3])
    glEnd()

    # Front face (green) with hole
    glBegin(GL_QUADS)
    glColor3fv(face_colors[1])
    # Outer vertices of the front face, excluding the center (creating a hole)
    glVertex3fv(vertices[4])
    glVertex3fv([0.2, -0.5, 0.5])  # Break here for hole
    glVertex3fv([0.2, 0.5, 0.5])
    glVertex3fv(vertices[7])

    glVertex3fv([0.2, 0.5, 0.5])
    glVertex3fv([0.5, 0.5, 0.5])
    glVertex3fv([0.5, 0.2, 0.5])
    glVertex3fv([0.2, 0.2, 0.5])

    glVertex3fv([0.5, 0.2, 0.5])
    glVertex3fv([0.5, -0.2, 0.5])
    glVertex3fv([0.2, -0.2, 0.5])
    glVertex3fv([0.2, 0.2, 0.5])

    glVertex3fv([0.5, -0.2, 0.5])
    glVertex3fv([0.5, -0.5, 0.5])
    glVertex3fv([0.2, -0.5, 0.5])
    glVertex3fv([0.2, -0.2, 0.5])
    glEnd()

    # Left face (blue)
    glBegin(GL_QUADS)
    glColor3fv(face_colors[2])
    glVertex3fv(vertices[0])
    glVertex3fv(vertices[3])
    glVertex3fv(vertices[7])
    glVertex3fv(vertices[4])
    glEnd()

    # Right face (yellow)
    glBegin(GL_QUADS)
    glColor3fv(face_colors[3])
    glVertex3fv(vertices[1])
    glVertex3fv(vertices[2])
    glVertex3fv(vertices[6])
    glVertex3fv(vertices[5])
    glEnd()

    # Top face (magenta)
    glBegin(GL_QUADS)
    glColor3fv(face_colors[4])
    glVertex3fv(vertices[3])
    glVertex3fv(vertices[2])
    glVertex3fv(vertices[6])
    glVertex3fv(vertices[7])
    glEnd()

    # Bottom face (cyan)
    glBegin(GL_QUADS)
    glColor3fv(face_colors[5])
    glVertex3fv(vertices[0])
    glVertex3fv(vertices[1])
    glVertex3fv(vertices[5])
    glVertex3fv(vertices[4])
    glEnd()

def display(window):
    global angle_x, angle_y
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    # glClearColor(1.0, 1.0, 1.0, 1.0)

    # Apply transformations
    glTranslatef(*translateVec)
    glScalef(*scaleVec)
    apply_isometric_projection()  # Apply isometric projection

    glRotatef(angle_x, 1, 0, 0)  # Rotate along X-axis
    glRotatef(angle_y, 0, 1, 0)  # Rotate along Y-axis

    draw_cube()

    glfw.swap_buffers(window)
    glfw.poll_events()

def key_callback(window, key, scancode, action, mods):
    global delta, old_delta, angle_x, angle_y
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
            scaleVec[0] += scaleRatio
            scaleVec[1] += scaleRatio
            scaleVec[2] += scaleRatio
        if key == glfw.KEY_X:
            scaleVec[0] -= scaleRatio
            scaleVec[1] -= scaleRatio
            scaleVec[2] -= scaleRatio

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
    scaleVec[0] += yoffset * scaleRatio
    scaleVec[1] += yoffset * scaleRatio
    scaleVec[2] += yoffset * scaleRatio

if __name__ == "__main__":
    main()
