import json

from jadn.core import data_dir
from jsonschema import validate
import os
import pytest

JADN_SCHEMA_DIR = 'schemas/jadn'
JADN_BAD_SCHEMA_DIR = 'schemas/jadn-errs'


@pytest.fixture(scope='session')
def json_schema():
    # Setup
    with open(os.path.join(data_dir(), 'jadn_v2.0_schema.json')) as f:
        js = json.load(f)
    yield js
    # Teardown


@pytest.mark.parametrize('in_path', os.listdir(JADN_SCHEMA_DIR))
def test_jadn_wellformed(in_path: str, json_schema) -> None:
    with open(os.path.join(JADN_SCHEMA_DIR, in_path)) as f:
        jadn_schema = json.load(f)
    validate(instance=jadn_schema, schema=json_schema)


@pytest.mark.parametrize('in_path', os.listdir(JADN_BAD_SCHEMA_DIR))
def test_jadn_wellformed_errs(in_path: str, json_schema) -> None:
    with open(os.path.join(JADN_BAD_SCHEMA_DIR, in_path)) as f:
        jadn_schema = json.load(f)
    validate(instance=jadn_schema, schema=json_schema)
