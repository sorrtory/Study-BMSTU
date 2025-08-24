# Torus PyOpenGl implementation
# Thanks to https://www.songho.ca/opengl/gl_torus.html

from OpenGL.GL import *
import numpy as np
from math import pi, cos, sin

from Angle import Angle


class Torus:
    def __init__(self, R, r):
        self.R = R  # Major radius
        self.r = r  # Minor radius

        # Torus properties
        self.texture_id = None
        self.color = [1.0, 0.1, 0.4]
        self.scale = [1.0, 1.0, 1.0]
        self.position = [0.0, 0.0, 0.0]
        self.velocity = [0.0, 0.0, 0.0]
        self.rotation = Angle(0, 0)

        # 3d model basically
        self.display_list = None

        # Array List for torus
        self.vertices = None
        self.normals = None
        self.texcoords = None

        # Indices for drawing Array List
        self.indices = None

    def draw(self, side_count=40, sector_count=20):
        """
        Draw torus by GL_TRIANGLE_STRIP
        Parameters:
            R: Radious of the circle
            r: Radius of the tube
        """

        TWO_PI = 2.0 * pi

        for side_index in range(side_count):
            angle0 = side_index * TWO_PI / side_count
            angle1 = (side_index + 1) * TWO_PI / side_count
            cos_angle0, sin_angle0 = cos(angle0), sin(angle0)
            cos_angle1, sin_angle1 = cos(angle1), sin(angle1)
            glBegin(GL_TRIANGLE_STRIP)
            for sector_index in range(sector_count + 1):
                sector_angle = sector_index * TWO_PI / sector_count
                cos_sector = cos(sector_angle)
                sin_sector = sin(sector_angle)

                # Points on ring side_index
                normal_x = cos_angle0 * cos_sector
                normal_y = sin_angle0 * cos_sector
                normal_z = sin_sector
                glNormal3f(normal_x, normal_y, normal_z)
                glTexCoord2f(side_index / side_count,
                             sector_index / sector_count)
                glVertex3f((self.R + self.r * cos_sector) * cos_angle0,
                           (self.R + self.r * cos_sector) * sin_angle0,
                           self.r * sin_sector)

                # Points on ring side_index+1
                normal_x = cos_angle1 * cos_sector
                normal_y = sin_angle1 * cos_sector
                normal_z = sin_sector
                glNormal3f(normal_x, normal_y, normal_z)
                glTexCoord2f((side_index + 1) / side_count,
                             sector_index / sector_count)
                glVertex3f((self.R + self.r * cos_sector) * cos_angle1,
                           (self.R + self.r * cos_sector) * sin_angle1,
                           self.r * sin_sector)
            glEnd()

    def generate(self, side_count=40, sector_count=20):
        """
        Same as draw() but saves vertices, normals, and texture coordinates
        instead of just drawing them.
        """
        TWO_PI = 2.0 * pi
        vertices = []
        normals = []
        texcoords = []

        for side_index in range(side_count):
            angle0 = side_index * TWO_PI / side_count
            angle1 = (side_index + 1) * TWO_PI / side_count
            cos_angle0, sin_angle0 = cos(angle0), sin(angle0)
            cos_angle1, sin_angle1 = cos(angle1), sin(angle1)

            for sector_index in range(sector_count + 1):
                sector_angle = sector_index * TWO_PI / sector_count
                cos_sector = cos(sector_angle)
                sin_sector = sin(sector_angle)

                for (cos_angle, sin_angle) in [(cos_angle0, sin_angle0), 
                                               (cos_angle1, sin_angle1)]:
                    normal_x = cos_angle * cos_sector
                    normal_y = sin_angle * cos_sector
                    normal_z = sin_sector
                    normals.append((normal_x, normal_y, normal_z))
                    texcoords.append(
                        (side_index / side_count, sector_index / sector_count))
                    vertex_x = (self.R + self.r * cos_sector) * cos_angle
                    vertex_y = (self.R + self.r * cos_sector) * sin_angle
                    vertex_z = self.r * sin_sector
                    vertices.append((vertex_x, vertex_y, vertex_z))

        self.vertices = np.array(vertices, dtype=np.float32)
        self.normals = np.array(normals, dtype=np.float32)
        self.texcoords = np.array(texcoords, dtype=np.float32)

    def draw_vertices(self):
        """
        Draw torus using vertex array approach
        Needs to be called after generate()
        """
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glNormalPointer(GL_FLOAT, 0, self.normals)
        glTexCoordPointer(2, GL_FLOAT, 0, self.texcoords)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, len(self.vertices))

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

 

    def generate2(self, side_count=40, sector_count=20):
        """
        Generates vertices, normals, texture coordinates, and indices for a torus.
        Consistent with the original generate() method but using indices.
        """
        TWO_PI = 2.0 * pi
        vertices = []
        normals = []
        texcoords = []
        indices = []

        for side_index in range(side_count + 1):
            angle0 = side_index * TWO_PI / side_count
            cos_angle0, sin_angle0 = cos(angle0), sin(angle0)

            for sector_index in range(sector_count + 1):
                sector_angle = sector_index * TWO_PI / sector_count
                cos_sector = cos(sector_angle)
                sin_sector = sin(sector_angle)

                # Compute vertex position
                vertex_x = (self.R + self.r * cos_sector) * cos_angle0
                vertex_y = (self.R + self.r * cos_sector) * sin_angle0
                vertex_z = self.r * sin_sector
                vertices.append((vertex_x, vertex_y, vertex_z))

                # Compute normal (same as in generate())
                normal_x = cos_angle0 * cos_sector
                normal_y = sin_angle0 * cos_sector
                normal_z = sin_sector
                normals.append((normal_x, normal_y, normal_z))

                # Texture coordinates (same as in generate())
                texcoords.append((side_index / side_count, sector_index / sector_count))

        # Generate indices for GL_TRIANGLE_STRIP
        for i in range(side_count):
            for j in range(sector_count + 1):
                indices.append(i * (sector_count + 1) + j)
                indices.append((i + 1) * (sector_count + 1) + j)

        # Convert to numpy arrays
        self.vertices = np.array(vertices, dtype=np.float32)
        self.normals = np.array(normals, dtype=np.float32)
        self.texcoords = np.array(texcoords, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32)
    
    def draw_vertices_indices(self):
        """
        Draw torus using vertex array approach with indices.
        Needs to be called after generate2()
        """
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glNormalPointer(GL_FLOAT, 0, self.normals)
        glTexCoordPointer(2, GL_FLOAT, 0, self.texcoords)

        glDrawElements(GL_TRIANGLE_STRIP, len(self.indices), GL_UNSIGNED_INT, self.indices)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    def __del__(self):
        # Cleanup display list if it exists
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
        self.display_list = None
