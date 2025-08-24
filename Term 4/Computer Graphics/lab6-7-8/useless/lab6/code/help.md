### Explanation of Lighting Parameters

1. **`light_position`**: Defines the position or direction of the light source. The first three values `[x, y, z]` specify the position or direction, and the fourth value determines whether the light is positional (`1.0`) or directional (`0.0`).
2. **`light_ambient`**: Controls the ambient light intensity, which is the base light present everywhere in the scene.
3. **`light_diffuse`**: Controls the diffuse light intensity, which depends on the angle between the light and the surface.
4. **`light_specular`**: Controls the specular light intensity, which creates shiny highlights on surfaces.
5. **`material_ambient`**: Defines how much ambient light the material reflects.
6. **`material_diffuse`**: Defines how much diffuse light the material reflects.
7. **`material_specular`**: Defines how much specular light the material reflects.
8. **`material_shininess`**: Controls the size and intensity of the specular highlight (higher values make the highlight smaller and sharper).