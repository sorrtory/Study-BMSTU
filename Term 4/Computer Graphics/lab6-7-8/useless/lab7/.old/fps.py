import glfw
from OpenGL.GL import *
import time

def main():
    if not glfw.init():
        return
    window = glfw.create_window(640, 480, "FPS Counter", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    frame_count = 0
    last_time = time.time()

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # FPS counting
        frame_count += 1
        current_time = time.time()
        elapsed = current_time - last_time
        if elapsed >= 1.0:
            print(f"FPS: {frame_count}")
            frame_count = 0
            last_time = current_time

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
