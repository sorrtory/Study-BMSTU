import glfw
from OpenGL.GL import *
import numpy as np

# Параметры окна
WIDTH, HEIGHT = 800, 800
framebuffer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
polygon = []

# Цвета
COLOR_WHITE = (255, 255, 255)
COLOR_POLYGON_FILL = (255, 0, 0)

def plot(x, y, color, alpha=1.0):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        framebuffer[y, x] = (framebuffer[y, x] * (1 - alpha) +
                             np.array(color) * alpha).astype(np.uint8)

def draw_line(x0, y0, x1, y1, color):
    dx, sx = abs(x1 - x0), 1 if x0 < x1 else -1
    dy, sy = -abs(y1 - y0), 1 if y0 < y1 else -1
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

def draw_circle(x1, y1, radius, color):
    x, y = 0, radius
    delta = 1 - 2 * radius
    while y >= x:
        for dx, dy in [(x, y), (x, -y), (-x, y), (-x, -y), (y, x), (y, -x), (-y, x), (-y, -x)]:
            plot(x1 + dx, y1 + dy, color)
        error = 2 * (delta + y) - 1
        if delta < 0 and error <= 0:
            delta += 2 * x + 1
            x += 1
        elif delta > 0 and error > 0:
            delta -= 2 * y + 1
            y -= 1
        else:
            delta += 2 * (x - y)
            x += 1
            y -= 1

def flood_fill(x, y, fill_color, boundary_color):
    stack = [(x, y)]
    while stack:
        x, y = stack.pop()
        if 0 <= x < WIDTH and 0 <= y < HEIGHT and \
           not np.array_equal(framebuffer[y, x], fill_color) and \
           not np.array_equal(framebuffer[y, x], boundary_color):
            lx, rx = x, x
            while lx > 0 and not np.array_equal(framebuffer[y, lx - 1], boundary_color):
                lx -= 1
            while rx < WIDTH - 1 and not np.array_equal(framebuffer[y, rx + 1], boundary_color):
                rx += 1
            for i in range(lx, rx + 1):
                plot(i, y, fill_color)
                for dy in [-1, 1]:
                    ny = y + dy
                    if 0 <= ny < HEIGHT and not np.array_equal(framebuffer[ny, i], boundary_color):
                        stack.append((i, ny))

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    w, h = glfw.get_framebuffer_size(window)
    glViewport(0, 0, w, h)
    glDrawPixels(WIDTH, HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, framebuffer)
    glfw.swap_buffers(window)

def framebuffer_size_callback(window, new_width, new_height):
    global WIDTH, HEIGHT, framebuffer, polygon
    WIDTH, HEIGHT = new_width, new_height
    framebuffer = np.resize(framebuffer, (HEIGHT, WIDTH, 3))
    glViewport(0, 0, WIDTH, HEIGHT)

def calculate_centroid(polygon):
    x_coords = [p[0] for p in polygon]
    y_coords = [p[1] for p in polygon]
    return sum(x_coords) // len(polygon), sum(y_coords) // len(polygon)

def draw_filtered_line(x0, y0, x1, y1, color):
    deltax, deltay = abs(x1 - x0), abs(y1 - y0)
    error = 0
    deltaerr = max(deltax, deltay) + 1
    x, y = x0, y0
    dirx = 1 if x1 > x0 else -1 if x1 < x0 else 0
    diry = 1 if y1 > y0 else -1 if y1 < y0 else 0

    if deltax >= deltay:
        for _ in range(deltax + 1):
            alpha = 1 - (error / deltaerr)
            plot(x, y, color, alpha)
            x += dirx
            error += deltay
            if error >= deltaerr:
                y += diry
                error -= deltaerr
    else:
        for _ in range(deltay + 1):
            alpha = 1 - (error / deltaerr)
            plot(x, y, color, alpha)
            y += diry
            error += deltax
            if error >= deltaerr:
                x += dirx
                error -= deltaerr

def draw_polygon(polygon, color):
    if len(polygon) > 2:
        for i in range(len(polygon)):
            draw_line(*polygon[i], *polygon[(i + 1) % len(polygon)], COLOR_WHITE)
        seed_x, seed_y = calculate_centroid(polygon)
        flood_fill(seed_x, seed_y, color, COLOR_WHITE)
        for i in range(len(polygon)):
            draw_filtered_line(*polygon[i], *polygon[(i + 1) % len(polygon)], COLOR_WHITE)

def mouse_button_callback(window, button, action, mods):
    global polygon
    if action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        x, y = int(x), HEIGHT - int(y)
        if button == glfw.MOUSE_BUTTON_LEFT:
            polygon.append((x, y))
            draw_circle(x, y, 5, COLOR_WHITE)
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            draw_polygon(polygon, COLOR_POLYGON_FILL)

def key_callback(window, key, scancode, action, mods):
    global framebuffer, polygon
    if key == glfw.KEY_R and action == glfw.PRESS:
        framebuffer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        polygon = []

if __name__ == "__main__":
    if not glfw.init():
        exit()
    window = glfw.create_window(400, 400, "Polygon Rasterization", None, None)
    glfw.make_context_current(window)
    WIDTH, HEIGHT = glfw.get_framebuffer_size(window)
    framebuffer_size_callback(window, WIDTH, HEIGHT)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_key_callback(window, key_callback)

    while not glfw.window_should_close(window):
        display()
        glfw.poll_events()
    glfw.terminate()

