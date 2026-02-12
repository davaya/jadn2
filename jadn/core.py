import os
import json
from copy import deepcopy
from jadn.definitions import TypeName, CoreType, TypeOptions, Fields, \
    ItemID,ItemValue, FieldType, FieldOptions
from typing import TextIO, BinaryIO, Any
from numbers import Number


# =========================================================
# Define JADN schema static function here because it's needed to load METASCHEMA.
# Using the JADN class would be an inheritance loop error.
# METASCHEMA can validate itself like any other JADN schema.
# =========================================================
def jadn_schema_loads(self, jadn_str: str) -> dict:
    """
    Load a logical JADN schema from a JSON string.

    For each type definition, fill in defaults and convert options from list of tagged strings to dict.

    :param self: supplied when calling from a class instance, not used
    :param jadn_str: {meta, types} in serialized format
    :return: schema value: {meta, types}
    """

    def load_tagstrings(tstrings: list[str], otype) -> dict[str, str]:
        """
        Parse JSON-serialized list of tagStrings (e.g., TypeOptions, FieldOptions) to a dict
        """
        return {self.OPT_NAME[ord(s[0])]: s[1:] for s in tstrings}

    """
    Convert string option values to typee values

    def opt(s: str) -> tuple[str, str]:
        t = OPT_NAME[ord(s[0])]
        if t[0] == 'format':
            return s, ''
        f = PYTHON_TYPES[core_type if t[1] is None else t[1]]
        if f == type(b''):
            f = bytes.fromhex
        return (t[0],
                True if f is bool else
                {'enum': s[2:]} if s[1] == chr(JADNCore.OPT_ID['enum']) else
                f(s[1:]))
        return self.OPT_NAME[ord(s[0])][0], s[1:]
    return dict(opt(s) for s in tstrings)
    """

    schema = json.loads(jadn_str)
    tdef = [None, None, [], '', []]  # [TypeName, CoreType, TypeOptions, TypeDesc, Fields]
    for td in schema['types']:
        td += tdef[len(td):len(tdef)]
        td[TypeOptions] = load_tagstrings(td[TypeOptions], td[CoreType])
        for fd in td[Fields]:
            fdef = [None, None, ''] if td[CoreType] == 'Enumerated' else [None, None, None, [], '']
            fd += fdef[len(fd):len(fdef)]
            if td[CoreType] != 'Enumerated':
                fd[FieldOptions] = load_tagstrings(fd[FieldOptions], fd[FieldType])
    return schema


def jadn_schema_dumps(self, style: dict=None) -> str:
    """
    Return a schema instance as a string containing JADN data in JSON format

    Don't include empty metadata section
    Don't include empty trailing optional columns
    """

    def dump_tagstrings(opts: dict[str, str], ct: str) -> list[str]:
        """
        Serialize TypeOptions and FieldOptions dict as JSON list of tag-strings
        """

        def dictopt(v: dict[str, str]) -> str:
            kv = v.popitem()
            return chr(self.OPT_ID[kv[0]]) + kv[1]

        def strs(k: str, v: Any) -> str:
            """
            v = '' if isinstance(v, bool) else\
                v.hex() if isinstance(v, bytes) else\
                dictopt(v) if isinstance(v, dict) else\
                str(v)
            """
            return chr(self.OPT_ID[k]) + str(v)

        return [strs(k, v) for k, v in sorted(opts.items(),  # Sort options to a canonical order to ease comparison
                                              key=lambda k: self.OPT_ORDER[k[0]])]

    schema_copy = {'meta': x} if (x := self.schema.get('meta')) else {}
    schema_copy.update({'types': deepcopy(self.schema['types'])})

    for td in schema_copy['types']:
        # Clean up field defs
        for fd in td[Fields]:       # TODO: delete default=1 minOccurs/maxOccurs (until instance validation)
            if td[CoreType] == 'Enumerated':
                fdef = [None, None, '']
            else:
                fd[FieldOptions] = dump_tagstrings(fd[FieldOptions], fd[FieldType])
                fdef = [None, None, None, [], '']
            while fd and fd[-1] == fdef[len(fd) - 1]:
                fd.pop()
        # Clean up type def
        td[TypeOptions] = dump_tagstrings(td[TypeOptions], td[CoreType])
        tdef = [None, None, [], '', []]
        while td and td[-1] == tdef[len(td) - 1]:
            td.pop()

    return _pprint(schema_copy, strip=style.get('strip', True)) + '\n'


# ========================================================
# JADN schema core class
# ========================================================
class JADNCore:
    METASCHEMA = None

    def __init__(self, pkg: 'JADNCore'=None) -> None:
        self.schema = None          # original schema
        self.source = None          # source of original schema
        self.full_schema = None     # schema after all shortcuts expanded (required for data validation)
        if pkg is not None:
            assert pkg.__class__.__bases__ == self.__class__.__bases__      # pkg must be a subclass of JADNCore
            self.__dict__.update(pkg.__dict__)      # Copy all instance variables from pkg (shallow)

        # If this is the first instance, load metaschema from JADN file into class variables
        if JADNCore.METASCHEMA is None:
            data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
            meta_file = os.path.join(data_dir, 'jadn_v2.0_schema.jadn')     # TODO: use only metaschema in data_dir
            with open(meta_file, encoding='utf8') as fp:
                jadn_str = fp.read()

            # Get option definitions from Metaschema reserved type "JADNOpts"
            # Pre-compute tag-string serialization tables as class variables
            schema = json.loads(jadn_str)
            JADNCore.TYPE_X = {td[TypeName]: td for td in schema['types']}
            assert 'JADNOpts' in JADNCore.TYPE_X, f'Metaschema {meta_file} is missing JADNOpts option definitions'
            opts = JADNCore.TYPE_X['JADNOpts'][Fields]
            JADNCore.OPT_NAME = {i[ItemID]: i[ItemValue] for i in opts}
            JADNCore.OPT_ID = {i[ItemValue]: i[ItemID] for i in opts}
            JADNCore.OPT_ORDER = {i[ItemValue]: n for n, i in enumerate(opts, start=1)}
            to = JADNCore.OPT_ORDER['typeOpts']     # Sentinel value separating type options from field options
            JADNCore.TYPE_OPTS = {k for k, v in JADNCore.OPT_ORDER.items() if v < to}
            JADNCore.FIELD_OPTS = {k for k, v in JADNCore.OPT_ORDER.items() if v > to}
            assert len(JADNCore.OPT_NAME) == len(JADNCore.OPT_ID) == len(JADNCore.OPT_ORDER) == len(opts),\
                f'{meta_file}: Bad JADNOpts (duplicate id or name)'

            # With option tables in place, load metaschema as any JADN schema
            JADNCore.METASCHEMA = jadn_schema_loads(self, jadn_str)

    def style(self) -> dict:
        return {}

    def schema_loads(self, message: str | bytes, source: str=None) -> None:
        raise NotImplementedError(f'{self.__class__.__name__} schema load not implemented')

    def schema_load(self, fp: TextIO | BinaryIO) -> None:
        self.schema_loads(fp.read(), fp.name)

    def schema_dumps(self, style: dict=None) -> str | bytes:
        raise NotImplementedError(f'{self.__class__.__name__} schema dump not implemented')

    def schema_dump(self, fp: TextIO | BinaryIO, style: dict=None) -> None:
        fp.write(self.schema_dumps(style))

    def schema_validate(self) -> None:
        """
        Validate a logical schema instance against JADN metaschema
        """
        pass


# ========================================================
# Support functions
# ========================================================

def _pprint(val: Any, level: int = 0, indent: int = 2, strip: bool = False) -> str:
    """
    Prettyprint a JSON-serialized JADN schema in compact format

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
# Diagnostics - replace with unit test schemas
# =========================================================
"""
from jadn.definitions import FieldID, FieldName, ALLOWED_TYPE_OPTIONS

if __name__ == '__main__':
    # Print class constants generated from definitions.py
    # print('OPTS:', len(JADN.OPTS), JADN.OPTS)   # Option {id: (name, type)}
    # print('OPTX:', len(JADN.OPTX), JADN.OPTX)   # Option {name: id}
    # print('OPTO:', len(JADN.OPTO), JADN.OPTO)   # Option sort order

    # Verify that Metaschema option IDs agree with definitions
    pkg = JADNCore()
    for td in pkg.METASCHEMA['types']:
        for fd in td[Fields]:
            if fd[FieldName] in pkg.OPT_ID:
                if (a := fd[FieldID]) != (b := pkg.OPT_ID[fd[FieldName]]):
                    print(f'{td[TypeName]}.{fd[FieldName]}: {a} != {b}')

    # Verify Metaschema's allowed options by type
    tdx = {t[TypeName]: t for t in pkg.METASCHEMA['types']}
    for to in tdx['TypeOptions'][Fields]:
        td = tdx[to[FieldType]]
        ato = ALLOWED_TYPE_OPTIONS[to[FieldName]]
        atm = [f[FieldName] for f in td[Fields]]
        if set(ato) != set(atm):
            print(f'Option mismatch: {td[TypeName]}: {ato} != {atm}')
        for f in td[Fields]:
            if (fm := f[FieldName]) != (fd := pkg.OPT_NAME[f[FieldID]][0]):
                print(f'Option mismatch: {td[TypeName]}: {fm} != {fd}')
            if (fm := f[FieldID]) != (fd := pkg.OPT_ID[f[FieldName]]):
                print(f'Option ID mismatch: {td[TypeName]}: {fm} != {fd}')

    # Test tagged-string serialization
    opts_s = [
        '=',        # id
        '*Foo',     # valueType: ArrayOf(TypeRef)
        '+#Bar',    # keyType: MapOf(Enum[TypeRef], ...)
        '#Pasta',   # enum: Enumerated(Enum[TypeRef])
        '>Zoo',     # pointer
        r'%^[-_\da-zA-Z]{1,10}$',    # pattern: String{pattern="..."}
        '{3',       # minLength
        '}10',      # maxLength
        'q',        # unique
        's',        # set
        'b',        # unordered
        'o',        # sequence
        '0',        # nillable
        'C2',       # union combine type (anyOf)
        '/ipv4',    # format (32 bit IPv4 address)
        # '/i32',     # format (signed 32 bit int)
        'E2',       # integer fixed point scale
        'tMapKeys', # tagString
        'a',        # abstract
        'rFoo',     # restricts
        'eBar',     # extends
        'f',        # final
        'A',        # attribute
        '[0',       # minOccurs
        ']-1',      # maxOccurs
        '&3',       # tagId
        '<',        # dir (pointer)
        'K',        # key
        'L',        # link
    ]
    print(f'\n Loaded opts: {opts_s}')
    opts_d = _load_tagstrings(opts_s, 'None')
    print('Logical opts:')
    pprint(opts_d, indent=4, sort_dicts=False)
    opts_s2 = _dump_tagstrings(opts_d, 'None')
    print(f' Dumped opts: {opts_s2}')
    if opts_s2 != opts_s:
        print('\n** Translation mismatch **')
        for i in range(len(opts_s)):
            if opts_s[i] != opts_s2[i]:
                print(f"    '{opts_s[i]}' != '{opts_s2[i]}'")

    # Test tagged-string options where Value Type = CoreType
    topts_s = {
        'Binary': [
            'u00010203466f6f',  # ....Foo
            'vc0a80001',        # 192.168.0.1
        ],
        'Boolean': [
            'u',        # default - present = True.  schema warning if any value present
                        # const ('v') - absent = False
        ],
        'Integer': [
            'w4',       # minExclusive Integer
            'x5',       # maxExclusive Integer - schema warning - no valid instance
            'E3',       # scale factor exponent - E3 means int = value*10^3 (milli-units)
        ],
        'Number': [
            'u3.14159', # default
            'y2',       # minInclusive
            'z3.00',    # maxInclusive
        ],
        'String': [
            'u3.1415@', # default - this is a valid string, not a number.
            'vFred',    # const
            'w0',       # minExclusive - schema warning - string collation order may not be supported
            'x10',      # maxExclusive - this is a string, not a number
            'yBar',     # minInclusive
            'zBaz',     # maxInclusive
        ]
    }

    for core_type, opts_s in topts_s.items():
        print(f'\n Loaded opts ({core_type}): {opts_s}')
        opts_d = {}
        try:
            opts_d = _load_tagstrings(opts_s, core_type)
        except ValueError as e:
            print(e)
        print(f'Logical opts ({core_type}):')
        pprint(opts_d, indent=4, sort_dicts=False)
        opts_s2 = _dump_tagstrings(opts_d, core_type)
        print(f' Dumped opts ({core_type}): {opts_s2}')
        if opts_s2 != opts_s:
            print('** Translation mismatch **')
"""
