import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Initialize GLFW
if not glfw.init():
    raise Exception("GLFW initialization failed")

width, height = 800, 600
window = glfw.create_window(width, height, "3D Cyrus-Beck Clipping", None, None)
if not window:
    glfw.terminate()
    raise Exception("GLFW window creation failed")

glfw.make_context_current(window)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Settings
wireframe_mode = False
cube_size = 0.8
zoom = 5.0
rotation_x = 30.0
rotation_y = 30.0

# Line parameters
line_start = np.array([-1.5, -1.5, -1.5], dtype=np.float32)
line_end = np.array([1.5, 1.5, 1.5], dtype=np.float32)

def setup_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def cyrus_beck_clip(P0, P1):
    planes = [
        (np.array([0, 0, 1], dtype=np.float32), -cube_size),  # Back
        (np.array([0, 0, -1], dtype=np.float32), -cube_size),  # Front
        (np.array([0, 1, 0], dtype=np.float32), -cube_size),   # Bottom
        (np.array([0, -1, 0], dtype=np.float32), -cube_size),  # Top
        (np.array([1, 0, 0], dtype=np.float32), -cube_size),   # Left
        (np.array([-1, 0, 0], dtype=np.float32), -cube_size)   # Right
    ]
    
    t_enter = 0.0
    t_exit = 1.0
    D = P1 - P0
    
    for normal, d in planes:
        numerator = np.dot(normal, P0) + d
        denominator = -np.dot(normal, D)
        
        if abs(denominator) < 1e-6:
            if numerator < 0: return None
        else:
            t = numerator / denominator
            if denominator < 0:
                if t > t_enter: t_enter = t
            else:
                if t < t_exit: t_exit = t
            
            if t_enter > t_exit: return None
    
    if t_enter <= t_exit and 0 <= t_enter <= 1 and 0 <= t_exit <= 1:
        return (P0 + t_enter * D, P0 + t_exit * D)
    return None

def draw_cube():
    vertices = [
        [-cube_size, -cube_size, -cube_size],
        [cube_size, -cube_size, -cube_size],
        [cube_size, cube_size, -cube_size],
        [-cube_size, cube_size, -cube_size],
        [-cube_size, -cube_size, cube_size],
        [cube_size, -cube_size, cube_size],
        [cube_size, cube_size, cube_size],
        [-cube_size, cube_size, cube_size]
    ]
    
    faces = [
        [0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4],
        [2, 3, 7, 6], [0, 3, 7, 4], [1, 2, 6, 5]
    ]
    
    if wireframe_mode:
        glColor3f(0.3, 0.3, 0.3)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glColor4f(0.7, 0.7, 0.7, 0.3)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    glBegin(GL_QUADS)
    for face in faces:
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()
    
    # Always draw wireframe over solid
    if not wireframe_mode:
        glColor3f(0.3, 0.3, 0.3)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBegin(GL_QUADS)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

def draw_line(start, end, color, width=1.0):
    glColor3fv(color)
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex3fv(start)
    glVertex3fv(end)
    glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0, 0, zoom, 0, 0, 0, 0, 1, 0)
    glRotatef(rotation_x, 1, 0, 0)
    glRotatef(rotation_y, 0, 1, 0)
    
    # Draw axes
    glBegin(GL_LINES)
    glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(1,0,0)
    glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,1,0)
    glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,1)
    glEnd()
    
    draw_cube()
    
    # Draw original line
    draw_line(line_start, line_end, (1, 0, 0))
    
    # Clip and draw visible segment
    clipped = cyrus_beck_clip(line_start, line_end)
    if clipped:
        # Draw thick green line for clipped segment
        draw_line(clipped[0], clipped[1], (0, 1, 0), 4.0)
        
        # Draw markers at clip points
        glPointSize(10.0)
        glBegin(GL_POINTS)
        glColor3f(1,1,0); glVertex3fv(clipped[0])  # Yellow entry point
        glColor3f(0,1,1); glVertex3fv(clipped[1])  # Cyan exit point
        glEnd()
    
    glfw.swap_buffers(window)

def key_callback(window, key, scancode, action, mods):
    global rotation_x, rotation_y, zoom, line_start, line_end, wireframe_mode
    
    if action == glfw.PRESS or action == glfw.REPEAT:
        # Rotation
        if key == glfw.KEY_LEFT: rotation_y -= 5
        elif key == glfw.KEY_RIGHT: rotation_y += 5
        elif key == glfw.KEY_UP: rotation_x -= 5
        elif key == glfw.KEY_DOWN: rotation_x += 5
        # Zoom
        elif key == glfw.KEY_Z: zoom -= 0.5
        elif key == glfw.KEY_X: zoom += 0.5
        # Reset view
        elif key == glfw.KEY_C:
            rotation_x, rotation_y, zoom = 30.0, 30.0, 5.0
        # Line movement
        elif key == glfw.KEY_1: line_start[0] -= 0.1
        elif key == glfw.KEY_2: line_start[0] += 0.1
        elif key == glfw.KEY_3: line_start[1] -= 0.1
        elif key == glfw.KEY_4: line_start[1] += 0.1
        elif key == glfw.KEY_5: line_start[2] -= 0.1
        elif key == glfw.KEY_6: line_start[2] += 0.1
        elif key == glfw.KEY_7: line_end[0] -= 0.1
        elif key == glfw.KEY_8: line_end[0] += 0.1
        elif key == glfw.KEY_9: line_end[1] -= 0.1
        elif key == glfw.KEY_0: line_end[1] += 0.1
        elif key == glfw.KEY_MINUS: line_end[2] -= 0.1
        elif key == glfw.KEY_EQUAL: line_end[2] += 0.1
        # Reset line
        elif key == glfw.KEY_R:
            line_start = np.array([-1.5, -1.5, -1.5], dtype=np.float32)
            line_end = np.array([1.5, 1.5, 1.5], dtype=np.float32)
        # Toggle wireframe
        elif key == glfw.KEY_W:
            wireframe_mode = not wireframe_mode

glfw.set_key_callback(window, key_callback)
setup_projection()

while not glfw.window_should_close(window):
    display()
    glfw.poll_events()

glfw.terminate()