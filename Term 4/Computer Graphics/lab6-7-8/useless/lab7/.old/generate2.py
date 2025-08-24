# FUNC to generate torus by triangles like song ho ahk  
def generate2(self, side_count=40, sector_count=20):
    """
    Generates vertices, normals, texture coordinates, and indices for a torus.
    """
    TWO_PI = 2.0 * pi
    vertices = []
    normals = []
    texcoords = []
    indices = []

    side_step = TWO_PI / side_count
    sector_step = TWO_PI / sector_count
    length_inv = 1.0 / self.r  # Inverse of minor radius for normalization

    for i in range(side_count + 1):
        side_angle = pi - i * side_step  # Starting from pi to -pi
        xy = self.r * cos(side_angle)   # r * cos(u)
        z = self.r * sin(side_angle)   # r * sin(u)

        for j in range(sector_count + 1):
            sector_angle = j * sector_step  # Starting from 0 to 2pi

            # Compute vertex position
            x = xy * cos(sector_angle)
            y = xy * sin(sector_angle)

            # Compute normal vector
            nx = x * length_inv
            ny = y * length_inv
            nz = z * length_inv
            normals.append((nx, ny, nz))

            # Shift x & y for vertex position
            x += self.R * cos(sector_angle)  # (R + r * cos(u)) * cos(v)
            y += self.R * sin(sector_angle)  # (R + r * cos(u)) * sin(v)
            vertices.append((x, y, z))

            # Texture coordinates
            s = j / sector_count
            t = i / side_count
            texcoords.append((s, t))

    # Generate indices
    for i in range(side_count):
        k1 = i * (sector_count + 1)       # Beginning of current side
        k2 = k1 + sector_count + 1       # Beginning of next side

        for j in range(sector_count):
            indices.append(k1)
            indices.append(k2)
            indices.append(k1 + 1)        # k1---k2---k1+1

            indices.append(k1 + 1)
            indices.append(k2)
            indices.append(k2 + 1)        # k1+1---k2---k2+1

            k1 += 1
            k2 += 1

    # Convert to numpy arrays
    self.vertices = np.array(vertices, dtype=np.float32)
    self.normals = np.array(normals, dtype=np.float32)
    self.texcoords = np.array(texcoords, dtype=np.float32)
    self.indices = np.array(indices, dtype=np.uint32)