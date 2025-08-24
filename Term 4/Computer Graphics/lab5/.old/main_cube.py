import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *  # Import GLU functions for gluPerspective
import numpy as np
from math import cos, sin, radians

# Initialize GLFW
if not glfw.init():
    raise Exception("GLFW initialization failed")

# Window dimensions
width, height = 800, 600
window = glfw.create_window(width, height, "3D Cyrus-Beck Clipping", None, None)

if not window:
    glfw.terminate()
    raise Exception("GLFW window creation failed")

glfw.make_context_current(window)

# Enable depth testing
glEnable(GL_DEPTH_TEST)

# Camera parameters
zoom = 5.0
rotation_x = 30.0  # Start with a slightly angled view
rotation_y = 30.0

# Clipping cube vertices (smaller size to fit better)
cube_size = 0.8  # Reduced from 1.0 to fit better
cube_vertices = np.array([
    [-cube_size, -cube_size, -cube_size],  # 0
    [cube_size, -cube_size, -cube_size],   # 1
    [cube_size, cube_size, -cube_size],    # 2
    [-cube_size, cube_size, -cube_size],   # 3
    [-cube_size, -cube_size, cube_size],   # 4
    [cube_size, -cube_size, cube_size],    # 5
    [cube_size, cube_size, cube_size],     # 6
    [-cube_size, cube_size, cube_size]     # 7
], dtype=np.float32)

# Cube faces (for visualization)
cube_faces = [
    [0, 1, 2, 3],  # back
    [4, 5, 6, 7],  # front
    [0, 1, 5, 4],  # bottom
    [2, 3, 7, 6],  # top
    [0, 3, 7, 4],  # left
    [1, 2, 6, 5]   # right
]

# Line to be clipped (initial points outside the cube)
line_start = np.array([-1.5, -1.5, -1.5], dtype=np.float32)
line_end = np.array([1.5, 1.5, 1.5], dtype=np.float32)

# Clipped line (will be calculated)
clipped_start = np.copy(line_start)
clipped_end = np.copy(line_end)

def setup_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = width / height
    gluPerspective(45, aspect, 0.1, 100.0)  # Reasonable perspective projection
    glMatrixMode(GL_MODELVIEW)

def cyrus_beck_clip(line_start, line_end, clip_vertices):
    # Define the 6 planes of the cube (normal pointing inward)
    planes = []
    # Back plane (z = -cube_size)
    planes.append((np.array([0, 0, 1], dtype=np.float32), -cube_size))
    # Front plane (z = cube_size)
    planes.append((np.array([0, 0, -1], dtype=np.float32), -cube_size))
    # Bottom plane (y = -cube_size)
    planes.append((np.array([0, 1, 0], dtype=np.float32), -cube_size))
    # Top plane (y = cube_size)
    planes.append((np.array([0, -1, 0], dtype=np.float32), -cube_size))
    # Left plane (x = -cube_size)
    planes.append((np.array([1, 0, 0], dtype=np.float32), -cube_size))
    # Right plane (x = cube_size)
    planes.append((np.array([-1, 0, 0], dtype=np.float32), -cube_size))
    
    t_enter = 0.0
    t_exit = 1.0
    line_dir = line_end - line_start
    
    for normal, d in planes:
        numerator = np.dot(normal, line_start) + d
        denominator = -np.dot(normal, line_dir)
        
        if abs(denominator) < 1e-6:
            # Line is parallel to the plane
            if numerator < 0:
                return None  # Line is outside
        else:
            t = numerator / denominator
            if denominator < 0:
                # Line is entering the clipping plane
                if t > t_enter:
                    t_enter = t
            else:
                # Line is exiting the clipping plane
                if t < t_exit:
                    t_exit = t
            
            if t_enter > t_exit:
                return None  # Line is completely outside
    
    if t_enter < t_exit and t_exit > 0 and t_enter < 1:
        new_start = line_start + t_enter * line_dir
        new_end = line_start + t_exit * line_dir
        return (new_start, new_end)
    
    return None

def draw_cube():
    glBegin(GL_QUADS)
    for face in cube_faces:
        for vertex in face:
            glVertex3fv(cube_vertices[vertex])
    glEnd()

def draw_line(start, end, color):
    glColor3fv(color)
    glBegin(GL_LINES)
    glVertex3fv(start)
    glVertex3fv(end)
    glEnd()

def draw_axes():
    # X axis (red)
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(2.0, 0.0, 0.0)
    glEnd()
    
    # Y axis (green)
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 2.0, 0.0)
    glEnd()
    
    # Z axis (blue)
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 2.0)
    glEnd()

def display():
    global clipped_start, clipped_end
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Set up the view
    gluLookAt(0, 0, 5,  # Eye position
              0, 0, 0,  # Look-at point
              0, 1, 0)  # Up vector
    
    # Apply rotation and zoom
    glTranslatef(0.0, 0.0, -zoom)
    glRotatef(rotation_x, 1.0, 0.0, 0.0)
    glRotatef(rotation_y, 0.0, 1.0, 0.0)
    
    # Draw axes
    draw_axes()
    
    # Draw the clipping cube (wireframe)
    glColor3f(0.5, 0.5, 0.5)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    draw_cube()
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    # Clip the line
    result = cyrus_beck_clip(line_start, line_end, cube_vertices)
    
    # Draw original line (red)
    draw_line(line_start, line_end, (1.0, 0.0, 0.0))
    
    # Draw clipped line (green)
    if result:
        clipped_start, clipped_end = result
        draw_line(clipped_start, clipped_end, (0.0, 1.0, 0.0))
    
    glfw.swap_buffers(window)

def key_callback(window, key, scancode, action, mods):
    global rotation_x, rotation_y, zoom, line_start, line_end, clipped_start, clipped_end
    
    if action == glfw.PRESS or action == glfw.REPEAT:
        # Rotation controls
        if key == glfw.KEY_LEFT:
            rotation_y -= 5
        elif key == glfw.KEY_RIGHT:
            rotation_y += 5
        elif key == glfw.KEY_UP:
            rotation_x -= 5
        elif key == glfw.KEY_DOWN:
            rotation_x += 5
        
        # Zoom controls
        elif key == glfw.KEY_Z:
            zoom -= 0.5
        elif key == glfw.KEY_X:
            zoom += 0.5
        
        # Clear rotation
        elif key == glfw.KEY_C:
            rotation_x = 30.0
            rotation_y = 30.0
            zoom = 5.0
        
        # Line endpoint controls
        elif key == glfw.KEY_1:
            line_start[0] -= 0.1
        elif key == glfw.KEY_2:
            line_start[0] += 0.1
        elif key == glfw.KEY_3:
            line_start[1] -= 0.1
        elif key == glfw.KEY_4:
            line_start[1] += 0.1
        elif key == glfw.KEY_5:
            line_start[2] -= 0.1
        elif key == glfw.KEY_6:
            line_start[2] += 0.1
        elif key == glfw.KEY_7:
            line_end[0] -= 0.1
        elif key == glfw.KEY_8:
            line_end[0] += 0.1
        elif key == glfw.KEY_9:
            line_end[1] -= 0.1
        elif key == glfw.KEY_0:
            line_end[1] += 0.1
        elif key == glfw.KEY_MINUS:
            line_end[2] -= 0.1
        elif key == glfw.KEY_EQUAL:
            line_end[2] += 0.1
        
        # Reset line
        elif key == glfw.KEY_R:
            line_start[:] = [-1.5, -1.5, -1.5]
            line_end[:] = [1.5, 1.5, 1.5]

# Set callbacks
glfw.set_key_callback(window, key_callback)
glfw.set_window_size_callback(window, lambda window, w, h: setup_projection())

# Initial setup
setup_projection()

# Main loop
while not glfw.window_should_close(window):
    display()
    glfw.poll_events()

glfw.terminate()