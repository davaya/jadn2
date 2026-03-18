import pytest
from pathlib import Path
from test_convert_rt import abs_dir, schema_convert, JADN_SCHEMA_CLASS

ABSTRACT_SCHEMA_DIR = 'schemas/abstract'


@pytest.mark.parametrize('out_format', ['jadn'])
@pytest.mark.parametrize('in_path', Path(abs_dir(ABSTRACT_SCHEMA_DIR)).glob('*'), ids=lambda p: p.name)
def test_abstract_schema_convert(session_data, in_path, out_format):
    """
    Convert JADN Schema in alternate format to native JADN format
    """
    schema_convert(JADN_SCHEMA_CLASS, in_path, out_format)
