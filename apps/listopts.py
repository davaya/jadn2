from jadn.definitions import TypeName, CoreType, TypeOptions, Fields, FieldOptions, OPTX
from jadn.convert import JADN

"""
List the options defined in a JADN Schema
(used to check coverage of all options in the jadn2-test schema)
"""

def getopts(td: list) -> list:
    opts = [k for k in td[TypeOptions]]
    if td[CoreType] != 'Enumerated':
        for fd in td[Fields]:
            opts += fd[FieldOptions]
    return opts

if __name__ == '__main__':
    # Load the schema to be checked
    fn = 'schemas/jadn2-test.jadn'
    print(f'Options defined in {fn}')
    js = JADN()
    with open(fn) as fp:
        js.schema_load(fp)

    # Collect the options used in each type definition
    opts = {k[TypeName]: getopts(k) for k in js.SCHEMA["types"]}
    opttypes = {k: set() for k in OPTX}
    for k, v in opts.items():
        for o in v:
            opttypes[o] |= {k,}

    # Print the results
    for k, v in opttypes.items():
        print(f'{k:>12}: {v}')
