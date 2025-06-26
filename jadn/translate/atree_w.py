from asciitree import LeftAligned
from asciitree.drawing import BoxStyle, BOX_BLANK, BOX_ASCII, BOX_LIGHT, BOX_HEAVY, BOX_DOUBLE
from jadn.definitions import TypeName, CoreType, TypeOptions
from jadn.utils import build_deps, jadn2typestr
from typing import TextIO

"""
Translate JADN abstract schema to a tree diagram
"""

def atree_style(self) -> dict:
    # Return default column positions
    return {
        'draw': 'light',            # blank, ascii, light, heavy, double
        'detail': 'conceptual',     # conceptual (name), logical (name+type), information (name+type+options)
    }


def atree_dumps(self, style: dict = None) -> str:
    """
    Translate JADN schema to ascii tree diagram
    """
    def line(t: str, tx: dict[str, list], detail: str) -> str:
        tree_col, name = t.rsplit(' ', maxsplit=1)
        jtype = (f'{name}' if detail == 'conceptual' else
                 f'{name} = {tx[name][CoreType]}' if detail == 'logical' else
                 f'{name} = {jadn2typestr(tx[name][CoreType], tx[name][TypeOptions])}')
        return ' '.join((tree_col, jtype))

    tr = tree_style(style['draw'])
    defs = build_deps(self.schema)  # Get all type definitions and their dependencies
    refs = set(d for deps in defs.values() for d in deps)   # All referenced types
    roots = set(defs) - refs        # Unreferenced types
    tree = '\n\n'.join([tr(build_tree(defs, root)) for root in roots])
    tx = {} if style['detail'] == 'conceptual' else {k[TypeName]: k for k in self.schema['types']}
    return '\n'.join([line(t, tx, style['detail']) for t in tree.split('\n')])


def atree_dump(self, fp: TextIO, style: dict = None) -> None:
    fp.write(self.atree_dumps(style))

# ========================================================
# Support functions
# ========================================================

def build_tree(dependencies: dict[str, list], this: str) -> dict:
    def bt(dependencies, this):
        tree = {}
        if this in dependencies:
            for dep in dependencies[this]:
                tree[dep] = bt(dependencies, dep)
        return tree
    return {' ' + this: bt(dependencies, this)}


def tree_style(style: str) -> LeftAligned:
    omap = {
        'blank': BoxStyle(gfx=BOX_BLANK, label_space=0, label_format='[{}]', indent=0),
        'ascii': BoxStyle(gfx=BOX_ASCII),
        'light': BoxStyle(gfx=BOX_LIGHT),
        'heavy': BoxStyle(gfx=BOX_HEAVY),
        'double': BoxStyle(gfx=BOX_DOUBLE)
    }
    return LeftAligned(draw=omap[style])


# =========================================================
# Diagnostics
# =========================================================
if __name__ == '__main__':

    dependencies = {
        'asciitree': ['sometimes', 'just', 'trees', 'in'],
        'sometimes': ['you'],
              'you': [],
             'just': ['want'],
             'want': ['to', 'draw'],
            'trees': [],
               'in': ['your'],
             'your': ['terminal'],
         'terminal': []
    }

    tr = tree_style('double')
    tree = build_tree(dependencies, 'asciitree')
    print(tr(tree))


__all__ = [
    'atree_style',
    'atree_dumps',
    'atree_dump',
]
