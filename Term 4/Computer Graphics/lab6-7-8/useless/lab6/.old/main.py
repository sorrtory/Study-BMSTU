import glfw
from OpenGL.GL import *
from math import cos, sin, pi
from PIL import Image

# Глобальные параметры
angle_x, angle_y = 0, 0
scaleVec = [0.5, 0.5, 0.5]
translateVec = [0, 0, 0]
velocity = [0.005, 0.006, 0.007]
bounds = [-0.5, 0.5]
texture_id = None
wireframe = False
use_texture = True
animation = False

# Освещение
light_presets = [
    ([1, 1, 1, 0], [0.2, 0.2, 0.2, 1], [1, 1, 1, 1], [1, 1, 1, 1]),
    ([0, 1, 0, 0], [0.1, 0.1, 0.1, 1], [1, 0, 0, 1], [1, 1, 1, 1]),
    ([1, 0, 0, 0], [0.2, 0.2, 0.2, 1], [0, 1, 0, 1], [1, 1, 1, 1]),
    ([0, 0, 1, 0], [0.1, 0.1, 0.1, 1], [0, 0, 1, 1], [1, 1, 1, 1]),
    ([1, 1, 0, 0], [0.3, 0.3, 0.3, 1], [1, 0.5, 0, 1], [1, 1, 1, 1]),
]
light_index = 0

material_ambient = [0.3, 0.2, 0.2, 1.0]
material_diffuse = [0.8, 0.5, 0.3, 1.0]
material_specular = [1.0, 1.0, 1.0, 1.0]
material_shininess = 80.0
global_ambient = [0.1, 0.1, 0.1, 1.0]


def apply_isometric_projection():
    glRotatef(35.264, 1, 0, 0)
    glRotatef(45, 0, 1, 0)


def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    pos, amb, diff, spec = light_presets[light_index]
    glLightfv(GL_LIGHT0, GL_POSITION, pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, amb)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diff)
    glLightfv(GL_LIGHT0, GL_SPECULAR, spec)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, global_ambient)
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, material_shininess)


def load_texture(path='texture.bmp'):
    global texture_id
    try:
        img = Image.open(path).convert('L')
    except Exception as e:
        print("Texture loading failed:", e)
        return

    width, height = img.size
    img_data = img.tobytes()
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, width, height, 0,
                 GL_LUMINANCE, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


def draw_axes():
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(1, 0, 0)
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 1, 0)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 1)
    glEnd()


def draw_bounds():
    glColor3f(1, 1, 0)
    glBegin(GL_LINES)
    for x in bounds:
        for y in bounds:
            glVertex3f(x, y, bounds[0])
            glVertex3f(x, y, bounds[1])
    for x in bounds:
        for z in bounds:
            glVertex3f(x, bounds[0], z)
            glVertex3f(x, bounds[1], z)
    for y in bounds:
        for z in bounds:
            glVertex3f(bounds[0], y, z)
            glVertex3f(bounds[1], y, z)
    glEnd()


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

                nx = cos_phi * cos_theta
                ny = cos_phi * sin_theta * 1.8
                nz = sin_phi
                glNormal3f(nx, ny, nz)

                if use_texture:
                    glTexCoord2f(theta / (2 * pi), phi / (2 * pi))
                glVertex3f(x, y, z)
        glEnd()


def display(window):
    global translateVec

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if animation:
        for i in range(3):
            translateVec[i] += velocity[i]
            if translateVec[i] > bounds[1] or translateVec[i] < bounds[0]:
                velocity[i] = -velocity[i]

    glPushMatrix()
    glTranslatef(*translateVec)
    glScalef(*scaleVec)
    apply_isometric_projection()
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    setup_lighting()

    if use_texture and texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
    else:
        glDisable(GL_TEXTURE_2D)

    glColor3f(1.0, 1.0, 1.0)
    draw_elliptical_torus(1.0, 0.3, 40, 20)
    glPopMatrix()

    draw_axes()
    draw_bounds()

    glfw.swap_buffers(window)
    glfw.poll_events()


def key_callback(window, key, scancode, action, mods):
    global angle_x, angle_y, translateVec, scaleVec
    global wireframe, use_texture, animation, velocity, light_index

    if action in [glfw.PRESS, glfw.REPEAT]:
        if key == glfw.KEY_SPACE:
            animation = not animation
        if key == glfw.KEY_RIGHT:
            angle_y -= 3
        if key == glfw.KEY_LEFT:
            angle_y += 3
        if key == glfw.KEY_UP:
            angle_x -= 3
        if key == glfw.KEY_DOWN:
            angle_x += 3
        if key == glfw.KEY_W:
            translateVec[1] += 0.1
        if key == glfw.KEY_S:
            translateVec[1] -= 0.1
        if key == glfw.KEY_A:
            translateVec[0] -= 0.1
        if key == glfw.KEY_D:
            translateVec[0] += 0.1
        if key == glfw.KEY_Q:
            translateVec[2] += 0.1
        if key == glfw.KEY_E:
            translateVec[2] -= 0.1
        if key == glfw.KEY_Z:
            scaleVec = [v + 0.1 for v in scaleVec]
        if key == glfw.KEY_X:
            scaleVec = [v - 0.1 for v in scaleVec]
        if key == glfw.KEY_M:
            wireframe = not wireframe
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)
        if key == glfw.KEY_T:
            use_texture = not use_texture
        if key == glfw.KEY_EQUAL:
            velocity = [v * 1.1 for v in velocity]
        if key == glfw.KEY_MINUS:
            velocity = [v * 0.9 for v in velocity]
        if key in [glfw.KEY_1, glfw.KEY_2, glfw.KEY_3, glfw.KEY_4, glfw.KEY_5]:
            light_index = key - glfw.KEY_1
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def scroll_callback(window, xoffset, yoffset):
    for i in range(3):
        scaleVec[i] += yoffset * 0.1


def main():
    if not glfw.init():
        return
    window = glfw.create_window(800, 800, "Realistic Torus", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    glEnable(GL_DEPTH_TEST)
    load_texture("texture.bmp")

    while not glfw.window_should_close(window):
        display(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
