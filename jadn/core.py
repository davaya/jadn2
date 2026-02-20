import os
import json
from jadn.definitions import TypeName, CoreType, TypeOptions, Fields, \
    ItemID, ItemValue, FieldName, FieldType, FieldOptions
from typing import TextIO, BinaryIO, Any


# =========================================================
# Define JADN schema static load function because it's needed to load METASCHEMA,
# and using the class method would be recursive.
# =========================================================
def jadn_schema_loads(self, jadn_str: str) -> dict:
    """
    Load a logical JADN schema from a JSON string.

    For each type definition, fill in column defaults and convert options from tagString list to dict.

    :param self: pre-computed option tag-to-name lookup table
    :param jadn_str: {meta, types} in JSON-serialized format
    :return: schema dict value: {meta, types}
    """

    def load_tagstrings(tag_strings: list[str]) -> dict[str, str]:
        """
        Convert JSON-serialized list of tagString-serialized TypeOptions and FieldOptions to dict format
        """
        return {self.OPT_NAME[ord(s[0])]: s[1:] for s in tag_strings}

    schema = json.loads(jadn_str)
    tdef = [None, None, [], '', []]  # [TypeName, CoreType, TypeOptions, TypeDesc, Fields]
    for td in schema['types']:
        td += tdef[len(td):len(tdef)]
        td[TypeOptions] = load_tagstrings(td[TypeOptions])
        for fd in td[Fields]:
            # [ItemID, ItemValue, ItemDesc] or [FieldID, FieldName, FieldType, FieldOptions, FieldDesc]
            fdef = [None, '', ''] if td[CoreType] == 'Enumerated' else [None, None, None, [], '']
            fd += fdef[len(fd):len(fdef)]
            if td[CoreType] != 'Enumerated':
                fd[FieldOptions] = load_tagstrings(fd[FieldOptions])
    return schema


# ========================================================
# JADN schema core class
# ========================================================
class JADNCore:
    METASCHEMA = None

    def __init__(self, pkg: 'JADNCore'=None) -> None:
        self.schema = None          # original schema
        self.source = None          # source of original schema
        self.full_schema = None     # schema with shortcuts expanded for data validation
        if pkg is not None:
            assert pkg.__class__.__bases__ == self.__class__.__bases__      # pkg must be a subclass of JADNCore
            self.__dict__.update(pkg.__dict__)      # Copy all instance variables from pkg (shallow)

        # If this is the first instance, load metaschema from JADN file into class variables
        if JADNCore.METASCHEMA is None:
            data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
            meta_file = os.path.join(data_dir, 'jadn_v2.0_schema.jadn')
            with open(meta_file, encoding='utf8') as fp:
                jadn_str = fp.read()

            # Get option definitions from Metaschema reserved type "JADNOpts"
            # Pre-compute tag-string serialization tables as class variables
            schema = json.loads(jadn_str)
            tx = {td[TypeName]: td for td in schema['types']}
            assert 'JADNOpts' in tx, f'Metaschema {meta_file} is missing JADNOpts option definitions'
            opts = tx['JADNOpts'][Fields]

            JADNCore.OPT_NAME = {i[ItemID]: i[ItemValue] for i in opts}     # ID to Name lookup
            JADNCore.OPT_ID = {i[ItemValue]: i[ItemID] for i in opts}       # Name to ID lookup
            JADNCore.OPT_ORDER = {i[ItemValue]: n for n, i in enumerate(opts, start=1)}     # Name to position

            to = self.OPT_ORDER['typeOpts']     # Sentinel value separating type options from field options
            JADNCore.TYPE_OPTS = {k for k, v in self.OPT_ORDER.items() if v < to}
            JADNCore.FIELD_OPTS = {k for k, v in self.OPT_ORDER.items() if v > to}
            assert len(self.OPT_NAME) == len(self.OPT_ID) == len(self.OPT_ORDER) == len(opts), \
                f'{meta_file}: Bad JADNOpts (duplicate id or name)'

            # With option tables in place, load metaschema as with any JADN schema
            JADNCore.METASCHEMA = jadn_schema_loads(self, jadn_str)
            JADNCore.TYPE_X = {td[TypeName]: td for td in self.METASCHEMA['types']}

            JADNCore.REF_OPTS = {fd[FieldName]  # Options that refer to other types
                for td in self.METASCHEMA['types'] if 'tagString' in td[TypeOptions]
                    for fd in td[Fields] if fd[FieldType] == 'TypeRef'}

            for td in self.METASCHEMA['types']:  # Cconvert option strings to typed values
               if ts := td[TypeOptions].get('tagString'):
                   print(f'{td[TypeName]}: {td[TypeOptions]} - {ts}')
            print(' *')

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

    def schema_load_finish(self) -> None:
        """
        Common schema-load post-processing
          * expand shortcuts to produce execution-optimized schema
          * validate schema against Metaschema
        """

    """
    Convert option strings to typed values

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


    def schema_validate(self) -> None:
        """
        Validate a logical schema instance against JADN metaschema
        """
        pass


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
