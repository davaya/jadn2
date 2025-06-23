import os
from jadn.definitions import DEFS
from jadn.convert import jadn_rw
from types import ModuleType

# ========================================================
# JADN schema core class
# ========================================================

class JADN:

    # Load constants from DEFS (definitions.py) into class variables
    for k, v in DEFS.__dict__.items():
        if not k.startswith('__'):
            locals()[k] = v

    # Defer loading METASCHEMA until after the class is defined

    def __init__(self, schema: dict = None):
        self.schema = schema
        self.source = None
        return

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
