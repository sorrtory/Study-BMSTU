# This program is a silly OpenGL app that renders torus in 3D space.
# User can manipulate torus's position, rotation, and scale.
# Also there is a lighting system and a texture mapping.
# Some optimizations are included too (vars.py contains settings).

import time
# Window manager required `sudo apt install libglfw3-dev`
import glfw
from OpenGL.GL import *
from math import cos, sin, pi, sqrt
from PIL import Image
import numpy as np

# Canvas letters `sudo apt-get install mesa-utils`
from OpenGL.GLUT import glutInit, glutBitmapCharacter, GLUT_BITMAP_HELVETICA_12

from Angle import Angle
from Torus import Torus

import vars
import callbacks
import shaders
import matrices


### Rendering functions ###

def setup_lighting():
    if not vars.Light_Enabled:
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glDisable(GL_COLOR_MATERIAL)
        return

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Get current light configuration
    pos, amb, diff, spec, global_amb = vars.light_presets[vars.light_index]

    # Set up light 0 (main light)
    glLightfv(GL_LIGHT0, GL_POSITION, pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, amb)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diff)
    glLightfv(GL_LIGHT0, GL_SPECULAR, spec)

    # Set global ambient light
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, global_amb)

    mat_amb, mat_diff, mat_spec, mat_shininess = vars.get_material_properties()

    if vars.OPTIMIZE_LIGHT:
        combined_amb_and_diff = vars.get_combined_ambient_diffuse()
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        glColor4f(*combined_amb_and_diff)
    else:
        glMaterialfv(GL_FRONT, GL_AMBIENT, mat_amb)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diff)

    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_spec)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)


def load_texture(path='texture.bmp'):
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

    vars.My_Torus.texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, vars.My_Torus.texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)


def draw_axes(length=0.5, x=0, y=0, z=0):
    if not vars.Axes_show:
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
    glDisable(GL_LIGHTING)
    glColor3f(0.7, 0.7, 0.7)
    glLineWidth(1.0)
    glBegin(GL_LINES)

    # Draw the bounding box edges
    for x in [vars.Bounds_min[0], vars.Bounds_max[0]]:
        for y in [vars.Bounds_min[1], vars.Bounds_max[1]]:
            glVertex3f(x, y, vars.Bounds_min[2])
            glVertex3f(x, y, vars.Bounds_max[2])

    for x in [vars.Bounds_min[0], vars.Bounds_max[0]]:
        for z in [vars.Bounds_min[2], vars.Bounds_max[2]]:
            glVertex3f(x, vars.Bounds_min[1], z)
            glVertex3f(x, vars.Bounds_max[1], z)

    for y in [vars.Bounds_min[1], vars.Bounds_max[1]]:
        for z in [vars.Bounds_min[2], vars.Bounds_max[2]]:
            glVertex3f(vars.Bounds_min[0], y, z)
            glVertex3f(vars.Bounds_max[0], y, z)

    glEnd()
    glEnable(GL_LIGHTING)


def draw_light_marker():
    glDisable(GL_LIGHTING)
    glPointSize(10)
    glBegin(GL_POINTS)
    pos = vars.light_presets[vars.light_index][0]
    if pos[3] == 0:  # Directional light
        glColor3f(1.0, 1.0, 0.0)  # Yellow
    else:            # Positional light
        glColor3f(1.0, 0.5, 0.0)  # Orange
    glVertex3f(pos[0], pos[1], pos[2])
    glEnd()
    glEnable(GL_LIGHTING)


def animate_torus():
    """
    Bounce from the walls and rotate.
    """
    for i in range(3):
        vars.My_Torus.position[i] += vars.My_Torus.velocity[i]
        check_collision_and_reflect(i, vars.My_Torus.R + vars.My_Torus.r)


def check_collision_and_reflect(axis_id, radius):
    """
    See torus is a sphere actually.
    """
    if vars.My_Torus.position[axis_id] - radius < vars.Bounds_min[axis_id]:
        # Bounce
        vars.My_Torus.position[axis_id] = vars.Bounds_min[axis_id] + radius
        vars.My_Torus.velocity[axis_id] = abs(vars.My_Torus.velocity[axis_id])
        # Reflect with rotation
        normal = np.zeros(3)
        normal[axis_id] = -1
        vars.My_Torus.rotation = apply_rotation_on_bounce(vars.My_Torus.velocity,
                                                          normal, vars.My_Torus.rotation)
    elif vars.My_Torus.position[axis_id] + radius > vars.Bounds_max[axis_id]:
        # Bounce
        vars.My_Torus.position[axis_id] = vars.Bounds_max[axis_id] - radius
        vars.My_Torus.velocity[axis_id] = -abs(vars.My_Torus.velocity[axis_id])
        # Reflect with rotation
        normal = np.zeros(3)
        normal[axis_id] = 1
        vars.My_Torus.rotation = apply_rotation_on_bounce(vars.My_Torus.velocity,
                                                          normal, vars.My_Torus.rotation)


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
        # Add to rotation angles (vars.scaled)
        angle += axis * spin_speed
    return Angle(angle[0], angle[1], angle[2])


def set_projection():
    # Apply rotation to the entire scene
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Set up perspective projection
    fov = 45.0  # Field of view in degrees
    aspect = 1.0  # Aspect ratio (width / height)
    near = 0.1  # Near clipping plane
    far = 10.0  # Far clipping plane

    matrix = matrices.perspective_projection(fov, aspect, near, far)
    glMultMatrixf(matrix)

    glTranslatef(*vars.scene_Translate)  # Move back to see the torus

    # Just good matrices and all. Which one to use - depends on the task
    # glOrtho(-2, 2, -2, 2, -10, 10)  # Wider view area. Disables Z
    # glFrustum(-2, 2, -2, 2, 0.1, 10)  # Perspective projection

    glMatrixMode(GL_MODELVIEW)


def compile_models():
    """
    Compiles the torus into a display list for faster rendering.
    """

    # Compile torus into a display list
    # Well, I calculate it anyway
    vars.My_Torus.display_list = glGenLists(1)
    glNewList(vars.My_Torus.display_list, GL_COMPILE)
    if vars.OPTIMIZE_USE_VA:
        if vars.OPTIMIZE_USE_VAI:
            vars.My_Torus.generate2()
            vars.My_Torus.draw_vertices_indices()
        else:
            vars.My_Torus.generate()
            vars.My_Torus.draw_vertices()
    else:
        vars.My_Torus.draw()
        if vars.OPTIMIZE_USE_VAI:
            vars.My_Torus.generate2()
        else:
            if vars.OPTIMIZE_USE_VA:
                vars.My_Torus.generate()
    glEndList()

    # Compile bounds into a display list
    vars.Bounds_DL = glGenLists(1)
    glNewList(vars.Bounds_DL, GL_COMPILE)
    draw_bounds()
    glEndList()

    # Compile axes into a display list
    vars.Axes_DL = glGenLists(1)
    glNewList(vars.Axes_DL, GL_COMPILE)
    draw_axes()
    glEndList()


def display(window):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    # ---- Draw scene ---
    glScalef(vars.scene_Scale, vars.scene_Scale, vars.scene_Scale)

    # Apply scene rotation
    glRotatef(vars.scene_Angle.x, 1, 0, 0)
    glRotatef(vars.scene_Angle.y, 0, 1, 0)

    # Draw axes, bounds, and light marker
    draw_light_marker()
    if vars.Axes_show:
        glCallList(vars.Axes_DL)
    if vars.Bounds_show:
       glCallList(vars.Bounds_DL)

    # ---- Draw torus ---
    if vars.USE_SHADERS:
        draw_torus_shaders()
        # Draw torus axes
        glTranslatef(*vars.My_Torus.position)
        glScalef(*vars.My_Torus.scale)
        glScalef(0.5, 0.5, 0.5)
        glCallList(vars.Axes_DL)
    else:
        setup_lighting()
        # Derive scene properties
        glTranslatef(*vars.My_Torus.position)
        glScalef(*vars.My_Torus.scale)

        # Draw torus axes
        glPushMatrix()
        glScalef(0.5, 0.5, 0.5)
        glCallList(vars.Axes_DL)
        glPopMatrix()

        # Apply torus rotation independently
        glRotatef(vars.My_Torus.rotation.x, 1, 0, 0)
        glRotatef(vars.My_Torus.rotation.y, 0, 1, 0)

        if vars.Torus_use_texture and vars.My_Torus.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, vars.My_Torus.texture_id)
        else:
            glDisable(GL_TEXTURE_2D)
            # Set material color (without texture)
            # But light overrides it :(
            glColor3f(*vars.My_Torus.color)

        # Draw the torus
        if vars.OPTIMIZE_USE_DL:
            glCallList(vars.My_Torus.display_list)
        else:
            if vars.OPTIMIZE_USE_VA:
                if vars.OPTIMIZE_USE_VAI:
                    vars.My_Torus.draw_vertices_indices()
                else:
                    vars.My_Torus.draw_vertices()
            else:
                vars.My_Torus.draw()

    glfw.swap_buffers(window)
    glfw.poll_events()


def launch_shaders(program, vao, model, view, projection):
    glUseProgram(program)

    # Pass vars to shaders
    # Matrices
    glUniformMatrix4fv(glGetUniformLocation(program, "model"), 1, GL_FALSE,
                       model)
    glUniformMatrix4fv(glGetUniformLocation(program, "view"), 1, GL_FALSE,
                       view)
    glUniformMatrix4fv(glGetUniformLocation(program, "projection"), 1, GL_FALSE,
                       projection)

    # Position
    glUniform3fv(glGetUniformLocation(program, "viewPos"), 1, [0, 0, 0])

    # Texture
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, vars.My_Torus.texture_id)
    glUniform1i(glGetUniformLocation(program, "texture1"), 0)
    glUniform1i(glGetUniformLocation(program, "useTexture"),
                vars.Torus_use_texture)

    # Lighting
    pos, amb, diff, spec, global_amb = vars.light_presets[vars.light_index]
    glUniform3fv(glGetUniformLocation(program, "lightPos"), 1, pos[:3])
    glUniform4fv(glGetUniformLocation(program, "ambient"), 1, amb)
    glUniform4fv(glGetUniformLocation(program, "diffuse"), 1, diff)
    glUniform4fv(glGetUniformLocation(program, "specular"), 1, spec)

    # Material
    mat_amb, mat_diff, mat_spec, mat_shininess = vars.get_material_properties()
    glUniform4fv(glGetUniformLocation(program, "matAmbient"), 1, mat_amb)
    glUniform4fv(glGetUniformLocation(program, "matDiffuse"), 1, mat_diff)
    glUniform4fv(glGetUniformLocation(program, "matSpecular"), 1, mat_spec)
    glUniform1f(glGetUniformLocation(program, "shininess"), mat_shininess)

    # Draw
    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLE_STRIP, len(vars.My_Torus.indices),
                   GL_UNSIGNED_INT, None)

    glBindVertexArray(0)
    glUseProgram(0)


def draw_torus_shaders():
    # View matrix
    scene_rotation = matrices.glrotatef(vars.scene_Angle.x, 1, 0, 0) @ \
        matrices.glrotatef(vars.scene_Angle.y, 0, 1, 0)
    scene_translation = matrices.translate(np.array(vars.scene_Translate,
                                                    dtype=np.float32))
    scene_scale = matrices.scale(vars.scene_Scale)
    view = scene_rotation.T @ scene_scale @ scene_translation

    # Projection matrix
    projection = matrices.perspective_projection(45.0, 1.0, 0.1, 10.0)

    # Model matrix
    # Why default rotation doesn't work?
    # torus_rotation = matrices.rotate(vars.My_Torus.rotation.x) @ matrices.rotate(vars.My_Torus.rotation.y)
    torus_rotation = matrices.glrotatef(vars.My_Torus.rotation.x, 1, 0, 0) @ \
        matrices.glrotatef(vars.My_Torus.rotation.y, 0, 1, 0)
    torus_position = matrices.translate(
        np.array(vars.My_Torus.position, dtype=np.float32))
    torus_scale = matrices.scale(
        np.array(vars.My_Torus.scale, dtype=np.float32))
    model = torus_rotation.T @ torus_scale @ torus_position

    # Render the scene
    launch_shaders(vars.Torus_Shader_Program, vars.Torus_VAO,
                   model,
                   view,
                   projection)


def compile_shaders():
    vars.My_Torus.generate2()
    vars.Torus_VAO = shaders.create_vao(vars.My_Torus)
    vars.Torus_Shader_Program = shaders.create_shader_program()


def main():
    # Set up timer
    frame_count = 0
    last_time = time.time()

    if not glfw.init():
        return

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
    glfw.set_key_callback(window, callbacks.key_callback)
    glfw.set_scroll_callback(window, callbacks.scroll_callback)
    width, height = glfw.get_framebuffer_size(window)

    # Check for viewport size
    viewport_ok = width == Window_Height and height == Window_Width
    # Print OpenGL info
    print("###### Info ######")
    print(f"[[{"OK" if viewport_ok else "PROBLEMS"}]]", end="")
    print(f". Framebuffer size: {width}x{height}; "
          f"glViewport: {glGetIntegerv(GL_VIEWPORT)}")

    print("OpenGL Version: ", glGetString(GL_VERSION).decode())
    print("Vendor: ", glGetString(GL_VENDOR).decode())
    print("Renderer: ", glGetString(GL_RENDERER).decode())
    print("GLSL Version: ", glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
    print("######")

    # Initialize OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    # Salute to macs and other strange resolutions like 3200x2000
    if not viewport_ok:
        Window_Height *= 2
        Window_Width *= 2
    glViewport(0, 0, Window_Height, Window_Width)

    # Load closest texture for torus
    texture = __file__[:__file__.rfind("/")+1] + 'texture.bmp'
    load_texture(texture)

    # Set up the models
    if vars.USE_SHADERS:
        compile_shaders()

    # Set projection matrix
    set_projection()

    # Set up display lists for torus, bounds, and axes
    compile_models()
    # I do not delete display lists ...

    # Main loop
    while not glfw.window_should_close(window):
        if vars.animation:
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
    vars.My_Torus = Torus(0.2, 0.1)
    vars.My_Torus.velocity = [0.0001, 0.00012, 0.00009]
    main()
