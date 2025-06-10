import copy
import json
import os
from jadn.definitions import TypeName, Fields, FieldID, FieldName,DEFS
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
with open(os.path.join(DEFS.DATA_DIR, 'jadn_v2.0_schema.jadn')) as fp:
    # JADN.METASCHEMA = JADN.json_loads(JSON, json.load(fp))
    JADN.METASCHEMA = {}

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
            if fd[FieldName] in DEFS.OPTX:
                if (a := fd[FieldID]) != (b := DEFS.OPTX[fd[FieldName]]):
                    print(f'{td[TypeName]}.{fd[FieldName]}: {a} != {b}')

    pkg = JADN()
    with open('data/jadn_v2.0_schema.jadn') as fp:
        pkg.load(fp)
    sc = {'meta': pkg.meta, 'types': pkg.types}
    print(f'\nSchema - Logical value:\n{sc}')           # Internal (logical) schema value
    print(f'\nSchema - JSON value:\n{pkg.dumps()}')     # External (lexical) schema value