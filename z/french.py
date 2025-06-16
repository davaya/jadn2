prefix = 'fr_'

def setter(self, txt: str) -> None:
    self.text = {
        'foo': 'foo',
        'bonjour le monde': 'hello world'
    }[txt]

def getter(self) -> str:
    out = {
        'foo': 'foo',
        'hello world': 'bonjour le monde'
    }[self.text]
    return out