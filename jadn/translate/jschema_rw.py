from typing import TextIO

"""
Translate JADN abstract schema to JSON schema
"""


def jschema_style(self) -> dict:
    # Return default column positions
    return {
        'meta': 12,     # Width of meta name column (Example from JIDL)
    }


def jschema_loads(self, doc: str) -> None:
    print('JSON Schema translation not implemented')
    exit(1)


def jschema_load(self, fp: TextIO) -> None:
    self.jschema_loads(fp.read())


def jschema_dumps(self, style: dict = None) -> str:
    """
    Translate JADN schema to/from jschema
    """
    print('JSON Schema translation not implemented')
    exit(1)


def jschema_dump(self, fp: TextIO, style: dict = None) -> None:
    fp.write(self.jschema_dumps(style))


__all__ = [
    'jschema_style',
    'jschema_loads',
    'jschema_load',
    'jschema_dumps',
    'jschema_dump',
]
