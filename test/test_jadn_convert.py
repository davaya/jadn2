import os
import pytest
from jadn.convert import JADN, JIDL, XASD, MD, ATREE, ERD
from jadn.translate import JSCHEMA, XSD, CDDL, PROTO, XETO

SCHEMA_DIR = '../apps/schemas'

def test_convert_schema():
    pass


def convert_file(schema_file: str) -> None:
    with open(os.path.join(SCHEMA_DIR, schema_file), 'r') as fp:
        pkg.schema_load(fp)