from typing import Self

class Base:
    def __init__(self, x: Base=None) -> None:
        self.value = x.value if x is not None else None

    def load_value(self):
        raise NotImplementedError

class A(Base):
    def load_value(self):
        self.value = 'aaa'

class B(Base):
    def load_value(self):
        self.value = 'bbb'


if __name__ == '__main__':
    objA = A()
    print('A0:', objA, objA.value)
    objA.load_value()
    print('A1:', objA, objA.value)
    objB = B(objA)
    print(' B:', objB, objB.value)