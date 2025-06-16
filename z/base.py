from types import ModuleType

class Base:
    def __init__(self):
        self.text = None
        self.source = None


def add_methods(mod: ModuleType) -> None:
    for v in dir(mod):
        if callable(f := getattr(mod, v)):
            setattr(Base, mod.prefix + v, f)

"""
def get_non_inherited_methods(cls: type) -> set:
    inherited_methods = set()
    for base in cls.__mro__[1:]:  # skip the class
        inherited_methods.update(dir(base))
    return set(dir(cls)) - inherited_methods

for m in get_non_inherited_methods(cls):
    if callable(cls.__getattribute__(cls(), m)):
        setattr(base, cls.prefix + m, base.m)
"""
