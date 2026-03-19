import pytest
from pathlib import Path
from jadn.translate import JSCHEMA, PROTO, XSD
from test_convert_rt import abs_dir, schema_convert

CONCRETE_SCHEMA_DIR = 'schemas/concrete'
CONCRETE_SCHEMA_CLASS = {
    'json': JSCHEMA,
    'proto': PROTO,
    'xsd': XSD,
    # 'cddl': CDDL,
    # 'xeto': XETO,
}


@pytest.mark.parametrize('out_format', {'jadn'})
@pytest.mark.parametrize('in_path', Path(abs_dir(CONCRETE_SCHEMA_DIR)).glob('*'), ids=lambda p: p.name)
def test_jadn_schema_translate_in(session_data: dict, in_path: Path, out_format: str):
    """
    Convert native JADN schema to equivalent alternate JADN format
    """
    schema_convert(CONCRETE_SCHEMA_CLASS, in_path, out_format)
