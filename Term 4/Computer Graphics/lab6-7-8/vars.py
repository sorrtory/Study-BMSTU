from Angle import Angle

### Configuration parameters ###
# Torus optimization parameters
OPTIMIZE_USE_DL = True      # Use Display Lists for rendering
OPTIMIZE_USE_VA = True      # Use Vertex Array for rendering
OPTIMIZE_LIGHT = False      # Combine ambient and diffuse lighting
OPTIMIZE_USE_VAI = False    # Use VA with indices for rendering

USE_SHADERS = False         # Use shaders for rendering Torus

# Scene parameters
scene_Angle = Angle(35.264, 45)  # Isometric view
scene_Scale = 0.8
scene_Translate = [0.0, 0.0, -3.0]  # Translate the scene
animation = True

# Axes parameters
Axes_show = True
Axes_DL = None

# Light parameters
Light_Enabled = True

# Bounding box parameters
Bounds_show = True
Bounds_min = [-1.0, -1.0, -1.0]
Bounds_max = [1.0, 1.0, 1.0]
Bounds_DL = None

# Torus parameters
Torus_wirerame = False
Torus_use_texture = True
Torus_VAO = None
Torus_Default_Velocity = [0.00005, 0.00012, 0.00009]
Torus_Shader_Program = None

My_Torus = None  # Torus controlling by user

# Lighting configuration
light_presets = [
    # Format: (position, ambient, diffuse, specular, light_model_ambient)
    # Preset 0: Natural daylight
    ([1.0, 1.0, 1.0, 0],  # Directional light from top-right-front
     [0.1, 0.1, 0.1, 1.0],  # Ambient
     [0.9, 0.9, 0.8, 1.0],  # Diffuse (slightly warm)
     [1.0, 1.0, 1.0, 1.0],  # Specular
     [0.2, 0.2, 0.2, 1.0]),  # Global ambient

    # Preset 1: Studio lighting
    ([0.5, 1.0, 0.7, 0],
     [0.15, 0.15, 0.15, 1.0],
     [0.8, 0.8, 0.8, 1.0],
     [1.0, 1.0, 1.0, 1.0],
     [0.15, 0.15, 0.15, 1.0]),

    # Preset 2: Warm sunset
    ([0.8, 0.3, -0.5, 0],
     [0.2, 0.1, 0.1, 1.0],
     [0.9, 0.6, 0.4, 1.0],
     [1.0, 0.8, 0.6, 1.0],
     [0.15, 0.1, 0.1, 1.0]),

    # Preset 3: Cool blue
    ([-0.5, 0.5, 1.0, 0],
     [0.05, 0.05, 0.1, 1.0],
     [0.5, 0.5, 0.9, 1.0],
     [0.8, 0.8, 1.0, 1.0],
     [0.05, 0.05, 0.1, 1.0]),

    # Preset 4: Point light
    ([0.0, 0.0, 1.0, 1],  # Positional light
     [0.05, 0.05, 0.05, 1.0],
     [0.9, 0.9, 0.9, 1.0],
     [1.0, 1.0, 1.0, 1.0],
     [0.1, 0.1, 0.1, 1.0])
]

light_index = 0

# Material properties
material_presets = [
    # Brass-like
    [0.33, 0.22, 0.03, 1.0],  # Ambient
    [0.78, 0.57, 0.11, 1.0],  # Diffuse
    [0.99, 0.91, 0.81, 1.0],  # Specular
    27.8,                     # Shininess

    # Red plastic
    [0.3, 0.0, 0.0, 1.0],
    [0.6, 0.1, 0.1, 1.0],
    [0.8, 0.6, 0.6, 1.0],
    32.0,

    # Emerald
    [0.0215, 0.1745, 0.0215, 1.0],
    [0.07568, 0.61424, 0.07568, 1.0],
    [0.633, 0.727811, 0.633, 1.0],
    76.8
]

# Combine ambient and diffuse for material presets
combined_ambient_diffuse = [
    [ambient[i] + diffuse[i] for i in range(4)]
    for ambient, diffuse in zip(material_presets[0::4], material_presets[1::4])
]

material_index = 0

def get_combined_ambient_diffuse():
    return combined_ambient_diffuse[material_index]

def get_material_properties():
    offset = material_index * 4
    return (
        material_presets[offset],
        material_presets[offset + 1],
        material_presets[offset + 2],
        material_presets[offset + 3]
    )

