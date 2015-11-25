################################################################################

# TWO DIMENTIONAL VECTOR CLASS

class TwoD:

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return 'TwoD(%s, %s)' % (self.x, self.y)

    def __add__(self, other):
        return TwoD(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return TwoD(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return TwoD(self.x * other, self.y * other)

    def __div__(self, other):
        return TwoD(self.x / other, self.y / other)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __idiv__(self, other):
        if isinstance(other, TwoD):
            self.x /= other.x if other.x else 1
            self.y /= other.y if other.y else 1
        else:
            self.x /= other
            self.y /= other
        return self

    def mag(self):
        return ((self.x ** 2) + (self.y ** 2)) ** 0.5

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def copy(self):
        return TwoD(self.x, self.y)

    def perp(self):
        return TwoD(-self.y, self.x)

    def unit(self):
        return self / self.mag()

    def projection(self, other):
        unit = self.unit()
        return unit * unit.dot(other)
