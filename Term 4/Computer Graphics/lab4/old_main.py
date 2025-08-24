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
def resize_framebuffer(new_width, new_height):
    global framebuffer, WIDTH, HEIGHT, polygon
    
    # Calculate scaling factors
    x_scale = new_width / WIDTH
    y_scale = new_height / HEIGHT
    
    # Scale the polygon coordinates
    polygon = [(int(x * x_scale), int(y * y_scale)) for x, y in polygon]
    
    np.resize(framebuffer, (new_height, new_width, 3))
    # # Create a new framebuffer with the new size
    # new_framebuffer = np.zeros((new_height, new_width, 3), dtype=np.uint8)

    # # Interpolate each color channel separately for rows
    # for y in range(new_height):
    #     old_y = int(y / y_scale)
    #     if old_y < HEIGHT:
    #         for channel in range(3):  # RGB channels
    #             new_framebuffer[y, :, channel] = np.interp(
    #                 np.arange(new_width), 
    #                 np.arange(WIDTH), 
    #                 framebuffer[old_y, :, channel]
    #             )
    
    # # Interpolate each color channel separately for columns
    # framebuffer = np.zeros((new_height, new_width, 3), dtype=np.uint8)
    # for x in range(new_width):
    #     old_x = int(x / x_scale)
    #     if old_x < WIDTH:
    #         for channel in range(3):  # RGB channels
    #             framebuffer[:, x, channel] = np.interp(
    #                 np.arange(new_height), 
    #                 np.arange(HEIGHT), 
    #                 new_framebuffer[:, old_x, channel]
    #             )

    # Update framebuffer and window size
    WIDTH, HEIGHT = new_width, new_height
    
def framebuffer_size_callback(window, new_width, new_height):
    global WIDTH, HEIGHT, framebuffer, polygon
    WIDTH, HEIGHT = new_width, new_height
    framebuffer = np.resize(framebuffer, (HEIGHT, WIDTH, 3))
    glViewport(0, 0, WIDTH, HEIGHT)

# Function to handle framebuffer resizing
# def framebuffer_size_callback(window, width, height):
    # global framebuffer, WIDTH, HEIGHT
    # Update window dimensions
    # WIDTH, HEIGHT = width, height

    # Resize the framebuffer array to match the new window size
    # resize_framebuffer(width, height)
    
    # framebuffer = np.ones((width, height , 3), dtype=np.float32)
    # framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    # framebuffer = np.resize(framebuffer, (height, width, 3))
    # Adjust the OpenGL viewport to match the new window size
    # glViewport(0, 0, width, height)

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
        # seed_x, seed_y = polygon[0]
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
        
        # polygon = []  # Reset the polygon for new input

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
    window = glfw.create_window(400, 400, "Polygon Rasterization", None, None)
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
