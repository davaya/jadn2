from asciitree import LeftAligned
from asciitree.drawing import BoxStyle, BOX_BLANK, BOX_ASCII, BOX_LIGHT, BOX_HEAVY, BOX_DOUBLE
from jadn.utils import build_deps
from typing import TextIO

"""
Translate JADN abstract schema to a tree diagram
"""

def atree_style(self) -> dict:
    # Return default column positions
    return {
        'draw': 'light',     # blank, ascii, light, heavy, double
        'indent': 1,
    }


def atree_dumps(self, style: dict = None) -> str:
    """
    Translate JADN schema to/from CDDL
    """
    omap = {
        'blank': BoxStyle(gfx=BOX_BLANK, label_space=0, label_format='[{}]', indent=0),
        'ascii': None,
        'light': BoxStyle(gfx=BOX_LIGHT),
        'heavy': BoxStyle(gfx=BOX_HEAVY),
        'double': BoxStyle(gfx=BOX_DOUBLE)
    }
    tr = LeftAligned(draw=omap[style['draw']])

    deps = build_deps(self.schema)

    print(tr(tree))


def atree_dump(self, fp: TextIO, style: dict = None) -> None:
    fp.write(self.atree_dumps(style))


__all__ = [
    'atree_style',
    'atree_dumps',
    'atree_dump',
]
