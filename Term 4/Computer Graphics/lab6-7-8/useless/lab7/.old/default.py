# This program is a silly OpenGL app that renders torus in 3D space.
# User can manipulate the torus's position, rotation, and scale.
# Also there is a lighting system and a texture mapping.

import time
import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *  # Seems old. Need `sudo apt-get install mesa-utils`
# But canvas letters are too good to ignore
from OpenGL.GLU import *
from math import cos, sin, pi, sqrt
from PIL import Image
import numpy as np


class Angle:
    """
    Angles in degrees for rotation mod 360.
    """

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        self._update()

    @staticmethod
    def updated(angle, delta=0):
        angle += delta
        if angle >= 360:
            angle -= 360
        elif angle < 0:
            angle += 360
        return angle

    def _update(self):
        self.x = Angle.updated(self.x)
        self.y = Angle.updated(self.y)
        self.z = Angle.updated(self.z)

    def update_x(self, dx):
        self.x = Angle.updated(self.x, dx)

    def update_y(self, dy):
        self.y = Angle.updated(self.y, dy)

    def update_z(self, dz):
        self.z = Angle.updated(self.z, dz)

    def __add__(self, other):
        if isinstance(other, Angle):
            return Angle(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Angle):
            return Angle(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __str__(self):
        return f"Angle(x={self.x}, y={self.y})"

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise IndexError("Index out of range for Angle object.")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError("Index out of range for Angle object.")

    def __len__(self):
        return 3

    def __iter__(self):
        return iter((self.x, self.y, self.z))

### Configuration parameters ###


# Scene parameters
show_axes = True
scale = 0.8
animation = True
wireframe = False


# Bounding box parameters
show_bounds = True
bounds_min = [-1.0, -1.0, -1.0]
bounds_max = [1.0, 1.0, 1.0]
scene_Angle = Angle(35.264, 45)


# Torus properties
texture_id = None
use_texture = True
# Torus_default_color = [0.8, 0.6, 0.4]
Torus_default_color = [1.0, 0.1, 0.4]
Torus_Scale = [1.0, 1.0, 1.0]
Torus_Pos = [0.0, 0.0, 0.0]
Torus_Velocity = [0.005, 0.002, 0.007]
Torus_Angle = Angle(0, 0)  # Torus rotation angles
Torus_R = 0.2  # Major radius
Torus_r = 0.1  # Minor radius


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

# -- Unused but self-made rotations -


def rotation_matrix_x(angle):
    rad = np.radians(angle)
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(rad), -np.sin(rad), 0],
        [0, np.sin(rad), np.cos(rad), 0],
        [0, 0, 0, 1]
    ])


def rotation_matrix_y(angle):
    rad = np.radians(angle)
    return np.array([
        [np.cos(rad), 0, np.sin(rad), 0],
        [0, 1, 0, 0],
        [-np.sin(rad), 0, np.cos(rad), 0],
        [0, 0, 0, 1]
    ])


def rotate(object_Angle_X=0, object_Angle_Y=0):
    # Compute matrices
    Rx = rotation_matrix_x(object_Angle_X % 360)
    Ry = rotation_matrix_y(object_Angle_Y % 360)

    # Multiply in the new order (Y first, then X)
    new_rotation_matrix = Ry @ Rx
    glMultMatrixf(np.array(new_rotation_matrix, dtype=np.float32))


def set_custom_ortho_projection(near=0.1, far=10):
    # Orthographic projection matrix manually constructed
    proj = np.identity(4, dtype=np.float32)
    proj[0][0] = 1.0 / (bounds_max[0] - bounds_min[0])
    proj[1][1] = 1.0 / (bounds_max[1] - bounds_min[1])
    proj[2][2] = -2.0 / (far - near)
    proj[3][2] = -(far + near) / (far - near)
    proj[3][3] = 1.0
    # Set projection matrix
    # Transpose because OpenGL expects column-major order
    glLoadMatrixf(proj.T)
# --


### Rendering functions ###


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
                img_data[i][j] = [(i ^ j) & 0xFF, (i * j) & 0xFF,
                                  (i + j) & 0xFF]
        img_data = img_data.flatten()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)


def draw_axes(length=0.5, x=0, y=0, z=0):
    if not show_axes:
        return

    glDisable(GL_LIGHTING)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # X axis (red)
    glColor3f(1, 0, 0)
    glVertex3f(x, y, z)
    glVertex3f(x+length, 0, 0)
    # Y axis (green)
    glColor3f(0, 1, 0)
    glVertex3f(x, y, z)
    glVertex3f(0, y+length, 0)
    # Z axis (blue)
    glColor3f(0, 0, 1)
    glVertex3f(x, y, z)
    glVertex3f(0, 0, z+length)
    glEnd()

    # Draw axis labels
    glRasterPos3f(x+length + 0.05, y, z)
    glColor3f(1, 0, 0)
    for c in "X":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

    glRasterPos3f(x, y+length + 0.05, z)
    glColor3f(0, 1, 0)
    for c in "Y":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

    glRasterPos3f(x, y, z+length + 0.05)
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
    else:            # Positional light
        glColor3f(1.0, 0.5, 0.0)  # Orange
    glVertex3f(pos[0], pos[1], pos[2])
    glEnd()
    glEnable(GL_LIGHTING)


def draw_elliptical_torus(R, r, num_major=40, num_minor=20):
    eleptic_ratio = 1  # 1.5 - collision would be awkward...

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
                y = (R + r * cos_phi) * sin_theta * \
                    eleptic_ratio  # Elliptical shape
                z = r * sin_phi

                # Compute normal in local space
                nx = cos_phi * cos_theta
                ny = cos_phi * sin_theta
                nz = sin_phi

                # Apply elliptical distortion to the normal
                ny *= eleptic_ratio

                # Normalize
                norm = sqrt(nx * nx + ny * ny + nz * nz)
                nx /= norm
                ny /= norm
                nz /= norm

                glNormal3f(nx, ny, nz)
                if use_texture:
                    glTexCoord2f(theta / (2 * pi), phi / (2 * pi))
                glVertex3f(x, y, z)
        glEnd()


def animate_torus():
    global Torus_Pos, Torus_Velocity

    for i in range(3):
        Torus_Pos[i] += Torus_Velocity[i]
        check_collision_and_reflect(i, Torus_R + Torus_r)


def check_collision_and_reflect(axis_id, radius):
    global Torus_Pos, Torus_Velocity, Torus_Angle
    global bounds_min, bounds_max

    if Torus_Pos[axis_id] - radius < bounds_min[axis_id]:
        # Bounce
        Torus_Pos[axis_id] = bounds_min[axis_id] + radius
        Torus_Velocity[axis_id] = abs(Torus_Velocity[axis_id])
        # Reflect with rotation
        normal = np.zeros(3)
        normal[axis_id] = -1
        Torus_Angle = apply_rotation_on_bounce(Torus_Velocity,
                                               normal, Torus_Angle)
    elif Torus_Pos[axis_id] + radius > bounds_max[axis_id]:
        # Bounce
        Torus_Pos[axis_id] = bounds_max[axis_id] - radius
        Torus_Velocity[axis_id] = -abs(Torus_Velocity[axis_id])
        # Reflect with rotation
        normal = np.zeros(3)
        normal[axis_id] = 1
        Torus_Angle = apply_rotation_on_bounce(Torus_Velocity,
                                               normal, Torus_Angle)


def apply_rotation_on_bounce(velocity, normal, angle, spin_speed=15.0):
    """
    Updates the torus angles based on collision.

    velocity: np.array([vx, vy, vz]) - before collision
    normal: np.array([nx, ny, nz]) - surface normal (e.g., [1,0,0] for +X wall)
    angle: np.array([angle_x, angle_y, angle_z]) - current rotation angles (degrees)
    spin_speed: float - multiplier for rotation intensity
    """
    # Angular momentum approximation: axis = V × N
    axis = np.cross(velocity, normal)
    if np.linalg.norm(axis) > 0.0001:
        axis = axis / np.linalg.norm(axis)
        # Add to rotation angles (scaled)
        angle += axis * spin_speed
    return Angle(angle[0], angle[1], angle[2])


def set_perspective_projection():
    # Apply rotation to the entire scene
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    set_custom_ortho_projection()

    # Just good matrices and all. Which one to use - depends on the task
    # glOrtho(-2, 2, -2, 2, -10, 10)  # Wider view area. Disables Z
    # glFrustum(-2, 2, -2, 2, 0.1, 10)  # Perspective projection

    # Pussy vvv
    # gluPerspective(45, 1, 0.1, 100)  # Set perspective projection
    # glTranslatef(0, 0, -5)  # Move back to see the torus
    # OR
    # gluLookAt(0, 0, 5,  # Eye position
    #           0, 0, 0,  # Look at point
    #           0, 1, 0)  # Up vector
    glMatrixMode(GL_MODELVIEW)


def display(window):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    # ---- Draw scene ---
    glScalef(scale, scale, scale)

    # Apply scene rotation
    glRotatef(scene_Angle.x, 1, 0, 0)
    glRotatef(scene_Angle.y, 0, 1, 0)

    # # Setup lighting after view transformation but before object transformations
    setup_lighting()

    # Draw axes, bounds, and light marker
    # draw_axes()
    # draw_bounds()
    draw_light_marker()

    # ---- Draw torus ---
    # Derive scene properties
    glTranslatef(*Torus_Pos)
    glScalef(*Torus_Scale)

    # Apply torus rotation independently
    glRotatef(Torus_Angle.x, 1, 0, 0)
    glRotatef(Torus_Angle.y, 0, 1, 0)

    if use_texture and texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
    else:
        glDisable(GL_TEXTURE_2D)
        # Set material color (without texture)
        # But light overrides it :(
        glColor3f(*Torus_default_color)

    draw_elliptical_torus(Torus_R, Torus_r)
    # draw_axes(0.2)

    glfw.swap_buffers(window)
    glfw.poll_events()


def key_callback(window, key, scancode, action, mods):
    """
    Handles key press and key repeat events for controlling the OpenGL scene.

    Keybindings:
        General:
            - SPACE: Toggle animation on/off.
            - R: Reset torus position, velocity, scale, and scene rotation.
            - ESCAPE: Close the program.

        Scene Rotation:
            Axes are fucked. Depends on the camera position.
            No Z axis. Orho projection.
            - H: Rotate the scene left by y
            - L: Rotate the scene right by -y
            - J: Rotate the scene down by x
            - K: Rotate the scene up by -x

        Torus Rotation: 
            Axes are fucked. Depends on the torus position.
            No Z axis. I don't have so many keys.
            - RIGHT: Rotate the torus right by y
            - LEFT: Rotate the torus right by -y
            - UP: Rotate the torus up by x
            - DOWN: Rotate the torus down by -x

        Torus Position:
            - W: Move the torus up along the y-axis.
            - S: Move the torus down along the y-axis.
            - A: Move the torus left along the x-axis.
            - D: Move the torus right along the x-axis.
            - Q: Move the torus forward along the z-axis.
            - E: Move the torus backward along the z-axis.

        Torus Scale:
            - Z: Increase the torus scale by 10%.
            - X: Decrease the torus scale by 10%.

        Polygon Mode:
            - M: Toggle between wireframe and filled polygon rendering.

        Texture:
            - T: Toggle texture usage on/off.

        Animation Speed:
            - EQUAL (=): Increase the animation speed by 10%.
            - MINUS (-): Decrease the animation speed by 10%.

        Light and Material Presets:
            - 1-5: Select light presets (0-4).
            - 6-8: Select material presets (0-2).

        Display Toggles:
            - B: Toggle bounding box display on/off.
            - V: Toggle axes display on/off.
    """
    global Torus_Angle, Torus_Pos, Torus_Scale
    global wireframe, use_texture, animation, Torus_Velocity
    global light_index, material_index, show_axes, show_bounds
    global scene_Angle
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_SPACE:
            animation = not animation
        elif key == glfw.KEY_R:
            # Reset torus position and velocity and projection
            Torus_Pos = [0.0, 0.0, 0.0]
            Torus_Velocity = [0.005, 0.006, 0.007]
            Torus_Scale = [1.0, 1.0, 1.0]
            Torus_Angle = Angle(0, 0)
            scene_Angle = Angle(0, 0)

        # ----- Scene rotation ----
        elif key == glfw.KEY_H:
            scene_Angle.update_y(3)
        elif key == glfw.KEY_L:
            scene_Angle.update_y(-3)
        elif key == glfw.KEY_J:
            scene_Angle.update_x(-3)
        elif key == glfw.KEY_K:
            scene_Angle.update_x(3)

        # ----- Torus rotation ----
        elif key == glfw.KEY_RIGHT:
            Torus_Angle.update_y(3)
        elif key == glfw.KEY_LEFT:
            Torus_Angle.update_y(-3)
        elif key == glfw.KEY_UP:
            Torus_Angle.update_x(3)
        elif key == glfw.KEY_DOWN:
            Torus_Angle.update_x(-3)

        # ----- Torus position ----
        elif key == glfw.KEY_W:
            Torus_Pos[1] += 0.1
        elif key == glfw.KEY_S:
            Torus_Pos[1] -= 0.1
        elif key == glfw.KEY_A:
            Torus_Pos[0] -= 0.1
        elif key == glfw.KEY_D:
            Torus_Pos[0] += 0.1
        elif key == glfw.KEY_Q:
            Torus_Pos[2] += 0.1
        elif key == glfw.KEY_E:
            Torus_Pos[2] -= 0.1

        # ----- Torus scale ----
        elif key == glfw.KEY_Z:
            Torus_Scale = [v * 1.1 for v in Torus_Scale]
        elif key == glfw.KEY_X:
            Torus_Scale = [v * 0.9 for v in Torus_Scale]

        # ----- Polygon toggle ----
        elif key == glfw.KEY_M:
            wireframe = not wireframe
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)

        # ----- Texture toggle ----
        elif key == glfw.KEY_T:
            use_texture = not use_texture

        # ----- Animation speed ----
        elif key == glfw.KEY_EQUAL:
            Torus_Velocity = [v * 1.1 for v in Torus_Velocity]
        elif key == glfw.KEY_MINUS:
            Torus_Velocity = [v * 0.9 for v in Torus_Velocity]

        # ----- Light and material presets ----
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

        # ----- Toggle bounds display ----
        elif key == glfw.KEY_B:
            show_bounds = not show_bounds

        # ----- Toggle axes display ----
        elif key == glfw.KEY_V:
            show_axes = not show_axes

        # ----- Close program ----
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def scroll_callback(window, xoffset, yoffset):
    global Torus_Scale
    factor = 1.1 if yoffset > 0 else 0.9
    Torus_Scale = [v * factor for v in Torus_Scale]


def main():
    if not glfw.init():
        return
    
    # Set up timer
    frame_count = 0
    last_time = time.time()

    # Initialize GLUT
    glutInit()  # Required for GLUT functions like glutBitmapCharacter

    Window_Height = 800
    Window_Width = 800
    window = glfw.create_window(Window_Height, Window_Width,
                                "Enhanced Torus Simulation", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(0)  # отключаем V-Sync
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # Initialize OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    # Load closest texture for torus
    texture = __file__[:__file__.rfind("/")+1] + 'texture.bmp'
    load_texture(texture)



    # Set projection matrix
    set_perspective_projection()

    # Salute to macs and other strange resolutions like 3200x2000
    glViewport(0, 0, Window_Height, Window_Width)
    width, height = glfw.get_framebuffer_size(window)
    print("OK" if width == Window_Height and height == Window_Width else "PROBLEMS",
          end="")
    print(f". Framebuffer size: {width}x{height}; "
          f"glViewport: {glGetIntegerv(GL_VIEWPORT)}")

    # Main loop
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if animation:
            animate_torus()

        display(window)

        # FPS counting
        frame_count += 1
        current_time = time.time()
        elapsed = current_time - last_time
        if elapsed >= 1.0:
            print(f"FPS: {frame_count}")
            frame_count = 0
            last_time = current_time

    glfw.terminate()


if __name__ == "__main__":
    main()
