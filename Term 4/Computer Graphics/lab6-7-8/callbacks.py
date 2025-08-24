import glfw
from Angle import Angle
from OpenGL.GL import *
from vars import *
import vars

def key_callback(window, key, scancode, action, mods):
    """
    Handles key press and key repeat events for controlling the OpenGL scene.

    Keybindings:
        General:
            - SPACE: Toggle animation on/off.
            - R: Reset torus position, velocity, vars.scale, and scene rotation.
            - ESCAPE: Close the program.

        Scene Rotation:
            Axes are fucked. Depends on the camera position.
            No Z axis. Orho projection.
            - H: Rotate the scene left by y
            - L: Rotate the scene right by -y
            - J: Rotate the scene down by x
            - K: Rotate the scene up by -x

        Torus Rotation: 
            Axes are fucked. Depends on the torus position.
            No Z axis. I don't have so many keys.
            - RIGHT: Rotate the torus right by y
            - LEFT: Rotate the torus right by -y
            - UP: Rotate the torus up by x
            - DOWN: Rotate the torus down by -x

        Torus Position:
            - W: Move the torus up along the y-axis.
            - S: Move the torus down along the y-axis.
            - A: Move the torus left along the x-axis.
            - D: Move the torus right along the x-axis.
            - Q: Move the torus forward along the z-axis.
            - E: Move the torus backward along the z-axis.

        Torus vars.scale:
            - Z: Increase the torus vars.scale by 10%.
            - X: Decrease the torus vars.scale by 10%.

        Polygon Mode:
            - M: Toggle between wireframe and filled polygon rendering.

        Texture:
            - T: Toggle texture usage on/off.

        Animation Speed:
            - EQUAL (=): Increase the animation speed by 10%.
            - MINUS (-): Decrease the animation speed by 10%.

        Light and Material Presets:
            - 0: Toggle light on/off.
            - 1-5: Select light presets (0-4).
            - 6-8: Select material presets (0-2).

        Display Toggles:
            - B: Toggle bounding box display on/off.
            - V: Toggle axes display on/off.
    """
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_SPACE:
            vars.animation = not vars.animation
        elif key == glfw.KEY_R:
            # Reset torus position and velocity and projection
            vars.My_Torus.position = [0.0, 0.0, 0.0]
            vars.My_Torus.velocity = vars.Torus_Default_Velocity
            vars.My_Torus.scale = [1.0, 1.0, 1.0]
            vars.My_Torus.rotation = Angle(0, 0)
            vars.scene_Angle = Angle(0, 0)

        # ----- Scene rotation ----
        elif key == glfw.KEY_H:
            vars.scene_Angle.update_y(3)
        elif key == glfw.KEY_L:
            vars.scene_Angle.update_y(-3)
        elif key == glfw.KEY_J:
            vars.scene_Angle.update_x(-3)
        elif key == glfw.KEY_K:
            vars.scene_Angle.update_x(3)

        # ----- Torus rotation ----
        elif key == glfw.KEY_RIGHT:
            vars.My_Torus.rotation.update_y(3)
        elif key == glfw.KEY_LEFT:
            vars.My_Torus.rotation.update_y(-3)
        elif key == glfw.KEY_UP:
            vars.My_Torus.rotation.update_x(3)
        elif key == glfw.KEY_DOWN:
            vars.My_Torus.rotation.update_x(-3)

        # ----- Torus position ----
        elif key == glfw.KEY_W:
            vars.My_Torus.position[1] += 0.1
        elif key == glfw.KEY_S:
            vars.My_Torus.position[1] -= 0.1
        elif key == glfw.KEY_A:
            vars.My_Torus.position[0] -= 0.1
        elif key == glfw.KEY_D:
            vars.My_Torus.position[0] += 0.1
        elif key == glfw.KEY_Q:
            vars.My_Torus.position[2] += 0.1
        elif key == glfw.KEY_E:
            vars.My_Torus.position[2] -= 0.1

        # ----- Torus vars.scale ----
        elif key == glfw.KEY_Z:
            vars.My_Torus.scale = [v * 1.1 for v in vars.My_Torus.scale]
        elif key == glfw.KEY_X:
            vars.My_Torus.scale = [v * 0.9 for v in vars.My_Torus.scale]

        # ----- Polygon toggle ----
        elif key == glfw.KEY_M:
            vars.Torus_wirerame = not vars.Torus_wirerame
            glPolygonMode(GL_FRONT_AND_BACK,
                          GL_LINE if vars.Torus_wirerame else GL_FILL)

        # ----- Texture toggle ----
        elif key == glfw.KEY_T:
            vars.Torus_use_texture = not vars.Torus_use_texture

        # ----- Animation speed ----
        elif key == glfw.KEY_EQUAL:
            vars.My_Torus.velocity = [v * 1.1 for v in vars.My_Torus.velocity]
        elif key == glfw.KEY_MINUS:
            vars.My_Torus.velocity = [v * 0.9 for v in vars.My_Torus.velocity]

        # ----- Light and material presets ----
        elif key == glfw.KEY_1:
            vars.light_index = 0
        elif key == glfw.KEY_2:
            vars.light_index = 1
        elif key == glfw.KEY_3:
            vars.light_index = 2
        elif key == glfw.KEY_4:
            vars.light_index = 3
        elif key == glfw.KEY_5:
            vars.light_index = 4
        elif key == glfw.KEY_6:
            vars.material_index = 0
        elif key == glfw.KEY_7:
            vars.material_index = 1
        elif key == glfw.KEY_8:
            vars.material_index = 2

        # ----- Toggle light -----
        elif key == glfw.KEY_0:
            vars.Light_Enabled = not vars.Light_Enabled

        # ----- Toggle bounds display ----
        elif key == glfw.KEY_B:
            vars.Bounds_show = not vars.Bounds_show

        # ----- Toggle axes display ----
        elif key == glfw.KEY_V:
            vars.Axes_show = not vars.Axes_show

        # ----- Close program ----
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def scroll_callback(window, xoffset, yoffset):
    factor = 1.1 if yoffset > 0 else 0.9
    vars.My_Torus.scale = [v * factor for v in vars.My_Torus.scale]
