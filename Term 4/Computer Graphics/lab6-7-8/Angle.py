class Angle:
    """
    Angles in degrees. 
    Cannot be negative or greater than 360.
    """

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        self._update()

    @staticmethod
    def updated(angle, delta=0):
        angle += delta
        if angle >= 360:
            angle -= 360
        elif angle < 0:
            angle += 360
        return angle

    def _update(self):
        self.x = Angle.updated(self.x)
        self.y = Angle.updated(self.y)
        self.z = Angle.updated(self.z)

    def update_x(self, dx):
        self.x = Angle.updated(self.x, dx)

    def update_y(self, dy):
        self.y = Angle.updated(self.y, dy)

    def update_z(self, dz):
        self.z = Angle.updated(self.z, dz)

    def __add__(self, other):
        if isinstance(other, Angle):
            return Angle(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Angle):
            return Angle(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __str__(self):
        return f"Angle(x={self.x}, y={self.y})"

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise IndexError("Index out of range for Angle object.")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError("Index out of range for Angle object.")

    def __len__(self):
        return 3

    def __iter__(self):
        return iter((self.x, self.y, self.z))