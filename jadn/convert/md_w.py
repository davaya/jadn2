import json
from typing import TextIO
from jadn.definitions import TypeName, CoreType, TypeOptions, TypeDesc, Fields, ItemID, FieldID, META_ORDER
from jadn.utils import jadn2typestr, jadn2fielddef

"""
Convert JADN type definitions to Markdown tables
"""


def md_style(self) -> dict:
    # Return default column positions
    return {
        'pad': True,    # Use one space horizontal padding
        'links': True   # Retain Markdown links: [text](link)
    }


def md_dumps(self, style: dict) -> str:
    """
    Convert JADN schema to Markdown Tables
    """
    text = '```\n'
    meta = self.schema['meta']
    mlist = [k for k in META_ORDER if k in meta]
    for k in mlist + list(set(meta) - set(mlist)):      # Display meta elements in fixed order
        text += f'{k:>14}: {json.dumps(meta[k])}\n'     # TODO: wrap to width, continuation-line parser
    text += '```\n'

    for td in self.schema['types']:
        if len(td) > Fields and td[Fields]:
            tdef = f'{td[TypeName]} ({jadn2typestr(td[CoreType], td[TypeOptions])})'
            tdesc = f'\n{td[TypeDesc]}\n' if td[TypeDesc] else ''
            text += f'{tdesc}\n**Type: ' + tdef.replace("*", r"\*") + '**\n'
            idt = td[CoreType] == 'Array' or td[TypeOptions].get('id', False)
            table_type = (0 if td[CoreType] == 'Enumerated' else 2) + (0 if idt else 1)
            table = [
                [['ID', 'Description']],
                [['ID', 'Item', 'Description']],
                [['ID', 'Type', r'\#', 'Description']],
                [['ID', 'Name', 'Type', r'\#', 'Description']]
            ][table_type]
            for fd in td[Fields]:
                fname, fdef, fmult, fdesc = jadn2fielddef(fd, td)
                fdef = fdef.replace('*', r'\*')
                fmult = fmult.replace('*', r'\*')
                dsc = fdesc.split('::', maxsplit=2)
                fdesc = f'**{dsc[0]}** - {dsc[1].strip()}' if len(dsc) == 2 else fdesc
                if table_type == 0:
                    table.append([str(fd[ItemID]), fdesc])
                elif table_type == 1:
                    table.append([str(fd[ItemID]), f'**{fname}**', fdesc])
                elif table_type == 2:
                    table.append([str(fd[FieldID]), fdef, fmult, fdesc])
                elif table_type == 3:
                    table.append([str(fd[FieldID]), f'**{fname}**', fdef, fmult, fdesc])
        else:
            table = [['Type Name', 'Type Definition', 'Description'],
                     [f'**{td[TypeName]}**', jadn2typestr(td[CoreType], td[TypeOptions]), td[TypeDesc]]]
        text += f'\n{format_table(table)}\n\n**********\n'
    return text


def format_table(rows: list) -> str:
    cwidth = [len(data.strip()) for data in rows[0]]
    for row in rows[1:]:
        for c in range(len(row)):
            cwidth[c] = max(cwidth[c], len(row[c].strip()))
    hbar = f'|{"|".join(["-" * (c + 2) for c in cwidth])}|'
    cf = f'| {" | ".join(["{:" + str(c) + "}" for c in cwidth])} |'
    return '\n'.join([cf.format(*rows[0])] + [hbar] + [cf.format(*r) for r in rows[1:]])


def md_dump(self, fp: TextIO, style: dict) -> None:
    fp.write(self.md_dumps(style))


__all__ = [
    'md_style',
    'md_dumps',
    'md_dump',
]
