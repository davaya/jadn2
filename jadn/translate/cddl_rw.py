from typing import TextIO

"""
Translate JADN abstract schema to Concise Data Definition Language (CDDL), a concrete schema for DBOR
"""


def cddl_style(self) -> dict:
    # Return default column positions
    return {
        'meta': 12,     # Width of meta name column (Example from JIDL)
    }


def cddl_loads(self, doc: str) -> None:
    print('CDDL load not implemented')
    exit(1)


def cddl_load(self, fp: TextIO) -> None:
    return self.cddl_loads(fp.read())


def cddl_dumps(self, style: dict = None) -> str:
    """
    Translate JADN schema to/from CDDL
    """
    print('CDDL dump not implemented')
    exit(1)


def cddl_dump(self, fp: TextIO, style: dict = None) -> None:
    fp.write(self.cddl_dumps(style))


__all__ = [
    'cddl_style',
    'cddl_loads',
    'cddl_load',
    'cddl_dumps',
    'cddl_dump',
]
