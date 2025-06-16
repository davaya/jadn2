prefix = 'es_'

def setter(self, txt: str) -> None:
    self.text = {
        'foo': 'foo',
        'hola mundo': 'hello world'
    }[txt]

def getter(self) -> str:
    out = {
        'foo': 'foo',
        'hello world': 'hola mundo'
    }[self.text]
    return out