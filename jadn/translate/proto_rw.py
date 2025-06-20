from typing import TextIO

"""
Translate JADN abstract schema to Protocol Buffers
"""


def proto_style(self) -> dict:
    # Return default column positions
    return {
        'meta': 12,     # Width of meta name column (Example from JIDL)
    }


def proto_loads(self, doc: str) -> None:
    print('proto load not implemented')
    exit(1)


def proto_load(self, fp: TextIO) -> None:
    return self.proto_loads(fp.read())


def proto_dumps(self, style: dict = None) -> str:
    """
    Translate JADN schema to/from proto
    """
    print('proto dump not implemented')
    exit(1)


def proto_dump(self, fp: TextIO, style=None) -> None:
    fp.write(self.proto_dumps(self.schema, style))


__all__ = [
    'proto_style',
    'proto_loads',
    'proto_load',
    'proto_dumps',
    'proto_dump',
]
