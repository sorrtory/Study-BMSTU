import glfw
from OpenGL.GL import *
import numpy as np

# Параметры окна
WIDTH, HEIGHT = 800, 800
framebuffer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
polygon = []  # Храним точки многоугольника
polygons = []  # Храним многоугольники
# Global color definitions
COLOR_WHITE = (255, 255, 255)
COLOR_POLYGON_FILL = (255, 0, 0)

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
def flood_fill(x, y, fill_color, boundary_color):
    stack = [(x, y)]
    filled_pixels = 0
    while stack:
        x, y = stack.pop()
        if 0 <= x < WIDTH and 0 <= y < HEIGHT and not np.array_equal(framebuffer[y, x], fill_color) and not np.array_equal(framebuffer[y, x], boundary_color):
            lx, rx = x, x
            while lx > 0 and not np.array_equal(framebuffer[y, lx - 1], boundary_color):
                lx -= 1
            while rx < WIDTH - 1 and not np.array_equal(framebuffer[y, rx + 1], boundary_color):
                rx += 1
            for i in range(lx, rx + 1):
                plot(i, y, fill_color)
                filled_pixels += 1
                if filled_pixels % 100 == 0:
                    display()
                if i > 0 and y > 0 and not np.array_equal(framebuffer[y - 1, i], boundary_color):
                    stack.append((i, y - 1))
                if i < WIDTH - 1 and y > 0 and not np.array_equal(framebuffer[y - 1, i], boundary_color):
                    stack.append((i, y - 1))
                if i > 0 and y < HEIGHT - 1 and not np.array_equal(framebuffer[y + 1, i], boundary_color):
                    stack.append((i, y + 1))
                if i < WIDTH - 1 and y < HEIGHT - 1 and not np.array_equal(framebuffer[y + 1, i], boundary_color):
                    stack.append((i, y + 1))

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    width, height = glfw.get_framebuffer_size(window)
    glViewport(0, 0, width, height)
    glDrawPixels(WIDTH, HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, framebuffer)
    glfw.swap_buffers(window)


# Function to resize the framebuffer while keeping the existing content using np.interp
def resized_framebuffer(new_width, new_height):
    global framebuffer, WIDTH, HEIGHT
    old_height, old_width, _ = framebuffer.shape
    new_framebuffer = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    scale_x = old_width / new_width
    scale_y = old_height / new_height

    for new_y in range(new_height):
        for new_x in range(new_width):
            old_x = int(round(new_x * scale_x))
            old_y = int(round(new_y * scale_y))
            old_x = min(old_x, old_width - 1)  # Prevent out-of-bounds
            old_y = min(old_y, old_height - 1)

            new_framebuffer[new_y, new_x] = framebuffer[old_y, old_x]

    return new_framebuffer

def resize_framebuffer_keep_pixels(new_width, new_height):
    global framebuffer, WIDTH, HEIGHT
    new_framebuffer = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    min_width = min(WIDTH, new_width)
    min_height = min(HEIGHT, new_height)

    # Copy the overlapping region from the old framebuffer to the new one using a loop
    for y in range(min_height):
        for x in range(min_width):
            if x-1 < WIDTH and y-1 < HEIGHT and x - 1 < new_width and y - 1 < new_height:
                new_framebuffer[y, x] = framebuffer[y, x]

    return framebuffer

def framebuffer_size_callback(window, new_width, new_height):
    global WIDTH, HEIGHT, framebuffer, polygon
    # framebuffer = resized_framebuffer(new_width, new_height)
    framebuffer = resize_framebuffer_keep_pixels(new_width, new_height)
    WIDTH, HEIGHT = new_width, new_height
    glViewport(0, 0, WIDTH, HEIGHT)


def calculate_centroid(polygon):
    x_coords = [p[0] for p in polygon]
    y_coords = [p[1] for p in polygon]
    centroid_x = sum(x_coords) // len(polygon)
    centroid_y = sum(y_coords) // len(polygon)
    return centroid_x, centroid_y

def draw_polygon(polygon, color):
    if len(polygon) > 2:
        # Draw the polygon edges
        for i in range(len(polygon) - 1):
            draw_line(*polygon[i], *polygon[i + 1], COLOR_WHITE)
        draw_line(*polygon[-1], *polygon[0], COLOR_WHITE)
        # Use the first point of the polygon as the seed point for filling
        seed_x, seed_y = calculate_centroid(polygon)
        flood_fill(seed_x, seed_y, color, COLOR_WHITE)

        # Draw the polygon edges
        for i in range(len(polygon) - 1):
            draw_filtered_line(*polygon[i], *polygon[i + 1], COLOR_WHITE)
        draw_filtered_line(*polygon[-1], *polygon[0], COLOR_WHITE)

def mouse_button_callback(window, button, action, mods):
    global polygon
    if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_LEFT:
        # Get the mouse position
        x, y = glfw.get_cursor_pos(window)
        x, y = int(x), HEIGHT - int(y)  # Convert to framebuffer coordinates
        polygon.append((x, y))  # Add the vertex to the polygon
        draw_circle(x, y, 5, COLOR_WHITE)  # Draw a circle at the clicked position
    elif action == glfw.PRESS and button == glfw.MOUSE_BUTTON_RIGHT:
        draw_polygon(polygon, COLOR_POLYGON_FILL)  # Draw the polygon

def key_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_R and action == glfw.PRESS:
        # Очистка экрана при нажатии R
        global framebuffer, polygon
        framebuffer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        polygon = []

# Bresenham's line algorithm with anti-aliasing
def draw_filtered_line(x0, y0, x1, y1, color):
    deltax = abs(x1 - x0)
    deltay = abs(y1 - y0)
    error = 0
    deltaerr = deltay + 1 if deltax >= deltay else deltax + 1
    x, y = x0, y0
    dirx = 1 if x1 > x0 else -1 if x1 < x0 else 0
    diry = 1 if y1 > y0 else -1 if y1 < y0 else 0

    if deltax >= deltay:
        for _ in range(deltax + 1):
            alpha = 1 - (error / (deltax + 1)) if deltax else 1
            plot(x, y, color, alpha)
            x += dirx
            error += deltay
            if error >= deltax + 1:
                y += diry
                error -= deltax + 1
    else:
        for _ in range(deltay + 1):
            alpha = 1 - (error / (deltay + 1)) if deltay else 1
            plot(x, y, color, alpha)
            y += diry
            error += deltax
            if error >= deltay + 1:
                x += dirx
                error -= deltay + 1

if __name__ == "__main__":
    if not glfw.init():
        exit()
    window = glfw.create_window(WIDTH, HEIGHT, "Polygon Rasterization", None, None)
    glfw.make_context_current(window)
    
    # Query the actual framebuffer size
    WIDTH, HEIGHT = glfw.get_framebuffer_size(window)
    framebuffer_size_callback(window, WIDTH, HEIGHT)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    glfw.set_mouse_button_callback(window, mouse_button_callback)
    # Обработчик клавиш для очистки
    glfw.set_key_callback(window, key_callback)
    while not glfw.window_should_close(window):
        display()
        glfw.poll_events()
    glfw.terminate()
