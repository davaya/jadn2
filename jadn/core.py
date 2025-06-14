import copy
import json
import os
from jadn.definitions import (TypeName, Fields, FieldID, FieldName, FieldType,
                              ALLOWED_TYPE_OPTIONS, ALLOWED_TYPE_OPTIONS_ALL, DEFS)
from jadn.convert.json_rw import JSON
from jadn.convert.jidl_rw import JIDL
from jadn.convert.xasd_rw import XASD


# ========================================================
# JADN schema class static values and methods
# ========================================================

class JADN(JSON, JIDL, XASD):     # Add methods

    # Copy class variables from DEFS (definitions.py)
    for k, v in DEFS.__dict__.items():
        if not k.startswith('__'):
            locals()[k] = v

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


# =========================================================
# Load METASCHEMA class variable now that the JADN class exists
# =========================================================
with open(os.path.join(DEFS.DATA_DIR, 'jadn_v2.0_schema.jadn'), encoding='utf8') as fp:
    JADN.METASCHEMA = JADN().json_load(fp)  # Load using temporary instance


# =========================================================
# Diagnostics
# =========================================================
if __name__ == '__main__':
    # Initialize OPTX (reverse option index) from OPTS (option definitions)
    # j = JADN()
    # print('OPTS:', len(j.OPTS), j.OPTS)   # Option {id: (name, type)}
    # print('OPTX:', len(j.OPTX), j.OPTX)   # Option {name: id}
    # print('OPTO:', len(j.OPTO), j.OPTO)   # Option sort order

    # Verify that Metaschema option IDs agree with definitions
    for td in JADN.METASCHEMA['types']:
        for fd in td[Fields]:
            if fd[FieldName] in DEFS.OPTX:
                if (a := fd[FieldID]) != (b := DEFS.OPTX[fd[FieldName]]):
                    print(f'{td[TypeName]}.{fd[FieldName]}: {a} != {b}')

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

    pkg = JADN()
    with open('data/jadn_v2.0_schema.jadn') as fp:
        sc = pkg.json_load(fp)
    print(f'\nIM Schema - Logical value:\n{sc}')                   # Internal (logical) schema value
    print(f'\nIM Schema - JSON value:\n{pkg.json_dumps(sc)}')      # External (lexical) schema value
