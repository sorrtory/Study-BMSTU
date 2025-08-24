import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

# Инициализация параметров
window_width = 800
window_height = 600
cube_size = 4.0
ball_radius = 0.2
ball_pos = np.array([0.0, 0.0, 0.0], dtype=np.float32)
ball_vel = np.array([0.03, 0.05, 0.02], dtype=np.float32)  # Начальная скорость

def init():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (window_width/window_height), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

def draw_cube():
    half_size = cube_size / 2.0
    vertices = [
        [-half_size, -half_size, -half_size],
        [ half_size, -half_size, -half_size],
        [ half_size,  half_size, -half_size],
        [-half_size,  half_size, -half_size],
        [-half_size, -half_size,  half_size],
        [ half_size, -half_size,  half_size],
        [ half_size,  half_size,  half_size],
        [-half_size,  half_size,  half_size]
    ]
    
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_ball():
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(ball_pos[0], ball_pos[1], ball_pos[2])
    quadric = gluNewQuadric()
    gluSphere(quadric, ball_radius, 32, 32)
    gluDeleteQuadric(quadric)
    glPopMatrix()

def update_ball_position():
    global ball_pos, ball_vel
    half_cube = cube_size / 2.0 - ball_radius
    
    # Обновляем позицию
    ball_pos += ball_vel
    
    # Проверяем столкновения с границами куба и отражаем скорость
    for i in range(3):
        if ball_pos[i] > half_cube:
            ball_pos[i] = half_cube
            ball_vel[i] = -ball_vel[i]
        elif ball_pos[i] < -half_cube:
            ball_pos[i] = -half_cube
            ball_vel[i] = -ball_vel[i]

def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(window_width, window_height, "Шар в кубе с упругими отражениями", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    init()
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        # Обновление позиции шара
        update_ball_position()
        
        # Очистка буферов
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Установка камеры
        glLoadIdentity()
        gluLookAt(5, 5, 5, 0, 0, 0, 0, 1, 0)
        
        # Отрисовка сцены
        draw_cube()
        draw_ball()
        
        glfw.swap_buffers(window)
    
    glfw.terminate()

if __name__ == "__main__":
    main()