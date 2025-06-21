from typing import TextIO

"""
Convert JADN type definitions to Markdown tables
"""


def md_style(self) -> dict:
    # Return default column positions
    return {
        'meta': 12,     # Width of meta name column (Example from JIDL)
    }


def md_dumps(self, style: dict = None) -> str:
    """
    Convert JADN schema to JADN-IDL
    """
    print('Markdown dump not implemented')
    exit(1)


def md_dump(self, fp: TextIO, style: dict = None) -> None:
    fp.write(self.md_dumps(style))


__all__ = [
    'md_style',
    'md_dumps',
    'md_dump',
]
