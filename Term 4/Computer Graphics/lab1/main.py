import glfw
from OpenGL.GL import *
delta = 0.1
old_delta = 0
angle = 0
posx = 0
posy = 0
size = 0
unit = 0.5
scaleVec = [1, 1, 1]
scaleRatio = 0.1
translateVec = [0, 0, 0]
translateRatio = 0.1
def main():
    if not glfw.init():
        return
    window = glfw.create_window(1000, 640, "Lab1", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    while not glfw.window_should_close(window):
        display(window)
    glfw.destroy_window(window)
    glfw.terminate()


def display(window):
    global angle
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(*translateVec)
    glScalef(*scaleVec)
    glRotatef(angle, 0, 0, 1)
    glBegin(GL_POLYGON)
    glColor3f(0.1,0.1,0.1)  
    offsetx = posx - 0.5*unit
    offsety = posy - unit
    glVertex2f(offsetx,offsety)
    glVertex2f(offsetx + unit,offsety)
    glVertex2f(offsetx + 1.5*unit,offsety + unit)
    glVertex2f(offsetx + unit,offsety + 2*unit)
    glVertex2f(offsetx,offsety + 2*unit)
    glVertex2f(offsetx-0.5*unit,offsety + unit)
    glEnd()

    glPopMatrix()
    angle += delta
    glfw.swap_buffers(window)
    glfw.poll_events()

def key_callback(window, key, scancode, action,
mods):
    global delta
    global old_delta
    global angle
    global translateRatio
    if action == glfw.PRESS:
        if key == glfw.KEY_RIGHT:
            delta = -3
        if key == 263: # glfw.KEY_LEFT
            delta = 3
        # Stop rotating
        if key == glfw.KEY_SPACE:
            if delta == 0:
                delta = old_delta
            else:
                old_delta = delta
                delta = 0


        # Move by X and Y
        if key == glfw.KEY_W:
            translateVec[1] += 1 * translateRatio
        if key == glfw.KEY_A:
            translateVec[0] -= 1 * translateRatio
        if key == glfw.KEY_S:
            translateVec[1] -= 1 * translateRatio
        if key == glfw.KEY_D:
            translateVec[0] += 1 * translateRatio
        
        # Scale X and Y
        if key == glfw.KEY_X:
            scaleVec[0] += scaleRatio
        if key == glfw.KEY_Z:
            scaleVec[0] -= scaleRatio
        if key == glfw.KEY_C:
            scaleVec[1] -= scaleRatio
        if key == glfw.KEY_V:
            scaleVec[1] += scaleRatio
        

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, 1)

def scroll_callback(window, xoffset, yoffset):
    global size
    if (xoffset > 0):
        size -= yoffset/10
    else:
        size += yoffset/10


if __name__ == "__main__":
    main()