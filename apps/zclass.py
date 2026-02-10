import copy

class Base:
    def __init__(self, obj: 'Base'=None) -> None:
        self.x = None
        self.y = None
        if obj is not None:
            self.__dict__.update(obj.__dict__)

    def load_value(self):
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
