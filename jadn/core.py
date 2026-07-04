import os
import json

from jadn.definitions import TypeName, CoreType, TypeOptions, Fields, \
    FieldID, FieldName, FieldType, FieldOptions, has_fields, is_builtin
from dataclasses import dataclass, field, fields
from typing import TextIO, BinaryIO, Any, ClassVar, Optional


# Handle errors
def raise_error(*s) -> None:
    raise ValueError(*s)


def data_dir() -> str:
    """
    Return directory containing JADN schema files
    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


# =========================================================
# Define JADN schema static load function because it's needed to load METASCHEMA,
# Subclass cannot initialize parent class
# =========================================================

def jadn_schema_loads(jadn_str: str, opt_name: dict[int, str]) -> dict:
    """
    Load a JADN schema from a JSON string.

    For each type definition, fill in column defaults and convert options from tagString list to dict.

    :param jadn_str: {meta, types} in JSON-serialized format
    :param opt_name: schema-defined tag-to-name lookup table
    :return: schema dict value: {meta, types}
    """
    def load_tagstrings(tag_strings: list[str], tag_name: dict[int, str]) -> dict[str, str]:
        # Convert tagString-serialized value list to dict
        return {tag_name[ord(s[0])]: s[1:] for s in tag_strings}

    schema = json.loads(jadn_str)
    tdef = [None, None, [], '', []]  # [TypeName, CoreType, TypeOptions, TypeDesc, Fields]
    for td in schema['types']:
        td += tdef[len(td):len(tdef)]
        td[TypeOptions] = load_tagstrings(td[TypeOptions], opt_name)
        for fd in td[Fields]:
            # [ItemID, ItemValue, ItemDesc] or [FieldID, FieldName, FieldType, FieldOptions, FieldDesc]
            fdef = [None, '', ''] if td[CoreType] == 'Enumerated' else [None, None, None, [], '']
            fd += fdef[len(fd):len(fdef)]
            if has_fields(td[CoreType]):
                fd[FieldOptions] = load_tagstrings(fd[FieldOptions], opt_name)
    return schema


# ========================================================
# JADN schema core class
# 1: Class variables are computed once from the Metaschema, the first time any subclass is initialized
# 2: Instance variables are
# 2a: computed once when a subclass is initialized
# 2b: computed when a schema is loaded using the subclass
# 2c: copied when an input schema is linked to an output schema
# 3: Cached when a document is validated against a schema
# ========================================================
@dataclass(slots=True, order=True)      # Automatically generate __init__() and data methods
class JADNCore:
    pkg: Optional['JADNCore'] = None    # Argument to copy schema instance from pkg to self
    METASCHEMA: ClassVar[dict] = {}     # Class variables loaded and precomputed once
    OPT_NAME: ClassVar[dict] = {}       # FieldID to FieldName
    OPT_ID: ClassVar[dict] = {}         # FieldName to FieldID
    OPT_TYPE: ClassVar[dict] = {}       # Option ID to Name
    OPT_TAB: ClassVar[dict] = {}        # Option Name to ID

    # Reserve fixed memory slots for instance variables, but do not include them in auto-generated __init__
    schema: dict = field(init=False)    # Original Schema Value
    source: TextIO = field(init=False)  # Source of original schema Document
    encoding: dict = field(init=False)  # schema-independent mechanisms for value representation
    type_x: dict = field(init=False)    # schema name to type definition lookup
    val_type: dict = field(init=False)  # list of values annotated with type
    cache: dict = field(init=False)  # tables for input package


    def __post_init__(self) -> None:            # Run immediately after __init__()
        # If this is the first instance, pre-compute class variables from metaschema definitions
        if not JADNCore.METASCHEMA:
            meta_file = os.path.join(data_dir(), 'jadn_v2.0_schema.jadn')
            with open(meta_file, encoding='utf8') as fp:
                jadn_str = fp.read()
            schema = json.loads(jadn_str)

            # Generate tag-string serialization tables
            # Get option definitions from Metaschema reserved type "JADNOpts"
            tx = {td[TypeName]: td for td in schema['types']}
            opts = tx['JADNOpts'][Fields]
            JADNCore.OPT_NAME = {i[FieldID]: i[FieldName] for i in opts}    # ID to Name lookup
            JADNCore.OPT_ID = {i[FieldName]: i[FieldID] for i in opts}      # Name to ID lookup
            assert len(self.OPT_NAME) == len(self.OPT_ID), f'{meta_file}: Bad JADNOpts (duplicate id or name)'

            # Generate option name to type lookup tables
            JADNCore.OPT_TYPE = {i[FieldName]: i[FieldType] for i in opts}  # Name to value type lookup
            JADNCore.OPT_TAB = {i[FieldName]: {f[FieldName]: f[FieldType] for f in tx[i[FieldType]][Fields]} \
                for i in opts if i[FieldType] not in {'Binary', 'Boolean', 'Integer', 'Number', 'String', 'BType'}}

            # Generate separate type and field option lists
            JADNCore.OPT_ORDER = {i[FieldName]: n for n, i in enumerate(opts, start=1)}     # Canonical position
            to = self.OPT_ORDER['typeOpts']     # Sentinel value separating type options from field options
            JADNCore.TYPE_OPTS = {k for k, v in self.OPT_ORDER.items() if v < to}
            JADNCore.FIELD_OPTS = {k for k, v in self.OPT_ORDER.items() if v > to}

            # Package configuration variables and types
            # JADNCore.META_TYPE = {i[FieldName]: i[FieldType] for i in tx['Config'][Fields]}

            # With option tables in place, load metaschema as normal JADN schema
            JADNCore.METASCHEMA = jadn_schema_loads(jadn_str, self.OPT_NAME)
            JADNCore.TYPE_X = {td[TypeName]: td for td in self.METASCHEMA['types']}
            self.load_option_types(self.METASCHEMA['types'])

            JADNCore.REF_OPTS = {fd[FieldName]  # Options that refer to other types
                for td in self.METASCHEMA['types'] if 'tagString' in td[TypeOptions]
                    for fd in td[Fields] if fd[FieldType] == 'TypeRef'}

            # Get TypeOptions for each CoreType from reserved type "TypeOptions"
            def topt(tname: str) -> list:
                return {k[FieldName]: k[FieldOptions].get('minOccurs', 1) for k in self.TYPE_X[tname][Fields]}
            JADNCore.TYPE_OPTIONS = {k[FieldName]: topt(k[FieldType]) for k in self.TYPE_X['TypeOptions'][Fields]}

        # Initialize schema instance
        self.schema = None      # original schema
        self.source = None      # source of original schema
        self.encoding = None    # schema-independent mechanisms for value representation
        self.type_x = None      # schema name to type definition lookup
        self.val_type = []      # list of parsed values annotated with type
        self.cache = None       # pre-computed and cached values used to speed validation

        # pkg must be a subclass of JADNCore
        if self.pkg is not None:
            assert self.pkg.__class__.__bases__ == self.__class__.__bases__
            # Copy specific instance variables from input pkg
            for f in ('schema', 'source'):
                setattr(self, f, getattr(self.pkg, f))
            """
            # Copy all instance variables from input pkg (shallow)
            for f in fields(self):
                if f.name != 'pkg':
                    setattr(self, f.name, getattr(self.pkg, f.name))
            """

    def style(self) -> dict:
        """

        :return:
        :rtype:
        """
        return {}

    def schema_loads(self, message: str | bytes, source: str=None) -> None:
        """

        :param message:
        :type message:
        :param source:
        :type source:
        :return:
        :rtype:
        """
        raise NotImplementedError(f'{self.__class__.__name__} schema load not implemented')

    def schema_load(self, fp: TextIO | BinaryIO) -> None:
        """

        :param fp:
        :type fp:
        :return:
        :rtype:
        """
        self.schema_loads(fp.read(), fp.name)

    def schema_dumps(self, style: dict=None) -> str | bytes:
        """

        :param style:
        :type style:
        :return:
        :rtype:
        """
        raise NotImplementedError(f'{self.__class__.__name__} schema dump not implemented')

    def schema_dump(self, fp: TextIO | BinaryIO, style: dict=None) -> str | bytes:
        """

        :param fp:
        :type fp:
        :param style:
        :type style:
        :return:
        :rtype:
        """
        message = self.schema_dumps(style)
        fp.write(message)
        return message

    def schema_load_finish(self, verbose_record: bool=True, verbose_string: bool=True) -> None:
        """
        Common schema-load post-processing
          * load Config options from meta instance
          * expand shortcuts to produce execution-optimized schema
          * validate schema against Metaschema
        """
        # self.load_meta_types()
        self.load_option_types(self.schema['types'])  # Convert option strings to typed values
        self.type_x = {v[TypeName]: v for v in self.schema['types']}   # Generate type index for validation
        self.encoding = {'verbose_record': verbose_record, 'verbose_string': verbose_string}
        self.schema_validate()

    def load_meta_types(self) -> None:
        if meta := self.schema.get('meta', {}):
            for k, v in (c := meta.get('config', {})).items():
                c[k] = self.str_to_val(self.META_TYPE[k], v)

    # JADNCore.META_TYPE = {i[FieldName]: i[FieldType] for i in tx['Config'][Fields]}

    def get_map(self, vt: str, lit: str, btype, t_table) -> Any:
        """
        Convert string representations to typed values of JADN TypeOptions based on the JADNOpts
        translation table, semantic validation keywords based on JADNFormats, and user-defined
        keyword values based on user-supplied translation tables.
        """
        if vt in self.TYPE_X:
            assert (mt := self.TYPE_X[vt])[CoreType] == 'Map'
            t = {i[FieldName]: i[FieldType] for i in mt[Fields]}
        else:
            t = self.OPT_TYPE
        if lit not in t:
            print(lit, t)
        # return {lit: self.str_to_val(t[lit], lit, t)}
        rv = {lit: self.str_to_val(t[lit], lit, btype, t_table)}
        return rv

    def str_to_val(self, k: str, v: str, btype: str) -> Any:
        vtypes = {
            'Boolean': bool,
            'Integer': int,
            'Number': float,
            'String': str,
        }

        if tt := self.OPT_TAB.get(k):
            vl = [i.strip() for i in v.split(',')]
            rv = {}
            for i in vl:
                i1, _, i2 = i.partition(':')
                try:
                    rv.update({i1: vtypes[tt[i1]](i2 if i2 else '1')})
                except (ValueError, KeyError) as e:
                    print(e)
            return rv

        kt = self.OPT_TYPE.get(k)
        if kt:
            kp = btype if kt == 'BType' else kt
            kp = kp if kp in vtypes else 'String'
            if kp in vtypes:
                return vtypes[kp](v)

        raise_error(f'Translation for {k} not found: table {kt}, value {v}, type {btype}')

        """
        return bytes.fromhex(literal[2:]) if vtype == 'Binary' \
            else True if vtype == 'Boolean' \
            else vtypes[vtype](literal) if vtype in vtypes \
            else t_table[literal] if vtype == 'BType' \
            else self.get_map(vtype, literal, t_table)
        """

    def load_option_types(self, type_defs: list) -> None:
        """
        Convert JADN option values in type definitions from strings to typed variables
        """

        def load_otype(opts: dict, base_type: str) -> None:
            opts.update({k: self.str_to_val(k, v, base_type) for k, v in opts.items()})

        for tdef in type_defs:
            load_otype(tdef[TypeOptions], tdef[CoreType])
            if has_fields(tdef[CoreType]):
                for fd in tdef[Fields]:
                    load_otype(fd[FieldOptions], fd[FieldType])

    def schema_validate(self) -> None:
        """
        Validate a schema instance against JADN metaschema
        Precompute lookup tables to optimize data validation against schema
        """
        def _val(tdef: list) -> dict:
            if xo := set(tdef[TypeOptions]) - set(self.TYPE_OPTIONS[tdef[CoreType]]):
                raise_error(f'Unsupported options {xo} for type {tdef[CoreType]} in {tdef[TypeName]}')
            if xo := {k for k, v in self.TYPE_OPTIONS[tdef[CoreType]].items() if v == 1} - set(tdef[TypeOptions]):
                raise_error(f'Missing required options {xo} for type {tdef[CoreType]} in {tdef[TypeName]}')

            return {
                'fx': {fd[FieldName]: fd[FieldID] for fd in tdef[Fields]},
                'req': {fd[FieldName]: fd[FieldOptions].get('minOccurs', 1) for fd in tdef[Fields]}
            }

        self.cache = {td[TypeName]: _val(td) for td in self.schema['types']}
        self.cache['run_schema'] = {}  # Original schema with shortcuts expanded
        pass


    def validate_value(self, tname: str, fdef: list, val: Any, ctx: Any, type_callback) -> None:
        # perform class-agnostic value validation
        # classify type and validity of val according to type options

        tdef = self.TYPE_X.get(tname, tname)
        self.val_type.append((tdef[TypeName], val))
        schema_opts = self.TYPE_OPTIONS[tdef[CoreType]]
        type_callback(tdef, fdef, val, ctx)   # Perform class-specific processing on type

        if (tn := tdef[CoreType]) == 'Boolean':
            pass

        elif tn == 'Integer':
            pass

        elif tn == 'Number':
            pass

        elif tn == "String":
            pass    # done - no generic processing

        elif tn == 'Binary':
            pass

        elif tn == 'Array':
            pass

        elif tn == 'Map':
            pass

        elif tn == 'Record':
            fnames = set()
            ftypes = {k[FieldName]: k[FieldType] for k in tdef[Fields]}
            for k, v in val.items():
                fnames.add(k)
                pass
        #     for fdef in tdef[Fields]:
        #         type_callback(tdef, fdef, val, ctx)

        elif tn == 'ArrayOf':
            fdef = self.TYPE_X.get(tdef[TypeOptions]['valueType'])
            for f in val:
                type_callback(tdef, fdef, val, ctx)
                # make_val_element(fname, f, fdef[TypeName], ctx)

        elif tn == 'MapOf':
            pass    # get column names/values as attributes

        elif tn == 'Enumerated':
            pass

        elif tn == 'Choice':
            pass

        else:
            raise_error(f'Unknown Core Type: {tdef} {fdef}')

def dump_option_type(opts: dict, base_type: str, t_table: dict) -> None:
    """

    :param opts:
    :type opts:
    :param base_type:
    :type base_type:
    :param t_table:
    :type t_table:
    :return:
    :rtype:
    """
    def dict_to_str(val: dict) -> str:
        vl = (k if (isinstance(v, bool) or not v) else k + ':' + str(v) for k, v in val.items())
        return ','.join(vl)

    def val_to_str(vtype: str, val: Any) -> str | dict:
        return f'0x{val.hex()}' if vtype == 'Binary' else dict_to_str(val) if isinstance(val, dict) else str(val)

    if not isinstance(opts, dict):
        print
    op = {k: val_to_str(base_type if (t := t_table[k]) == 'BType' else t, v) for k, v in opts.items()}
    opts.update(op)


def dump_option_types(type_defs: list, type_table: dict[str, str]) ->None:
    """
    Convert JADN option values in type definitions from typed variables to strings
    """
    for tdef in type_defs:
        dump_option_type(tdef[TypeOptions], tdef[CoreType], type_table)
        if has_fields(tdef[CoreType]):
            for fd in tdef[Fields]:
                dump_option_type(fd[FieldOptions], fd[FieldType], type_table)


    # =========================================================
    # Support Functions
    # =========================================================

def build_deps(self) -> dict[str, list[tuple[str, str]]]:
    """
    Build a Dependency dict: {TypeName: [Dep1, Dep2, ...]}
    Returns dependencies for each type in order and a list of all referenced types.
    A single unreferenced type (root) indicates a fully-connected hierarchy;
    multiple roots indicate disconnected items or hierarchies,
    and no roots indicate a dependency cycle.
    """
    def get_refs(tdef: list) -> list[tuple[str, str]]:  # Return all type references from a type definition
        """
        # Options whose value is/has a type name: strip option id
        oids = [JADN.OPTX['keyType'], JADN.OPTX['valueType'], JADN.OPTX['extends'], JADN.OPTX['restricts']]
        # Options that enumerate fields: keep option id
        oids2 = [JADN.OPTX['enum'], JADN.OPTX['pointer']]
        refs = [to[1:] for to in tdef[TypeOptions] if to[0] in oids and not is_builtin(to[1:])]
        refs += ([to[1:] for to in tdef[TypeOptions] if to[0] in oids2])
        """

        # Type options that reference other types (e.g., value_type)
        refs = [(v, 'C') for k, v in tdef[TypeOptions].items() if k in self.REF_OPTS and not is_builtin(v)]
        # Fields that contain or link to other types
        if has_fields(tdef[CoreType]):  # Ignore Enumerated
            for f in tdef[Fields]:
                if not is_builtin(f[FieldType]):    # Ignore core types
                    fo = set(f[FieldOptions])
                    ref_type = (
                        'I' if {'extends', 'restricts'} & fo else   # Type Inheritance in schema
                        'L' if {'link'} & fo else                   # Link (foreign key) in container instance
                        'C')                                        # Value in container instance
                    refs.append((f[FieldType], ref_type))
                # Get references from TypeOptions in field using fake TypeDefinition
                refs += get_refs(['', f[FieldType], f[FieldOptions], '', []])
        return refs

    deps = {t[TypeName]: get_refs(t) for t in self.schema['types']}
    return deps


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
