import glob
import os
import pytest
import sys
from jadn.core import JADNCore
from jadn.convert import JADN, JIDL, XASD, MD, ATREE, ERD
from jadn.translate import JSCHEMA, PROTO, XSD
from jadn.config import style_args, style_fname
from pathlib import Path

JADN_SCHEMA_DIR = 'schemas/jadn'
ABSTRACT_SCHEMA_DIR = 'schemas/abstract'
CONCRETE_SCHEMA_DIR = 'schemas/concrete'
CONFIG_FILE = 'apps/jadn_config.json'
JADN_SCHEMA_CLASS = {
    'jadn': JADN,
    'jidl': JIDL,
    'xasd': XASD,
    'md': MD,
    # 'html': HTML,
    # 'dot': GRAPH_VIZ,
    # 'puml': PLANT_UML,
    'erd': ERD,
    'atree': ATREE,
}
CONCRETE_SCHEMA_CLASS = {
    'json': JSCHEMA,
    'proto': PROTO,
    'xsd': XSD,
}

SCHEMA_CLASS = JADN_SCHEMA_CLASS | CONCRETE_SCHEMA_CLASS


def schema_convert(session_data: dict, in_path: str, out_format: str, round_trip: str) -> ((str | bytes), JADNCore):
    in_fn = os.path.split(in_path)[1]
    in_ext = os.path.splitext(in_fn)[1].lstrip('.')
    assert in_ext in set(SCHEMA_CLASS), f'Unsupported file type {in_path}'
    in_pkg = SCHEMA_CLASS[in_ext]()
    if in_ext in {'erd', 'atree'}:
        return '', in_pkg
    with open(in_path, 'r', encoding='utf8') as fp:
        in_pkg.schema_load(fp)
    out_path = os.path.join(session_data['output_dir'], in_fn.replace('.', '_') + f'.{out_format}')
    out_pkg = SCHEMA_CLASS[out_format](in_pkg)
    style = style_args(out_pkg,'', CONFIG_FILE)
    with open(out_path, 'w', encoding='utf8') as fp:
        schema_msg = out_pkg.schema_dump(fp, style)
    return schema_msg, in_pkg


@pytest.mark.parametrize('round_trip', ['', 'jadn'])
@pytest.mark.parametrize('out_format', JADN_SCHEMA_CLASS)
@pytest.mark.parametrize('in_path', Path(JADN_SCHEMA_DIR).glob('*'), ids=lambda p: p.name)
def test_jadn_schema_convert(session_data: dict, in_path: str, out_format: str, round_trip: str):
    """
    Convert native JADN schema to equivalent alternate JADN format
    If round_trip is "jadn", convert alternate format back to native JADN and compare to original
    """
    schema_msg, in_pkg = schema_convert(session_data, in_path, out_format, round_trip)

    if round_trip == 'jadn':
        check_pkg = JADN_SCHEMA_CLASS[out_format]()
        if out_format in {'erd', 'atree'}:
            with pytest.raises(NotImplementedError):
                check_pkg.schema_loads(schema_msg)
        else:
            check_pkg.schema_loads(schema_msg)
            assert check_pkg.schema == in_pkg.schema


@pytest.mark.parametrize('out_format', ['jadn'])
@pytest.mark.parametrize('in_path', Path(ABSTRACT_SCHEMA_DIR).glob('*'), ids=lambda p: p.name)
def test_abstract_schema_convert(session_data, in_path, out_format):
    """
    Convert JADN Schema in alternate format to native JADN format
    """
    schema_convert(session_data, in_path, out_format, round_trip='jadn')


@pytest.mark.parametrize('out_format', CONCRETE_SCHEMA_CLASS)
@pytest.mark.parametrize('in_path', Path(JADN_SCHEMA_DIR).glob('*'), ids=lambda p: p.name)
def test_jadn_schema_translate_out(session_data: dict, in_path: str, out_format: str):
    """
    Convert native JADN schema to equivalent alternate JADN format
    """
    schema_msg, in_pkg = schema_convert(session_data, in_path, out_format, '')


@pytest.mark.parametrize('out_format', {'jadn'})
@pytest.mark.parametrize('in_path', Path(CONCRETE_SCHEMA_DIR).glob('*'), ids=lambda p: p.name)
def test_jadn_schema_translate_in(session_data: dict, in_path: str, out_format: str):
    """
    Convert native JADN schema to equivalent alternate JADN format
    """
    schema_msg, in_pkg = schema_convert(session_data, in_path, out_format, '')
