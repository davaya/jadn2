import json
import os
import pytest
from jadn.core import data_dir
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from pathlib import Path

JADN_SCHEMA_DIR = 'schemas/jadn'
JADN_BAD_SCHEMA_DIR = 'schemas/jadn-not-wellformed'


def abs_dir(relative_path: str) -> Path:
    p = Path(__file__).parts
    parts = p[:p.index('test')] + Path(relative_path).parts
    return Path(*parts)


@pytest.fixture(scope='session')
def json_schema():
    # Setup
    with open(os.path.join(data_dir(), 'jadn_v2.0_schema.json')) as f:
        js = json.load(f)
    yield js
    # Teardown


@pytest.mark.parametrize('in_path', Path(abs_dir(JADN_SCHEMA_DIR)).glob('*'), ids=lambda p: p.name)
def test_jadn_wellformed(in_path: str, json_schema) -> None:
    with open(os.path.join(JADN_SCHEMA_DIR, in_path)) as f:
        jadn_schema = json.load(f)
    validate(instance=jadn_schema, schema=json_schema)


@pytest.mark.parametrize('in_path', Path(abs_dir(JADN_BAD_SCHEMA_DIR)).glob('*'), ids=lambda p: p.name)
def test_jadn_wellformed_errs(in_path: str, json_schema) -> None:
    with open(os.path.join(JADN_BAD_SCHEMA_DIR, in_path)) as f:
        jadn_schema = json.load(f)
    with pytest.raises(ValidationError):
        validate(instance=jadn_schema, schema=json_schema)