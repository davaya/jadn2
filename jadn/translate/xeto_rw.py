from typing import TextIO

"""
Translate JADN abstract schema to/from Haystack Extensible Explicitly Typed Objects (Xeto) schema language
"""


def xeto_style(self) -> dict:
    # Return default column positions
    return {
        'meta': 12,     # Width of meta name column (Example from JIDL)
    }


def xeto_loads(self, doc: str) -> None:
    print('Xeto load not implemented')
    exit(1)


def xeto_load(self, fp: TextIO) -> None:
    return self.xeto_loads(fp.read())


def xeto_dumps(self, style: dict = None) -> str:
    """
    Translate JADN schema to/from Xeto
    """
    print('Xeto dump not implemented')
    exit(1)


def xeto_dump(self, fp: TextIO, style=None) -> None:
    fp.write(self.xeto_dumps(self.schema, style))


__all__ = [
    'xeto_style',
    'xeto_loads',
    'xeto_load',
    'xeto_dumps',
    'xeto_dump',
]
