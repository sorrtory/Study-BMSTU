import glfw
from OpenGL.GL import *
from math import cos, sin, pi
from PIL import Image

# Глобальные параметры
angle_x, angle_y = 0, 0
scaleVec = [1, 1, 1]
translateVec = [0, 0, 0]
velocity = [0.005, 0.006, 0.007]
bounds_min = [-1.0, -1.0, -1.0]
bounds_max = [1.0, 1.0, 1.0]
texture_id = None
wireframe = False
use_texture = True
animation = True

Torus_R = 0.5
Torus_r = 0.2

# Освещение
light_presets = [
    ([-1, -1, 1, 0], [0.1, 0.1, 0.1, 1], [1, 1, 1, 1], [1, 1, 1, 1]),
    ([0, 1, 0, 0], [0.1, 0.1, 0.1, 1], [1, 0, 0, 1], [1, 1, 1, 1]),
    ([1, 0, 0, 0], [0.2, 0.2, 0.2, 1], [0, 1, 0, 1], [1, 1, 1, 1]),
    ([0, 0, 1, 0], [0.05, 0.05, 0.05, 1], [0, 0, 1, 1], [1, 1, 1, 1]),
    ([1, 1, 0, 0], [0.05, 0.05, 0.05, 1], [1, 0.5, 0, 1], [1, 1, 1, 1]),
]
light_index = 0

material_ambient = [0.3, 0.2, 0.2, 1.0]
material_diffuse = [0.8, 0.5, 0.3, 1.0]
material_specular = [1.0, 1.0, 1.0, 1.0]
material_shininess = 80.0
global_ambient = [0.05, 0.05, 0.05, 1.0]

def apply_isometric_projection():
    glRotatef(35.264, 1, 0, 0)
    glRotatef(45, 0, 1, 0)

def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    pos, amb, diff, spec = light_presets[light_index]
    
    # Change own color
    glLightfv(GL_LIGHT0, GL_POSITION, pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, amb)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diff)
    glLightfv(GL_LIGHT0, GL_SPECULAR, spec)

    # Set global ambient light
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
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    glColor3f(1, 0, 0); glVertex3f(0, 0, 0); glVertex3f(0.5, 0, 0)
    glColor3f(0, 1, 0); glVertex3f(0, 0, 0); glVertex3f(0, 0.5, 0)
    glColor3f(0, 0, 1); glVertex3f(0, 0, 0); glVertex3f(0, 0, 0.5)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_bounds():
    glDisable(GL_LIGHTING)
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    # Draw edges of the bounding box
    for x in [bounds_min[0], bounds_max[0]]:
        for y in [bounds_min[1], bounds_max[1]]:
            for z in [bounds_min[2], bounds_max[2]]:
                glVertex3f(x, y, bounds_min[2])
                glVertex3f(x, y, bounds_max[2])
                glVertex3f(x, bounds_min[1], z)
                glVertex3f(x, bounds_max[1], z)
                glVertex3f(bounds_min[0], y, z)
                glVertex3f(bounds_max[0], y, z)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_light_marker():
    glDisable(GL_LIGHTING)
    glPointSize(12)
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 0.0)
    pos = light_presets[light_index][0]
    glVertex3f(pos[0], pos[1], pos[2])
    glEnd()
    glEnable(GL_LIGHTING)

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

def update_bounds(ratio):
    global bounds_min, bounds_max, scaleVec
    ratio_min = -ratio
    ratio_max = ratio

    bounds_min = [b + ratio_min for b in bounds_min]
    bounds_max = [b + ratio_max for b in bounds_max]

def animate_torus():
    global translateVec, velocity, bounds_min, bounds_max
    for i in range(3):
        translateVec[i] += velocity[i]
        # Check for collision with bounds and reverse velocity if needed
        torus_min = bounds_min[i] + Torus_r * 2
        torus_max = bounds_max[i] - Torus_r * 2
        if translateVec[i] < torus_min or translateVec[i] > torus_max:
            velocity[i] = -velocity[i]
            translateVec[i] = max(min(translateVec[i], torus_max), torus_min)

def display(window):
    global translateVec
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()    

    if animation:
        animate_torus()

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
    draw_elliptical_torus(Torus_R, Torus_r, 40, 20)
    glPopMatrix()

    # --- Bounds
    draw_light_marker()
    glPushMatrix()
    apply_isometric_projection()
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    draw_axes()
    draw_bounds()
    glPopMatrix()

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
            update_bounds(0.1)
        if key == glfw.KEY_X:
            scaleVec = [v - 0.1 for v in scaleVec]
            update_bounds(-0.1)
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
