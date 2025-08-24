import glfw
from OpenGL.GL import *
from math import cos, sin, pi
from PIL import Image

use_texture = False
texture_id = None


velocity = [0.01, 0.012, 0.015]
bounds = [-1.5, 1.5]


# Parameters for rotation, scaling, translation
angle_x, angle_y = 0, 0
scaleVec = [0.5, 0.5, 0.5]
translateVec = [0, 0, 0]
translateRatio = 0.1
wireframe = False  # Mode switch

# Adjusted Lighting properties for more dynamic appearance
light_position = [1.0, 1.0, 1.0, 0.0]  # Directional light
light_ambient = [0.2, 0.2, 0.2, 1.0]   # Reduced ambient light intensity
light_diffuse = [1.0, 0.8, 0.6, 1.0]   # Warmer diffuse light intensity
light_specular = [1.0, 1.0, 1.0, 1.0]  # Stronger specular light intensity for highlights

# Adjusted Material properties for better color reflection
material_ambient = [0.3, 0.2, 0.2, 1.0]  # Slightly reddish ambient reflectivity
material_diffuse = [0.8, 0.5, 0.3, 1.0]  # Warmer diffuse reflectivity
material_specular = [1.0, 1.0, 1.0, 1.0] # Stronger specular reflectivity for highlights
material_shininess = 80.0                # Sharper and more focused highlights

# Global lighting model
global_ambient = [0.1, 0.1, 0.1, 1.0]    # Global ambient light

# Rotation matrix for isometric projection
def apply_isometric_projection():
    glRotatef(35.264, 1, 0, 0)  # Rotate 35.264 degrees along X-axis
    glRotatef(45, 0, 1, 0)      # Rotate 45 degrees along Y-axis

def setup_lighting():
    # Enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Set light source properties
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    # Set global ambient light
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, global_ambient)

    # Set material properties
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, material_shininess)

def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 800, "Isometric Torus", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glEnable(GL_DEPTH_TEST)
    setup_lighting()  # Initialize lighting
    # glEnable(GL_TEXTURE_2D)
    # load_texture()

    while not glfw.window_should_close(window):
        display(window)
    glfw.destroy_window(window)
    glfw.terminate()


def load_texture(path='texture.bmp'):
    global texture_id
    img = Image.open(path)
    img_data = img.convert("RGB").tobytes()
    width, height = img.size

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

# Функция для создания эллиптического тора
def draw_elliptical_torus(R, r, num_major, num_minor):
    for i in range(num_major):
        theta1 = i * 2 * pi / num_major
        theta2 = (i + 1) * 2 * pi / num_major

        glBegin(GL_QUAD_STRIP)
        for j in range(num_minor + 1):
            phi = j * 2 * pi / num_minor
            for theta in [theta1, theta2]:
                cos_phi, sin_phi = cos(phi), sin(phi)
                cos_theta, sin_theta = cos(theta), sin(theta)

                x = (R + r * cos_phi) * cos_theta
                y = (R + r * cos_phi) * sin_theta * 1.8
                z = r * sin_phi

                # Нормаль (направление от центра тора к поверхности)
                nx = cos_phi * cos_theta
                ny = cos_phi * sin_theta * 1.8
                nz = sin_phi
                glNormal3f(nx, ny, nz)

                if use_texture:
                    glTexCoord2f(theta / (2 * pi), phi / (2 * pi))
                glVertex3f(x, y, z)
        glEnd()



def display(window):
    global angle_x, angle_y
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # glClearColor(1.0, 1.0, 1.0, 1.0)

    if use_texture:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
    else:
        glDisable(GL_TEXTURE_2D)

    for i in range(3):
        translateVec[i] += velocity[i]
        if translateVec[i] > bounds[1] or translateVec[i] < bounds[0]:
            velocity[i] = -velocity[i]  # Отражение

    # # Draw static cube
    # glLoadIdentity()
    # apply_isometric_projection()  # Apply isometric projection
    # glTranslatef(1, 0, 0)         # Move static cube to the left
    # glScalef(*scaleVec)
    # # Отрисовка эллиптического тора
    # glColor3f(0.2, 0.7, 1.0)
    # draw_elliptical_torus(1.0, 0.3, 40, 20)

    # Draw rotating cube
    # Apply transformations
    glLoadIdentity()
    glTranslatef(*translateVec)
    glScalef(*scaleVec)
    apply_isometric_projection()  # Apply isometric projection

    glRotatef(angle_x, 1, 0, 0)  # Rotate along X-axis
    glRotatef(angle_y, 0, 1, 0)  # Rotate along Y-axis

    # Reset light position after transformations
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # Отрисовка эллиптического тора
    glColor3f(0.8, 0.1, 1.0) 
    draw_elliptical_torus(1.0, 0.3, 40, 20)


    

    glfw.swap_buffers(window)
    glfw.poll_events()


def key_callback(window, key, scancode, action, mods):
    global angle_x, angle_y
    global translateVec, scaleVec, wireframe
    global use_texture

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

        if key == glfw.KEY_T:
            use_texture = not use_texture

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
