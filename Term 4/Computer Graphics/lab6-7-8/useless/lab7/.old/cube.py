import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import numpy as np
import math

angle = 0.0
frame_count = 0
start_time = time.time()

# 8 вершин куба
vertices = [
    (-0.5, -0.5, -0.5),
    ( 0.5, -0.5, -0.5),
    ( 0.5,  0.5, -0.5),
    (-0.5,  0.5, -0.5),
    (-0.5, -0.5,  0.5),
    ( 0.5, -0.5,  0.5),
    ( 0.5,  0.5,  0.5),
    (-0.5,  0.5,  0.5),
]

# Пары индексов для линий (12 рёбер)
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # нижнее основание
    (4, 5), (5, 6), (6, 7), (7, 4),  # верхнее основание
    (0, 4), (1, 5), (2, 6), (3, 7)   # вертикальные рёбра
]

def draw_wire_cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def rotation_x(angle_rad):
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [1, 0,  0, 0],
        [0, c, -s, 0],
        [0, s,  c, 0],
        [0, 0,  0, 1]
    ], dtype=np.float32)

def rotation_y(angle_rad):
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

def rotation_matrix(angle_degrees, x, y, z):
    """Construct a 4x4 rotation matrix like glRotatef(angle, x, y, z)."""
    angle = np.radians(angle_degrees)
    c = np.cos(angle)
    s = np.sin(angle)
    t = 1 - c

    # Normalize axis vector
    mag = np.sqrt(x*x + y*y + z*z)
    if mag == 0:
        raise ValueError("Rotation axis cannot be zero vector")
    x /= mag
    y /= mag
    z /= mag

    return np.array([
        [t*x*x + c,   t*x*y - s*z, t*x*z + s*y, 0],
        [t*x*y + s*z, t*y*y + c,   t*y*z - s*x, 0],
        [t*x*z - s*y, t*y*z + s*x, t*z*z + c,   0],
        [0,           0,           0,           1]
    ], dtype=np.float32)

def isometric_matrix():
    pass
def isometric_projection():
    # glRotatef(35.264, 1, 0, 0)
    # glRotatef(45, 0, 1, 0)
    # angle_rad = np.radians(45)  # Convert angle to radians
    # c = np.cos(angle_rad)
    # s = np.sin(angle_rad)
    # x, y, z = 1, 1, 1  # Normalized vector (x, y, z)

    # matrix = [
    #     [x * x * (1 - c) + c,     x * y * (1 - c) - z * s, x * z * (1 - c) + y * s, 0],
    #     [y * x * (1 - c) + z * s, y * y * (1 - c) + c,     y * z * (1 - c) - x * s, 0],
    #     [x * z * (1 - c) - y * s, y * z * (1 - c) + x * s, z * z * (1 - c) + c,     0],
    #     [0,                       0,                       0,                       1]
    # ]

    # matrix = np.array(matrix, dtype=np.float32).T.flatten()  # Транспонируем и распрямляем матрицу
    # glMultMatrixf(matrix)  # Применяем матрицу к текущей матрице модели
    # Usage example:
    # alpha = np.radians(35.264)  # 30 degrees in radians
    # beta = np.radians(45)   # 45 degrees in radians

    # # Combine rotations (order matters: Y then X)
    # rotation_matrix = rotation_x(alpha) @ rotation_y(beta)

    # # Pass to shader (assuming you have a shader program)
    # glMultMatrixf(rotation_matrix)

    scale_matrix = 1 / np.sqrt(6) * np.array([
        [np.sqrt(3), 0, -np.sqrt(3), 0],
        [1, 2, 1, 0],
        [np.sqrt(2), -np.sqrt(2), np.sqrt(2), 0],
        [0, 0, 0, np.sqrt(6)]
    ], dtype=np.float32)
    # glMultMatrixf(scale_matrix)
    glMultMatrixf(rotation_matrix(35.264, 1, 0, 0))
    glMultMatrixf(rotation_matrix(45, 0, 1, 0))

def main():
    global angle, frame_count, start_time

    if not glfw.init():
        raise Exception("GLFW init failed")

    window = glfw.create_window(640, 480, "Wireframe Cube (no GLUT)", None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window failed")

    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)

    # glMatrixMode(GL_PROJECTION)
    # glLoadIdentity()
    # glRotatef(35.264, 1, 0, 0)
    # glRotatef(-45, 0, 1, 0)
    # glOrtho(-2, 2, -2, 2, 0.1, 10.0)
    # gluPerspective(45, 640/480, 0.1, 100)
    # glOrtho(-10, 10, -10, 10, -10, 10); 
    # glRotatef(35.264, 1, 0, 0); 
    # glRotatef(45, 0, 1, 0);     

    # glMatrixMode(GL_MODELVIEW)

    # gluPerspective(45, 640/480, 0.1, 100)
    # glOrtho(-1, 1, -1, 1, -1, 1)  # Параметры для ортографической проекции

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # glTranslatef(0, 0, -1)
        glRotatef(angle, 1, 1, 0)

        # glRotatef(35.264, 1, 0, 0)
        # glRotatef(35.264, 1, 0, 0)
        # glRotatef(45, 0, 1, 0)
        # glRotatef(-45, 0, 1, 0)
        
        # isometric_projection()
        draw_wire_cube()
        glfw.swap_buffers(window)
        glfw.poll_events()

        # FPS счетчик
        frame_count += 1
        now = time.time()
        if now - start_time >= 1.0:
            print(f"FPS: {frame_count}")
            frame_count = 0
            start_time = now

        angle += 1

    glfw.terminate()

if __name__ == "__main__":
    main()
