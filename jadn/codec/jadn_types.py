from jadn.definitions import TypeName, CoreType, TypeOptions, Fields, FieldID, FieldType, FieldOptions

class Binary(bytes):
    def __init__(self, value: bytes):
        self.value = None


Boolean = bool      # bool is final
# class Boolean(bool):
#     def __init__(self, value: bool):
#         self.value = None


class Integer(int):
    def __init__(self, value: int):
        self.value = None


class Number(float):
    def __init__(self, value: float):
        self.value = None


class String(str):
    def __init__(self, value: str):
        self.__set__(value)

    def __set__(self, value: str) -> None:
        print('New String:', value)     # Check typeoptions
        self.value = value

class Set(set):
    def __init__(self):
        self.value = None


class Sequence(tuple):
    def __init__(self):
        self.value = None


class OrderedSet(set):
    def __init__(self):
        self.value = None


if __name__ == '__main__':
    def make_type(td: list):
        return jtype

    myPkg = {
        'types': [
            ['MyName', 'String', {'pattern': '^[a-zA-Z]*$', 'minLength': 1, 'maxLength': 6}, '', []]
        ]
    }
    jtypes = [make_type(td) for td in myPkg['types']]
    a = MyName('abc3')

