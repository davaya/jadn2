import os
from jadn.definitions import TYPE_OPTIONS, FIELD_OPTIONS
from jadn.convert import jadn_rw
from typing import TextIO, BinaryIO
from types import ModuleType

# ========================================================
# JADN schema core class
# ========================================================

class JADN:
    # Precompute constants
    OPTS = (TYPE_OPTIONS | FIELD_OPTIONS)  # Defined Option table: {id: (name, type, sort_order)}
    OPTX = {v[0]: k for k, v in OPTS.items()}  # Generated Option reverse index: {name: id}
    OPTO = {v[0]: v[2] for k, v in OPTS.items()}  # Generated canonical option sort order {name: order}
    BOOL_OPTS = {'/', }  # Full-key Boolean options, present=True (e.g., /format)
    DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    METASCHEMA = None  # Placeholder for loading JADN metaschema

    # Defer loading METASCHEMA until after the class is defined

    def __init__(self):
        self.package = {None: {}}   # {package: {source:x, schema:y, ...}}

    def style(self) -> dict:
        return {}

    def schema_loads(self, message: str | bytes) -> None:
        pass

    def schema_load(self, fp: TextIO | BinaryIO) -> None:
        self.loads(fp.read())

    def schema_dumps(self, style: dict = {}) -> str | bytes:
        return ''

    def schema_dump(self, fp: TextIO | BinaryIO, style: dict = {}) -> None:
        fp.write(self.dumps(style))

    def validate(self) -> None:
        """
        Validate a logical schema instance against JADN metaschema
        """
        pass


# Dynamically add methods listed in module's __all__ to JADN class
def add_methods(mod: ModuleType) -> None:
    for f in mod.__all__:
        setattr(JADN, f, getattr(mod, f))


# =========================================================
# Load METASCHEMA class variable now that the JADN class exists
# TODO: figure out why this loads twice
# =========================================================
add_methods(jadn_rw)    # Register JSON loader to read metaschema
with open(os.path.join(DEFS.DATA_DIR, 'jadn_v2.0_schema.jadn'), encoding='utf8') as fp:
    (tmp := JADN()).jadn_load(fp)
    JADN.METASCHEMA = tmp.schema  # Load from JSON format using a temporary instance


# =========================================================
# Diagnostics
# =========================================================
from jadn.definitions import TypeName, Fields, FieldID, FieldName, FieldType, ALLOWED_TYPE_OPTIONS

if __name__ == '__main__':
    # Print class constants generated from definitions.py
    # print('OPTS:', len(JADN.OPTS), JADN.OPTS)   # Option {id: (name, type)}
    # print('OPTX:', len(JADN.OPTX), JADN.OPTX)   # Option {name: id}
    # print('OPTO:', len(JADN.OPTO), JADN.OPTO)   # Option sort order

    # Verify that Metaschema option IDs agree with definitions
    for td in JADN.METASCHEMA['types']:
        for fd in td[Fields]:
            if fd[FieldName] in DEFS.OPTX:
                if (a := fd[FieldID]) != (b := DEFS.OPTX[fd[FieldName]]):
                    print(f'{td[TypeName]}.{fd[FieldName]}: {a} != {b}')

    # Verify Metaschema's allowed options by type
    tdx = {t[TypeName]: t for t in JADN.METASCHEMA['types']}
    for to in tdx['TypeOptions'][Fields]:
        td = tdx[to[FieldType]]
        ato = ALLOWED_TYPE_OPTIONS[to[FieldName]]
        atm = [f[FieldName] for f in td[Fields]]
        if set(ato) != set(atm):
            print(f'Option mismatch: {td[TypeName]}: {ato} != {atm}')
        for f in td[Fields]:
            if (fm := f[FieldName]) != (fd := DEFS.OPTS[f[FieldID]][0]):
                print(f'Option mismatch: {td[TypeName]}: {fm} != {fd}')

    # Print internal (program variable) and external (JSON) schema for comparison
    pkg = JADN()
    with open('data/jadn_v2.0_schema.jadn') as fp:
        pkg.jadn_load(fp)
    print(f'\nIM Schema - Logical value:\n{pkg.schema}')            # Internal (logical) schema value
    print(f'\nIM Schema - JSON value:\n{pkg.jadn_dumps()}')         # External (lexical) schema value
