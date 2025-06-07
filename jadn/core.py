import copy
import json
import os
from jadn.definitions import (TYPE_OPTIONS, FIELD_OPTIONS, TypeName, CoreType, TypeOptions,
                         Fields, FieldID, FieldName, FieldType, FieldOptions, PYTHON_TYPES)
from jadn.convert.jidl import JIDL
from jadn.convert.xasd import XASD
from jsonschema import validate
from numbers import Number
from typing import TextIO, Any


# ========================================================
# JADN schema class static values and methods
# ========================================================

class JADN(JIDL, XASD):
    OPTS = (TYPE_OPTIONS | FIELD_OPTIONS)       # Defined Option table: {id: (name, type)}
    OPTX = {v[0]: k for k, v in OPTS.items()}   # Generated Option reverse index: {name: id}
    BOOL_OPTS = {'/', }     # Full-key Boolean options, present=True (e.g., /format)
    data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    # Defer loading METASCHEMA until after the class is defined

    def __init__(self):
        self.meta = None
        self.types = None
        self.source = None
        return

    def validate(self) -> None:
        """
        Validate logical schema instance against JADN metaschema
        """
        pass

    def loads(self, jadn_str: str) -> None:
        """
        Load a schema instance from a string in JSON format
        """
        json_data = json.loads(jadn_str)
        with open('data/jadn_v2.0_schema.json') as f:   # Check JSON data structure using JSON Schema
            validate(instance=json_data, schema=json.load(f))
        sc = _load(json_data)   # Load logical schema from JSON data
        self.meta = sc['meta']
        self.types = sc['types']
        self.source = None
        self.validate()

    def load(self, fp: TextIO) -> None:
        """
        Load a schema instance from a file-like object containing JADN data in JSON format
        :param fp: a TextIO reference to an open file

        Example:
            pkg = JADN()
            with open('file.jadn', 'r', encoding='utf-8') as fp:
                pkg.load(fp)
        """
        self.loads(fp.read())
        self.source = fp

    def dumps(self, strip: bool = True) -> str:
        """
        Return a schema instance as a string containing JADN data in JSON format
        """
        scc = {'meta': self.meta, 'types': copy.deepcopy(self.types)}
        return _pprint(_dump(scc), strip=strip)

    def dump(self, fp: TextIO, strip: bool = True) -> None:
        """
        Store a schema instance in a file-like object containing JADN data in JSON format

        :param fp: a TextIO reference to an open file
        :param strip: Bool, if True do not store empty trailing fields, default=True

        Example: pkg: a JADN schema instance from a previous load in any format
            with open('file.jadn', 'w', encoding='utf-8') as fp:
                pkg.dump(fp)
        """
        fp.write(self.dumps(strip=strip))

# ========================================================
# Private support functions
# ========================================================

def _load(json_data: dict) -> dict:
    """
    Convert a schema from loaded JSON data to logical JADN schema.  For each type definition,
    fill in missing defaults and convert options from string list to dict.

    :param json_data: {meta, types} in serialized format
    :return: {meta, types} in logical format
    """
    tdef = [None, None, [], '', []]    # [TypeName, CoreType, TypeOptions, TypeDesc, Fields]
    fdef = [None, None, None, [], '']  # [FieldId, FieldName, FieldType, FieldOptions, FieldDesc]
    for td in json_data['types']:
        td += tdef[len(td):len(tdef)]
        td[TypeOptions] = _load_tagstrings(td[TypeOptions], td[CoreType])
        for fd in td[Fields]:
            if td[CoreType] in {'Array', 'Map', 'Record', 'Choice'}:
                fd += fdef[len(fd):len(fdef)]
                fd[FieldOptions] = _load_tagstrings(fd[FieldOptions], fd[FieldType])
    return json_data


def _load_tagstrings(tstrings: list[str], ct: str) -> dict[str, str]:
    """
    Convert JSON-serialized TypeOptions and FieldOptions list of strings to dict
    """
    def opt(s: str, ct: str) -> tuple[str, str]:
        t = JADN.OPTS[ord(s[0])]
        f = PYTHON_TYPES[ct if t[1] is None else t[1]]
        return s if s[0] in JADN.BOOL_OPTS else t[0], '' if s[0] in JADN.BOOL_OPTS else True if f is bool else f(s[1:])
    return dict(opt(s, ct) for s in tstrings)


def _dump(json_data: dict) -> dict:
    """
    Convert a schema from logical JADN schema to JSON data to be serialized.
    For each type definition, remove trailing defaults and convert options from dict to string list.

    :param json_data: {meta, types} in logical format
    :return: {meta, types} in serialized format
    """
    for td in json_data['types']:
        td[TypeOptions] = _dump_tagstrings(td[TypeOptions], td[CoreType])
        if td[CoreType] in {'Array', 'Map', 'Record', 'Choice'}:
            for fd in td[Fields]:
                fd[FieldOptions] = _dump_tagstrings(fd[FieldOptions], fd[FieldType])
    return _strip_trailing_defaults(json_data)


def _dump_tagstrings(opts: dict[str, str], ct: str) -> list[str]:
    """
    Convert TypeOptions and FieldOptions dict to JSON-serialized list of strings
    """
    def strs(k: str, v: Any) -> str:
        v = '' if isinstance(v, bool) else str(v)
        return k if k[0] in JADN.BOOL_OPTS else chr(JADN.OPTX[k]) + v
    return [strs(k, v) for k, v in opts.items()]


def _strip_trailing_defaults(schema: dict) -> dict:
    """
    Remove empty trailing arrays and strings from JSON-serialized schema

    :param schema: JADN schema in JSON format
    :return: JADN schema in JSON format with trailing default values omitted
    """
    tdef = [None, None, [], '', []]
    for td in schema['types']:
        fdef = [None, None, ''] if td[CoreType] == 'Enumerated' else [None, None, None, [], '']
        for fd in td[Fields]:
            while fd and fd[-1] == fdef[len(fd)-1]:
                fd.pop()
        while td and td[-1] == tdef[len(td)-1]:
            td.pop()
    return schema


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
# Load METASCHEMA class variable now that the JADN class exists
# =========================================================
with open(os.path.join(JADN.data_dir, 'jadn_v2.0_schema.jadn')) as f:
    JADN.METASCHEMA = _load(json.load(f))


# =========================================================
# Diagnostics
# =========================================================
if __name__ == '__main__':
    # Initialize OPTX (reverse option index) from OPTS (option definitions)
    j = JADN()
    # print('OPTS:', len(j.OPTS), j.OPTS)   # Option {id: (name, type)}
    # print('OPTX:', len(j.OPTX), j.OPTX)   # Option {name: id}

    # Verify that Metaschema option IDs agree with definitions
    for td in JADN.METASCHEMA['types']:
        for fd in td[Fields]:
            if fd[FieldName] in JADN.OPTX:
                if (a := fd[FieldID]) != (b := JADN.OPTX[fd[FieldName]]):
                    print(f'{td[TypeName]}.{fd[FieldName]}: {a} != {b}')

    # Test tagged-string serialization
    opts_s = ['#Pasta', '[0', 'y2', 'z3.00', 'u3.14159', 'q', '/ipv4', '/d3']
    print(f'\nInput opts: {opts_s}')
    opts_d = _load_tagstrings(opts_s, 'Number')
    print(f'Logical opts: {opts_d}')
    opts_s2 = _dump_tagstrings(opts_d, 'Number')
    print(f'Dumped opts: {opts_s2}')
    if opts_s2 != opts_s:
        print(' ** Translation mismatch **')

    pkg = JADN()
    with open('data/jadn_v2.0_schema.jadn') as fp:
        pkg.load(fp)
    sc = {'meta': pkg.meta, 'types': pkg.types}
    print(f'\nSchema - Logical value:\n{sc}')               # Internal (logical) schema value
    print(f'\nSchema - JSON value:\n{pkg.dumps()}')    # External (lexical) schema value