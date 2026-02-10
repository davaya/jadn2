
class Base:
    FOO = 'Foo'     # Class variables not included in __dict__

    def __init__(self, obj: 'Base'=None) -> None:
        self.x = None       # Initialize all instance variables
        self.y = None
        if obj is not None:
            assert obj.__class__.__bases__ == self.__class__.__bases__      # obj must be subclass of same parent
            self.__dict__.update(obj.__dict__)      # Copy (shallow) all instance variables

    def load_value(self):   # Subclass method to set instance values must override this
        raise NotImplementedError


class A(Base):
    def load_value(self):
        self.x = 'aaa'
        self.y = 'a1'


class B(Base):
    def load_value(self):
        self.x = 'bbb'
        self.y = 'b2'


if __name__ == '__main__':
    objA = A()
    print('A0:', objA, objA.x, objA.y)
    objA.load_value()
    print('A1:', objA, objA.x, objA.y)
    objB = B(objA)
    print(' B:', objB, objB.x, objB.y)
    print(objB.__dict__)
