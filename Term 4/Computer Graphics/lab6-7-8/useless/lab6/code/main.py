import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *           # sudo apt-get install mesa-utils
from math import cos, sin, pi, sqrt
from PIL import Image
import numpy as np

# Global parameters
angle_x, angle_y = 0, 0
scaleVec = [1.0, 1.0, 1.0]
translateVec = [0.0, 0.0, 0.0]
velocity = [0.005, 0.006, 0.007]
bounds_min = [-1.0, -1.0, -1.0]
bounds_max = [1.0, 1.0, 1.0]
texture_id = None
wireframe = False
use_texture = True
animation = True
show_axes = True
show_bounds = True

# Torus parameters
Torus_R = 0.5  # Major radius
Torus_r = 0.2  # Minor radius

# Lighting configuration
light_presets = [
    # Format: (position, ambient, diffuse, specular, light_model_ambient)
    # Preset 0: Natural daylight
    ([1.0, 1.0, 1.0, 0],  # Directional light from top-right-front
     [0.1, 0.1, 0.1, 1.0],  # Ambient
     [0.9, 0.9, 0.8, 1.0],  # Diffuse (slightly warm)
     [1.0, 1.0, 1.0, 1.0],  # Specular
     [0.2, 0.2, 0.2, 1.0]),  # Global ambient

    # Preset 1: Studio lighting
    ([0.5, 1.0, 0.7, 0],
     [0.15, 0.15, 0.15, 1.0],
     [0.8, 0.8, 0.8, 1.0],
     [1.0, 1.0, 1.0, 1.0],
     [0.15, 0.15, 0.15, 1.0]),

    # Preset 2: Warm sunset
    ([0.8, 0.3, -0.5, 0],
     [0.2, 0.1, 0.1, 1.0],
     [0.9, 0.6, 0.4, 1.0],
     [1.0, 0.8, 0.6, 1.0],
     [0.15, 0.1, 0.1, 1.0]),

    # Preset 3: Cool blue
    ([-0.5, 0.5, 1.0, 0],
     [0.05, 0.05, 0.1, 1.0],
     [0.5, 0.5, 0.9, 1.0],
     [0.8, 0.8, 1.0, 1.0],
     [0.05, 0.05, 0.1, 1.0]),

    # Preset 4: Point light
    ([0.0, 0.0, 1.0, 1],  # Positional light
     [0.05, 0.05, 0.05, 1.0],
     [0.9, 0.9, 0.9, 1.0],
     [1.0, 1.0, 1.0, 1.0],
     [0.1, 0.1, 0.1, 1.0])
]

light_index = 0

# Material properties
material_presets = [
    # Brass-like
    [0.33, 0.22, 0.03, 1.0],  # Ambient
    [0.78, 0.57, 0.11, 1.0],  # Diffuse
    [0.99, 0.91, 0.81, 1.0],  # Specular
    27.8,                     # Shininess

    # Red plastic
    [0.3, 0.0, 0.0, 1.0],
    [0.6, 0.1, 0.1, 1.0],
    [0.8, 0.6, 0.6, 1.0],
    32.0,

    # Emerald
    [0.0215, 0.1745, 0.0215, 1.0],
    [0.07568, 0.61424, 0.07568, 1.0],
    [0.633, 0.727811, 0.633, 1.0],
    76.8
]

material_index = 0


def get_material_properties():
    offset = material_index * 4
    return (
        material_presets[offset],
        material_presets[offset + 1],
        material_presets[offset + 2],
        material_presets[offset + 3]
    )


def apply_isometric_projection():
    glRotatef(35.264, 1, 0, 0)
    glRotatef(45, 0, 1, 0)


def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Get current light configuration
    pos, amb, diff, spec, global_amb = light_presets[light_index]

    # Set up light 0 (main light)
    glLightfv(GL_LIGHT0, GL_POSITION, pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, amb)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diff)
    glLightfv(GL_LIGHT0, GL_SPECULAR, spec)

    # Set global ambient light
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, global_amb)

    # Set material properties
    mat_amb, mat_diff, mat_spec, mat_shininess = get_material_properties()
    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_amb)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diff)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_spec)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)


def load_texture(path='texture.bmp'):
    global texture_id
    try:
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_data = np.array(list(img.getdata()), np.uint8)
    except Exception as e:
        print(f"Texture loading failed: {e}")
        # Create a procedural texture as fallback
        width, height = 64, 64
        img_data = np.zeros((width, height, 3), dtype=np.uint8)
        for i in range(width):
            for j in range(height):
                img_data[i][j] = [(i ^ j) & 0xFF, (i * j)
                                  & 0xFF, (i + j) & 0xFF]
        img_data = img_data.flatten()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)


def draw_axes():
    if not show_axes:
        return

    glDisable(GL_LIGHTING)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # X axis (red)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0.5, 0, 0)
    # Y axis (green)
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0.5, 0)
    # Z axis (blue)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 0.5)
    glEnd()

    # Draw axis labels
    glRasterPos3f(0.55, 0, 0)
    glColor3f(1, 0, 0)
    for c in "X":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

    glRasterPos3f(0, 0.55, 0)
    glColor3f(0, 1, 0)
    for c in "Y":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

    glRasterPos3f(0, 0, 0.55)
    glColor3f(0, 0, 1)
    for c in "Z":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

    glEnable(GL_LIGHTING)


def draw_bounds():
    if not show_bounds:
        return

    glDisable(GL_LIGHTING)
    glColor3f(0.7, 0.7, 0.7)
    glLineWidth(1.0)
    glBegin(GL_LINES)

    # Draw the bounding box edges
    for x in [bounds_min[0], bounds_max[0]]:
        for y in [bounds_min[1], bounds_max[1]]:
            glVertex3f(x, y, bounds_min[2])
            glVertex3f(x, y, bounds_max[2])

    for x in [bounds_min[0], bounds_max[0]]:
        for z in [bounds_min[2], bounds_max[2]]:
            glVertex3f(x, bounds_min[1], z)
            glVertex3f(x, bounds_max[1], z)

    for y in [bounds_min[1], bounds_max[1]]:
        for z in [bounds_min[2], bounds_max[2]]:
            glVertex3f(bounds_min[0], y, z)
            glVertex3f(bounds_max[0], y, z)

    glEnd()
    glEnable(GL_LIGHTING)


def draw_light_marker():
    glDisable(GL_LIGHTING)
    glPointSize(10)
    glBegin(GL_POINTS)
    pos = light_presets[light_index][0]
    if pos[3] == 0:  # Directional light
        glColor3f(1.0, 1.0, 0.0)  # Yellow
    else:  # Positional light
        glColor3f(1.0, 0.5, 0.0)  # Orange
    glVertex3f(pos[0], pos[1], pos[2])
    glEnd()
    glEnable(GL_LIGHTING)


def draw_elliptical_torus(R, r, num_major=40, num_minor=20):
    for i in range(num_major):
        theta1 = i * 2 * pi / num_major
        theta2 = (i + 1) * 2 * pi / num_major
        glBegin(GL_QUAD_STRIP)
        for j in range(num_minor + 1):
            phi = j * 2 * pi / num_minor
            for theta in [theta1, theta2]:
                cos_phi = cos(phi)
                sin_phi = sin(phi)
                cos_theta = cos(theta)
                sin_theta = sin(theta)

                # Vertex position
                x = (R + r * cos_phi) * cos_theta
                y = (R + r * cos_phi) * sin_theta * 1.5  # Elliptical shape
                z = r * sin_phi

                # Normal vector
                nx = cos_phi * cos_theta
                ny = cos_phi * sin_theta * 1.5
                nz = sin_phi
                norm = sqrt(nx*nx + ny*ny + nz*nz)
                nx /= norm
                ny /= norm
                nz /= norm

                glNormal3f(nx, ny, nz)
                if use_texture:
                    glTexCoord2f(theta / (2 * pi), phi / (2 * pi))
                glVertex3f(x, y, z)
        glEnd()


def update_bounds(ratio):
    global bounds_min, bounds_max
    bounds_min = [b * (1 + ratio) for b in bounds_min]
    bounds_max = [b * (1 + ratio) for b in bounds_max]


def animate_torus():
    global translateVec, velocity

    # Calculate the effective collision radius (major radius + minor radius)
    collision_radius = Torus_R + Torus_r

    # Update position
    for i in range(3):
        translateVec[i] += velocity[i]

        if is_torus_colliding_with_bounds():
            # Reverse velocity if collision detected
            velocity[i] = -velocity[i]
            # Adjust position to prevent sticking
            translateVec[i] = max(bounds_min[i] + collision_radius,
                                  min(translateVec[i], bounds_max[i] - collision_radius))


def is_torus_colliding_with_bounds():
    """Check if torus is colliding with any of the bounding box faces"""
    collision_radius = Torus_R + Torus_r

    # Check collision with each axis
    collisions = [False, False, False]

    for i in range(3):
        if translateVec[i] - collision_radius <= bounds_min[i]:
            collisions[i] = True
        if translateVec[i] + collision_radius >= bounds_max[i]:
            collisions[i] = True

    return any(collisions)


def display(window):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if animation:
        animate_torus()

    # Draw torus
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

    # Set material color (without texture)
    if not use_texture or not texture_id:
        glColor3f(0.8, 0.6, 0.4)

    draw_elliptical_torus(Torus_R, Torus_r)
    glPopMatrix()

    # Draw scene elements
    glPushMatrix()
    apply_isometric_projection()
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    draw_axes()
    draw_bounds()
    draw_light_marker()
    glPopMatrix()

    glfw.swap_buffers(window)
    glfw.poll_events()


def key_callback(window, key, scancode, action, mods):
    global angle_x, angle_y, translateVec, scaleVec
    global wireframe, use_texture, animation, velocity
    global light_index, material_index, show_axes, show_bounds

    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_SPACE:
            animation = not animation
        elif key == glfw.KEY_RIGHT:
            angle_y -= 3
        elif key == glfw.KEY_LEFT:
            angle_y += 3
        elif key == glfw.KEY_UP:
            angle_x -= 3
        elif key == glfw.KEY_DOWN:
            angle_x += 3
        elif key == glfw.KEY_W:
            translateVec[1] += 0.1
        elif key == glfw.KEY_S:
            translateVec[1] -= 0.1
        elif key == glfw.KEY_A:
            translateVec[0] -= 0.1
        elif key == glfw.KEY_D:
            translateVec[0] += 0.1
        elif key == glfw.KEY_Q:
            translateVec[2] += 0.1
        elif key == glfw.KEY_E:
            translateVec[2] -= 0.1
        elif key == glfw.KEY_Z:
            scaleVec = [v * 1.1 for v in scaleVec]
            update_bounds(0.1)
        elif key == glfw.KEY_X:
            scaleVec = [v * 0.9 for v in scaleVec]
            update_bounds(-0.1)
        elif key == glfw.KEY_M:
            wireframe = not wireframe
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)
        elif key == glfw.KEY_T:
            use_texture = not use_texture
        elif key == glfw.KEY_EQUAL:
            velocity = [v * 1.1 for v in velocity]
        elif key == glfw.KEY_MINUS:
            velocity = [v * 0.9 for v in velocity]
        elif key == glfw.KEY_1:
            light_index = 0
        elif key == glfw.KEY_2:
            light_index = 1
        elif key == glfw.KEY_3:
            light_index = 2
        elif key == glfw.KEY_4:
            light_index = 3
        elif key == glfw.KEY_5:
            light_index = 4
        elif key == glfw.KEY_6:
            material_index = 0
        elif key == glfw.KEY_7:
            material_index = 1
        elif key == glfw.KEY_8:
            material_index = 2
        elif key == glfw.KEY_B:
            show_bounds = not show_bounds
        elif key == glfw.KEY_V:
            show_axes = not show_axes
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def scroll_callback(window, xoffset, yoffset):
    global scaleVec
    factor = 1.1 if yoffset > 0 else 0.9
    scaleVec = [v * factor for v in scaleVec]
    update_bounds(factor - 1)


def main():
    if not glfw.init():
        return

    # Initialize GLUT
    glutInit()  # Required for GLUT functions like glutBitmapCharacter

    window = glfw.create_window(800, 800, "Enhanced Torus Simulation", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # Initialize OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    # Load texture
    texture = __file__[:__file__.rfind("/")+1] + 'texture.bmp'
    load_texture(texture)

    # Main loop
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        display(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
