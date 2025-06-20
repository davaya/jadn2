from typing import TextIO

"""
Translate JADN abstract schema to XML schema definition (XSD)
"""


def xsd_style(self) -> dict:
    # Return default column positions
    return {
        'meta': 12,     # Width of meta name column (Example from JIDL)
    }


def xsd_loads(self, doc: str) -> None:
    print('xsd load not implemented')
    exit(1)


def xsd_load(self, fp: TextIO) -> None:
    self.xsd_loads(fp.read())


def xsd_dumps(self, style: dict = None) -> str:
    """
    Translate JADN schema to/from xsd
    """
    print('xsd dump not implemented')
    exit(1)


def xsd_dump(self, fp: TextIO, style=None) -> None:
    fp.write(self.xsd_dumps(self.schema, style))


__all__ = [
    'xsd_style',
    'xsd_loads',
    'xsd_load',
    'xsd_dumps',
    'xsd_dump',
]
