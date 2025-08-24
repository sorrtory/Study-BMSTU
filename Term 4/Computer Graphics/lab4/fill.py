import glfw
from OpenGL.GL import *
import numpy as np

# Параметры окна
WIDTH, HEIGHT = 800, 800
framebuffer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
polygon = []  # Храним точки многоугольника

# Global color definitions
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)

# Отрисовка пикселя
def plot(x, y, color, alpha=1.0):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        framebuffer[y, x] = (framebuffer[y, x] * (1 - alpha) +
                             np.array(color) * alpha).astype(np.uint8)

# https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
# Алгоритм Брезенхема для отрисовки линий
def draw_line(x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    error = dx + dy

    while True:
        plot(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * error
        if e2 >= dy:
            error += dy
            x0 += sx
        if e2 <= dx:
            error += dx
            y0 += sy
# https://ru.wikipedia.org/wiki/%D0%90%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC_%D0%91%D1%80%D0%B5%D0%B7%D0%B5%D0%BD%D1%85%D1%8D%D0%BC%D0%B0
# Алгоритм Брезенхема для отрисовки окружностей
def draw_circle(x1, y1, radius, color):
    x = 0
    y = radius
    delta = 1 - 2 * radius
    error = 0

    while y >= x:
        plot(x1 + x, y1 + y, color)
        plot(x1 + x, y1 - y, color)
        plot(x1 - x, y1 + y, color)
        plot(x1 - x, y1 - y, color)
        plot(x1 + y, y1 + x, color)
        plot(x1 + y, y1 - x, color)
        plot(x1 - y, y1 + x, color)
        plot(x1 - y, y1 - x, color)
        error = 2 * (delta + y) - 1
        if delta < 0 and error <= 0:
            delta += 2 * x + 1
            x += 1
            continue
        if delta > 0 and error > 0:
            delta -= 2 * y + 1
            y -= 1
            continue
        delta += 2 * (x - y)
        x += 1
        y -= 1

# https://en.wikipedia.org/wiki/Flood_fill
# Заливка
def flood_fill(x, y, fill_color, boundary_color):
    stack = [(x, y)]
    cnt = 0
    while stack:
        cx, cy = stack.pop()
        if 0 <= cx < WIDTH and 0 <= cy < HEIGHT:
            current_color = framebuffer[cy, cx]
            if not np.array_equal(current_color, fill_color) and not np.array_equal(current_color, boundary_color):
                framebuffer[cy, cx] = fill_color
                # stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1),
                #               (cx + 1, cy + 1), (cx - 1, cy - 1), (cx + 1, cy - 1), (cx - 1, cy + 1)])
                stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
                print(f"Filling pixel #{cnt}: ({cx}, {cy})\r", end="")
                cnt += 1 


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    width, height = glfw.get_framebuffer_size(window)
    glViewport(0, 0, width, height)
    glDrawPixels(WIDTH, HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, framebuffer)
    glfw.swap_buffers(window)


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)

def calculate_centroid(polygon):
    x_coords = [p[0] for p in polygon]
    y_coords = [p[1] for p in polygon]
    centroid_x = sum(x_coords) // len(polygon)
    centroid_y = sum(y_coords) // len(polygon)
    return centroid_x, centroid_y


def mouse_button_callback(window, button, action, mods):
    global polygon
    if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_LEFT:
        # Get the mouse position
        x, y = glfw.get_cursor_pos(window)
        x, y = int(x), HEIGHT - int(y)  # Convert to framebuffer coordinates
        polygon.append((x, y))  # Add the vertex to the polygon
        draw_circle(x, y, 5, COLOR_WHITE)  # Draw a circle at the clicked position
    elif action == glfw.PRESS and button == glfw.MOUSE_BUTTON_RIGHT:
        if len(polygon) > 2:
            # Draw the polygon edges
            for i in range(len(polygon) - 1):
                draw_line(*polygon[i], *polygon[i + 1], COLOR_WHITE)
            draw_line(*polygon[-1], *polygon[0], COLOR_WHITE)
            # Use the first point of the polygon as the seed point for filling
            seed_x, seed_y = calculate_centroid(polygon)
            # seed_x, seed_y = polygon[0]
            flood_fill(seed_x, seed_y, COLOR_RED, COLOR_WHITE)
        polygon = []  # Reset the polygon for new input

def key_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_R and action == glfw.PRESS:
        # Очистка экрана при нажатии R
        global framebuffer, polygon
        framebuffer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        polygon = []


if __name__ == "__main__":
    if not glfw.init():
        exit()
    window = glfw.create_window(
        WIDTH, HEIGHT, "Polygon Rasterization", None, None)
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    # Обработчик клавиш для очистки
    glfw.set_key_callback(window, key_callback)
    while not glfw.window_should_close(window):
        display()
        glfw.poll_events()
    glfw.terminate()
