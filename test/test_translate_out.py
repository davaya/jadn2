import pytest
from pathlib import Path
from jadn.translate import JSCHEMA, PROTO, XSD
from test_convert_rt import abs_dir, schema_convert

JADN_SCHEMA_DIR = 'schemas/jadn'
CONCRETE_SCHEMA_CLASS = {
    'json': JSCHEMA,
    'proto': PROTO,
    'xsd': XSD,
}


@pytest.mark.parametrize('out_format', CONCRETE_SCHEMA_CLASS)
@pytest.mark.parametrize('in_path', Path(abs_dir(JADN_SCHEMA_DIR)).glob('*'), ids=lambda p: p.name)
def test_jadn_schema_translate_out(session_data: dict, in_path: Path, out_format: str):
    """
    Convert native JADN schema to equivalent alternate JADN format
    """
    schema_msg, in_pkg = schema_convert(CONCRETE_SCHEMA_CLASS, in_path, out_format)
