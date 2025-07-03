import json
import os
from copy import deepcopy
from numbers import Number
from typing import TextIO, Any
from jadn.core import JADN_Core
from jadn.definitions import CoreType, TypeOptions, Fields, FieldType, FieldOptions, PYTHON_TYPES
from jsonschema import validate


class JADN(JADN_Core):
    def style(self) -> dict:
        return {
            'strip': True
        }

    def schema_loads(self, jadn_str: str) -> None:
        """
        Load a logical JADN schema from a JSON string.

        For each type definition, fill in defaults and convert options from list of tagged strings to dict.

        :param jadn_str: {meta, types} in serialized format
        :return: {meta, types} in logical format
        """
        schema = json.loads(jadn_str)
        with open(os.path.join(self.DATA_DIR, 'jadn_v2.0_schema.json')) as f:   # Check JSON data structure
            validate(instance=schema, schema=json.load(f))

        tdef = [None, None, [], '', []]  # [TypeName, CoreType, TypeOptions, TypeDesc, Fields]
        for td in schema['types']:
            td += tdef[len(td):len(tdef)]
            td[TypeOptions] = _load_tagstrings(td[TypeOptions], td[CoreType])
            for fd in td[Fields]:
                fdef = [None, None, ''] if td[CoreType] == 'Enumerated' else [None, None, None, [], '']
                fd += fdef[len(fd):len(fdef)]
                if td[CoreType] != 'Enumerated':
                    fd[FieldOptions] = _load_tagstrings(fd[FieldOptions], fd[FieldType])
        self.schema = schema

    def schema_dumps(self, style: dict = {}) -> str:
        """
        Return a schema instance as a string containing JADN data in JSON format
        """
        schema_copy = {'meta': self.schema['meta'], 'types': deepcopy(self.schema['types'])}

        for td in schema_copy['types']:
            td[TypeOptions] = _dump_tagstrings(td[TypeOptions], td[CoreType])
            for fd in td[Fields]:       # TODO: delete default=1 minOccurs/maxOccurs (until instance validation)
                fd[FieldOptions] = _dump_tagstrings(fd[FieldOptions], fd[FieldType])
                fdef = [None, None, ''] if td[CoreType] == 'Enumerated' else [None, None, None, [], '']
                while fd and fd[-1] == fdef[len(fd) - 1]:
                    fd.pop()
            tdef = [None, None, [], '', []]
            while td and td[-1] == tdef[len(td) - 1]:   # Don't pop Fields before checking them
                td.pop()
        return _pprint(schema_copy, strip=style.get('strip', True)) + '\n'

# ========================================================
# Support functions
# ========================================================

def _load_tagstrings(tstrings: list[str], ct: str) -> dict[str, str]:
    """
    Convert JSON-serialized TypeOptions and FieldOptions list of strings to dict
    """
    def opt(s: str, ct: str) -> tuple[str, str]:
        t = JADN.OPTS[ord(s[0])]
        f = PYTHON_TYPES[ct if t[1] is None else t[1]]
        return s if s[0] in JADN.BOOL_OPTS else t[0], '' if s[0] in JADN.BOOL_OPTS else True if f is bool else f(s[1:])
    return dict(opt(s, ct) for s in tstrings)


def _dump_tagstrings(opts: dict[str, str], ct: str) -> list[str]:
    """
    Convert TypeOptions and FieldOptions dict to JSON-serialized list of strings
    """
    def strs(k: str, v: Any) -> str:
        v = '' if isinstance(v, bool) else str(v)
        return k if k[0] in JADN.BOOL_OPTS else chr(JADN.OPTX[k]) + v
    return [strs(k, v) for k, v in sorted(opts.items(),     # Sort options to a canonical order to ease comparison
            key=lambda k: JADN.OPTO[k[0]] if k[0][0] not in JADN.BOOL_OPTS else JADN.OPTO['format'])]


def _pprint(val: Any, level: int = 0, indent: int = 2, strip: bool = False) -> str:
    """
    Prettyprint a JSON-serialized schema in compact format

    :param val: JSON string to be formatted
    :param level: Indentation level, default = 0 for external calls
    :param indent: Number of spaces per level, default = 2
    :param strip: Remove empty lines between types, boolean default = False
    :return: Formatted JSON string
    """
    if isinstance(val, (Number, type(''))):
        return json.dumps(val, ensure_ascii=False)

    sp = level * indent * ' '
    sp2 = (level + 1) * indent * ' '
    sep2 = ',\n' if strip else ',\n\n'
    if isinstance(val, dict):
        sep = ',\n' if level > 0 else sep2
        lines = sep.join(f'{sp2}"{k}": {_pprint(val[k], level + 1, indent, strip)}' for k in val)
        return f'{{\n{lines}\n{sp}}}'
    if isinstance(val, list):
        sep = ',\n' if level > 1 else sep2
        nest = val and isinstance(val[0], list)  # Not an empty list
        if nest:
            vals = [f"{sp2}{_pprint(v, level, indent, strip)}" for v in val]
            spn = level * indent * ' '
            return f"[\n{sep.join(vals)}\n{spn}]"
        vals = [f"{_pprint(v, level + 1, indent, strip)}" for v in val]
        return f"[{', '.join(vals)}]"
    return '???'


# =========================================================
# Diagnostics
# =========================================================
if __name__ == '__main__':
    # Test tagged-string serialization
    opts_s = ['=', '#Pasta', 'y2', 'z3.00', 'u3.14159', 'q', '/ipv4', '/d3', 'A', '[0']
    print(f'\n Loaded opts: {opts_s}')
    opts_d = _load_tagstrings(opts_s, 'Number')
    print(f'Logical opts: {opts_d}')
    opts_s2 = _dump_tagstrings(opts_d, 'Number')
    print(f' Dumped opts: {opts_s2}')
    if opts_s2 != opts_s:
        print(' ** Translation mismatch **')
