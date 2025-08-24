import glfw
from OpenGL.GL import *
import numpy as np
import sys

# --- Глобальные переменные ---
window_width = 800
window_height = 600

subject_polygon = []
clipper_polygon = []
clipped_segments = []

defining_state = 'subject'

EPSILON = 1e-6

# --- Вспомогательные функции ---

def screen_to_world(x, y):
    return x, window_height - y

def get_clipper_normals(polygon):
    normals = []
    num_vertices = len(polygon)
    if num_vertices < 3:
        return []

    for i in range(num_vertices):
        p1 = np.array(polygon[i])
        p2 = np.array(polygon[(i + 1) % num_vertices])
        edge_vector = p2 - p1
        normal = np.array([edge_vector[1], -edge_vector[0]])
        norm_length = np.linalg.norm(normal)
        if norm_length > EPSILON:
            normals.append(normal / norm_length)
        else:
            # Handle zero-length edge case if necessary, e.g., return [] or skip
            return [] # Or handle appropriately
    return normals

def is_convex_and_ccw(polygon):
    n = len(polygon)
    if n < 3:
        return False

    sign = 0
    for i in range(n):
        p1 = np.array(polygon[i])
        p2 = np.array(polygon[(i + 1) % n])
        p3 = np.array(polygon[(i + 2) % n])
        cross_product = np.cross(p2 - p1, p3 - p2)

        if abs(cross_product) > EPSILON:
            current_sign = np.sign(cross_product)
            if sign == 0:
                sign = current_sign
            elif current_sign != sign:
                return False # Not convex or mixed winding order

    return sign >= 0 # CCW or collinear

# --- Алгоритм Кируса-Бека (для внешнего отсечения) ---

def cyrus_beck_exterior_clip_segment(p0_in, p1_in, clipper_vertices, clipper_normals):
    p0 = np.array(p0_in)
    p1 = np.array(p1_in)
    d = p1 - p0

    if np.linalg.norm(d) < EPSILON: # Handle zero-length segment
        return []

    t_lower = 0.0
    t_upper = 1.0

    for i in range(len(clipper_vertices)):
        ni = clipper_normals[i]
        f = np.array(clipper_vertices[i])
        w = p0 - f
        denominator = np.dot(ni, d)
        numerator = np.dot(ni, w)

        if abs(denominator) < EPSILON:
            if numerator < 0: # Parallel and "inside" this edge normal
                 # For exterior clipping, if it's potentially inside *any* edge,
                 # it might be fully contained. We can't simply discard here
                 # like in interior clipping. A segment parallel and "inside"
                 # might still be partially outside if the clipper is concave
                 # (though we assume convex). For convex, if parallel and "inside",
                 # it means the whole line is "inside" or on the edge.
                 # If strictly inside (numerator < -EPSILON), the segment is fully inside.
                 # Let's consider a segment strictly inside as fully clipped away for exterior.
                 if numerator < -EPSILON:
                      return [] # Segment is fully inside relative to this edge plane
                 # else: it's parallel and on the edge or outside.
            # else: Parallel and outside or on edge - doesn't constrain t further
            pass
        else:
            t = -numerator / denominator
            if denominator < 0: # Potential Exit from Exterior (Entering Interior)
                t_lower = max(t_lower, t)
            else: # Potential Entry to Exterior (Leaving Interior)
                t_upper = min(t_upper, t)

    result_segments = []

    # Check if any valid segment remains potentially outside
    # Note: t_lower > t_upper means the standard *interior* segment is non-existent.
    # For exterior clipping, this means the *entire* original segment might be outside.


    if t_lower > t_upper:
         # The segment's line doesn't intersect the interior defined by the clipper
         # in the standard way. This implies the segment is entirely outside.
         result_segments.append((tuple(p0), tuple(p1)))
    elif t_lower < t_upper:
        # Standard CB would keep [t_lower, t_upper]. We want parts outside this.
        # Part from P0 up to t_lower
        if t_lower > 0.0 + EPSILON:
            q0 = tuple(p0)
            q1 = tuple(p0 + t_lower * d)
            result_segments.append((q0, q1))

        # Part from t_upper up to P1
        if t_upper < 1.0 - EPSILON:
            q0 = tuple(p0 + t_upper * d)
            q1 = tuple(p1)
            result_segments.append((q0, q1))
    # else t_lower == t_upper (approximately): Grazing contact or single point intersection
    # In this case, the "interior" segment has zero length.
    # So the exterior parts are [0, t_lower] and [t_upper, 1] which cover the whole line.
    # However, numerical precision might make t_lower slightly > t_upper.
    # The check `t_lower > t_upper` should ideally handle the "completely outside" case.
    # If t_lower is very close to t_upper, the logic above might create tiny/overlapping segments.
    # Let's refine: If t_lower >= t_upper (within EPSILON), consider it fully outside.

    # Refined logic:
    if t_lower >= t_upper - EPSILON:
        # Segment's interior part is zero or negative length -> fully outside
        result_segments = [(tuple(p0), tuple(p1))]
    else: # t_lower < t_upper
        result_segments = [] # Re-calculate safely
        # Part from P0 up to t_lower
        if t_lower > 0.0 + EPSILON:
            q0 = tuple(p0)
            q1 = tuple(p0 + t_lower * d)
            result_segments.append((q0, q1))

        # Part from t_upper up to P1
        if t_upper < 1.0 - EPSILON:
            q0 = tuple(p0 + t_upper * d)
            q1 = tuple(p1)
            result_segments.append((q0, q1))

    return result_segments


def perform_clipping():
    global clipped_segments
    clipped_segments = []

    if len(subject_polygon) < 2 or len(clipper_polygon) < 3:
        return

    # No warning print here, rely on function return value
    if not is_convex_and_ccw(clipper_polygon):
        # Decide behavior: proceed with potential errors or stop?
        # Let's proceed but normals might be wrong.
        pass # Or return

    clipper_normals = get_clipper_normals(clipper_polygon)
    if not clipper_normals:
        return

    num_subject_vertices = len(subject_polygon)
    for i in range(num_subject_vertices):
        p0 = subject_polygon[i]
        p1 = subject_polygon[(i + 1) % num_subject_vertices]

        segments_outside = cyrus_beck_exterior_clip_segment(p0, p1, clipper_polygon, clipper_normals)
        clipped_segments.extend(segments_outside)

# --- Обработчики событий ---

def mouse_button_callback(window, button, action, mods):
    global defining_state, subject_polygon, clipper_polygon
    if action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        world_x, world_y = screen_to_world(x, y)
        point = (world_x, world_y)

        if button == glfw.MOUSE_BUTTON_LEFT:
            if defining_state == 'subject':
                subject_polygon.append(point)
            elif defining_state == 'clipper':
                clipper_polygon.append(point)
                # Optional: check convexity dynamically if desired

        elif button == glfw.MOUSE_BUTTON_RIGHT:
            if defining_state == 'subject':
                if len(subject_polygon) >= 2:
                    defining_state = 'clipper'
            elif defining_state == 'clipper':
                if len(clipper_polygon) >= 3:
                    defining_state = 'done'
                    # Final check before allowing clipping
                    if not is_convex_and_ccw(clipper_polygon):
                        # Handle error state? Or let perform_clipping handle it.
                        pass


def key_callback(window, key, scancode, action, mods):
    global defining_state, subject_polygon, clipper_polygon, clipped_segments
    if action == glfw.PRESS:
        if key == glfw.KEY_C and defining_state == 'done':
            perform_clipping()
        if key == glfw.KEY_R:
            subject_polygon = []
            clipper_polygon = []
            clipped_segments = []
            defining_state = 'subject'


# --- Функции отрисовки ---

def draw_polygon(polygon, color=(1.0, 1.0, 1.0), line_width=1.0, mode=GL_LINE_LOOP):
    if not polygon:
        return
    glColor3f(*color)
    glLineWidth(line_width)
    glBegin(mode)
    for vertex in polygon:
        glVertex2f(*vertex)
    glEnd()

def draw_segments(segments, color=(0.0, 1.0, 0.0), line_width=2.0):
    if not segments:
        return
    glColor3f(*color)
    glLineWidth(line_width)
    glBegin(GL_LINES)
    for seg_start, seg_end in segments:
        glVertex2f(*seg_start)
        glVertex2f(*seg_end)
    glEnd()

def draw_points(points, color=(1.0, 0.0, 0.0), point_size=5.0):
    if not points:
        return
    glColor3f(*color)
    glPointSize(point_size)
    glBegin(GL_POINTS)
    for point in points:
        glVertex2f(*point)
    glEnd()

def setup_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# --- Основная функция ---

def main():
    global window_width, window_height

    if not glfw.init():
        sys.exit("Failed to initialize GLFW")

    window = glfw.create_window(window_width, window_height, "Lab 5 - Exterior Cyrus-Beck Clipping", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Failed to create GLFW window")

    glfw.make_context_current(window)
    glfw.set_window_size_limits(window, 200, 150, glfw.DONT_CARE, glfw.DONT_CARE)

    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_key_callback(window, key_callback)

    def framebuffer_size_callback(window, width, height):
        global window_width, window_height
        if width == 0 or height == 0:
             return
        window_width = width
        window_height = height
        glViewport(0, 0, width, height)
        setup_projection()

    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    glViewport(0, 0, window_width, window_height)
    setup_projection()
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_LINE_SMOOTH) # Optional: smooth lines too
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw subject polygon before clipping or if not clipped yet
        # If clipped, we only draw the resulting segments, not the original subject lines inside
        if not clipped_segments:
             draw_polygon(subject_polygon, color=(0.5, 0.5, 1.0), mode=GL_LINE_LOOP if len(subject_polygon)>2 else GL_LINE_STRIP)
        # Always draw vertices
        draw_points(subject_polygon, color=(0.7, 0.7, 1.0))


        draw_polygon(clipper_polygon, color=(1.0, 1.0, 0.0), mode=GL_LINE_LOOP)
        draw_points(clipper_polygon, color=(1.0, 1.0, 0.5))

        draw_segments(clipped_segments, color=(0.0, 1.0, 0.0), line_width=3.0)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()