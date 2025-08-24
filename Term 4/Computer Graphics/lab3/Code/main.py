import glfw
from OpenGL.GL import *
from math import cos, sin, pi

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

# Функция для создания эллиптического тора
def draw_elliptical_torus(R, r, num_major, num_minor):
    for i in range(num_major):
        theta1 = i * 2 * pi / num_major
        theta2 = (i + 1) * 2 * pi / num_major
        
        glBegin(GL_QUAD_STRIP)
        for j in range(num_minor + 1):
            phi = j * 2 * pi / num_minor
            for theta in [theta1, theta2]:
                x = (R + r * cos(phi)) * cos(theta)
                y = (R + r * cos(phi)) * sin(theta) * 1.8
                z = r * sin(phi)
                glVertex3f(x, y, z)
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
    # Отрисовка эллиптического тора
    glColor3f(0.2, 0.7, 1.0)
    draw_elliptical_torus(1.0, 0.3, 40, 20)

    # Draw rotating cube
    # Apply transformations
    glLoadIdentity()
    glTranslatef(*translateVec)
    glScalef(*scaleVec)
    apply_isometric_projection()  # Apply isometric projection

    glRotatef(angle_x, 1, 0, 0)  # Rotate along X-axis
    glRotatef(angle_y, 0, 1, 0)  # Rotate along Y-axis
    # Отрисовка эллиптического тора
    glColor3f(0.8, 0.1, 1.0) 
    draw_elliptical_torus(1.0, 0.3, 40, 20)

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
