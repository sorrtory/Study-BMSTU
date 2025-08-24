# Custom matrices for OpenGL
# In homogeneous coordinates then

import numpy as np
from OpenGL.GL import glLoadMatrixf, glMultMatrixf


def rotation_matrix_x(angle):
    rad = np.radians(angle)
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(rad), -np.sin(rad), 0],
        [0, np.sin(rad), np.cos(rad), 0],
        [0, 0, 0, 1]
    ])


def rotation_matrix_y(angle):
    rad = np.radians(angle)
    return np.array([
        [np.cos(rad), 0, np.sin(rad), 0],
        [0, 1, 0, 0],
        [-np.sin(rad), 0, np.cos(rad), 0],
        [0, 0, 0, 1]
    ])

def rotation_matrix_z(angle):
    rad = np.radians(angle)
    return np.array([
        [np.cos(rad), -np.sin(rad), 0, 0],
        [np.sin(rad), np.cos(rad), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])


def rotate(object_Angle_X=0, object_Angle_Y=0, object_Angle_Z=0):
    # Compute matrices
    Rx = rotation_matrix_x(object_Angle_X % 360)
    Ry = rotation_matrix_y(object_Angle_Y % 360)
    Rz = rotation_matrix_z(object_Angle_Z % 360)

    # Multiply in the new order (Y first, then X)
    new_rotation_matrix = np.dot(Ry, Rx)
    new_rotation_matrix = np.dot(Rz, new_rotation_matrix)
    return np.array(new_rotation_matrix, dtype=np.float32)
    


def ortho_projection(Bounds_min, Bounds_max, near=0.1, far=10):
    """
    My gluOrtho2D function to fit in the bounds
    """
    # Orthographic projection matrix manually constructed
    proj = np.identity(4, dtype=np.float32)
    proj[0][0] = 1.0 / (Bounds_max[0] - Bounds_min[0])
    proj[1][1] = 1.0 / (Bounds_max[1] - Bounds_min[1])
    proj[2][2] = -2.0 / (far - near)
    proj[3][2] = -(far + near) / (far - near)
    proj[3][3] = 1.0
    # Transpose because OpenGL expects column-major order
    return np.transpose(proj)


def perspective_projection(fov, aspect, near=0.1, far=10):
    """
    My gluPerspectivef function

    https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml
    """
    # Perspective projection matrix manually constructed
    proj = np.zeros((4, 4), dtype=np.float32)
    f = 1.0 / np.tan(np.radians(fov) / 2.0)
    proj[0][0] = f / aspect
    proj[1][1] = f
    proj[2][2] = (far + near) / (near - far)
    proj[2][3] = (2 * far * near) / (near - far)
    proj[3][2] = -1.0

    # Transpose because OpenGL expects column-major order
    return np.transpose(proj)

def look_at(eye, center, up):
    """
    My gluLookAt function

    https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml
    """
    f = center - eye
    f /= np.linalg.norm(f)
    s = np.cross(f, up)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)

    # Create the view matrix
    view = np.identity(4, dtype=np.float32)
    view[0][:3] = s
    view[1][:3] = u
    view[2][:3] = -f
    view[3][:3] = -np.dot(view[:3, :3], eye)

    # Transpose because OpenGL expects column-major order
    return np.transpose(view)

def translate(translation):
    translation_matrix = np.identity(4, dtype=np.float32)
    translation_matrix[3][:3] = translation
    return translation_matrix

def scale(scale):
    if not isinstance(scale, (list, np.ndarray)):
        scale = [scale, scale, scale]

    scale_matrix = np.identity(4, dtype=np.float32)
    scale_matrix[0][0] = scale[0]
    scale_matrix[1][1] = scale[1]
    scale_matrix[2][2] = scale[2]
    return scale_matrix

def glrotatef(angle, x, y, z):
    """
    Mimics the behavior of the OpenGL function glRotatef.

    Parameters:
    - angle: The angle of rotation in degrees.
    - x, y, z: The axis of rotation (should be a unit vector).
    """
    axis = np.array([x, y, z], dtype=np.float32)
    axis /= np.linalg.norm(axis)  # Normalize the axis
    x, y, z = axis

    rad = np.radians(angle)
    c = np.cos(rad)
    s = np.sin(rad)
    t = 1 - c

    # Rotation matrix around arbitrary axis
    rotation_matrix = np.array([
        [t * x * x + c,     t * x * y - s * z, t * x * z + s * y, 0],
        [t * x * y + s * z, t * y * y + c,     t * y * z - s * x, 0],
        [t * x * z - s * y, t * y * z + s * x, t * z * z + c,     0],
        [0,                 0,                 0,                 1]
    ], dtype=np.float32)

    # Apply the rotation matrix using glMultMatrixf
    return rotation_matrix