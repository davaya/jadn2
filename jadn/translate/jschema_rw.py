from typing import TextIO

"""
Translate JADN abstract schema to JSON schema
"""


def jschema_style(self) -> dict:
    # Return default column positions
    return {
        'meta': 12,     # Width of meta name column (Example from JIDL)
    }


def jschema_loads(self, doc: str) -> dict:
    print('jschema load not implemented')
    exit(1)


def jschema_load(self, fp: TextIO) -> dict:
    return self.jschema_loads(fp.read())


def jschema_dumps(self, schema: dict, style: dict = None) -> str:
    """
    Translate JADN schema to/from jschema
    """
    print('jschema dump not implemented')
    exit(1)


def jschema_dump(self, schema: dict, fp: TextIO, style=None) -> None:
    fp.write(self.jschema_dumps(schema, style))


__all__ = [
    'jschema_style',
    'jschema_loads',
    'jschema_load',
    'jschema_dumps',
    'jschema_dump',
]
