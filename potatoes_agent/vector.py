import math
from functools import reduce


class vector(list):

    def __getslice__(self, i, j):
        try:
            return vector(super(vector, self).__getslice__(i ,j))
        except:
            raise TypeError('vector::FAILURE in __getslice__')

    def __add__(self, other):
        return vector(map(lambda x ,y: x+ y, self, other))

    def __neg__(self):
        return vector(map(lambda x: -x, self))

    def __sub__(self, other):
        return vector(map(lambda x, y: x - y, self, other))

    def __mul__(self, other):
        try:
            return vector(map(lambda x, y: x * y, self, other))
        except:
            return vector(map(lambda x: x * other, self))

    def __rmul__(self, other):
        return (self * other)

    def __div__(self, other):
        try:
            return vector(map(lambda x, y: x / y, self, other))
        except:
            return vector(map(lambda x: x / other, self))

    def __rdiv__(self, other):
        try:
            return vector(map(lambda x, y: x / y, other, self))
        except:
            return vector(map(lambda x: other / x, self))

    def size(self):
        return len(self)

def isVector(x):
    return hasattr(x, '__class__') and x.__class__ is vector


def zeros(n):
    return vector(map(lambda x: 0., range(n)))


def ones(n):
    return vector(map(lambda x: 1., range(n)))


def random(n, lmin=0.0, lmax=1.0):
    import random
    gen = random.random()
    dl = lmax - lmin
    return vector(map(lambda x: dl * gen.random(),
                      range(n)))


def dot(a, b):
    try:
        sum=0
        for i in range(0,len(a)):
            sum+=a[i]*b[i]
        return sum
    except:
        raise TypeError('vector::FAILURE in dot')


def norm(a):
    try:
        return math.sqrt(abs(dot(a, a)))
    except:
        raise TypeError('vector::FAILURE in norm')


def sum(a):
    try:
        return reduce(lambda x, y: x + y, a, 0)
    except:
        raise TypeError('vector::FAILURE in sum')


if __name__ == "__main__":

    a = zeros(4)

    a[0] = 1.0

    a[3] = 3.0

    print(len(a))
    print(a.size())

    b = a;
    c = a + b
    print(c)

    c = -a
    print(c)
    print(a)

    c = a - b
    print(c)

    c = a * 1.2
    print(c)

    c = 1.2 * a
    print(c)

    print(dot(b, a))

    c = a * b
    print(c)

    print((a, 2 * ones(len(a))))

    c = ones(10)
    print(c)

    c = zeros(10)
    print(c)