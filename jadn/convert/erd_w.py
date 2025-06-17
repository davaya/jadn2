from typing import TextIO

"""
Convert JADN abstract schema to Entity Relationship Diagrams
"""


def erd_style(self) -> dict:
    # Return default column positions
    return {
        'meta': 12,     # Width of meta name column (Example from JIDL)
    }


def erd_dumps(self, schema: dict, style: dict = None) -> str:
    """
    Convert JADN schema to JADN-IDL
    """
    print('Markdown dump not implemented')
    exit(1)


def erd_dump(self, schema: dict, fp: TextIO, source='', style=None) -> None:
    fp.write(self.md_dumps(schema, style))


__all__ = [
    'erd_dump',
    'erd_dumps',
    'erd_style'
]
