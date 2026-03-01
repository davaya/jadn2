import glob
import os
import pytest
import sys
from jadn.core import JADNCore
from jadn.convert import JADN, JIDL, XASD, MD, ATREE, ERD
from jadn.config import style_args, style_fname

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


def get_files(in_dir: str) -> list[str]:
    return glob.glob(f'{in_dir}/*')


@pytest.mark.parametrize('round_trip', ['', 'jadn'])
@pytest.mark.parametrize('out_format', JADN_SCHEMA_CLASS)
@pytest.mark.parametrize(' in_path', get_files(JADN_SCHEMA_DIR))
def test_jadn_schema_convert(session_data, in_path, out_format, round_trip):
    """
    Convert native JADN schema to equivalent alternate JADN format
    """

    in_ext = os.path.splitext(in_path)[1].lstrip('.')
    in_pkg = JADN_SCHEMA_CLASS[in_ext]()
    with open(in_path, 'r', encoding='utf8') as fp:
        in_pkg.schema_load(fp)
    out_path = os.path.join(session_data['output_dir'], in_ext + f'.{out_format}')
    out_pkg = JADN_SCHEMA_CLASS[out_format](in_pkg)
    style = style_args(out_pkg,'', CONFIG_FILE)
    with open(out_path, 'w', encoding='utf8') as fp:
        schema_str = out_pkg.schema_dump(fp, style)

    if round_trip == 'jadn':
        pass


@pytest.mark.parametrize('schema_path', get_files(ABSTRACT_SCHEMA_DIR))
def test_abstract_schema_convert(schema_path):
    """
    Convert JADN Schema in alternate format to native JADN format
    """
    pass


@pytest.mark.parametrize('schema_path', get_files(CONCRETE_SCHEMA_DIR))
def test_concrete_schema_convert(schema_path):
    pass


    """
    with pytest.raises(NotImplementedError):
        in_pkg.schema_load(fp)
    """

"""
def schema_convert(fn: str, in_pkg: 'JADNCore', in_path: str, out_fmt: str, out_dir: str) -> JADNCore:
    with open(in_path, 'r', encoding='utf8') as fp:
        in_pkg.schema_load(fp)
    out_pkg = JADN_SCHEMA_CLASS[out_fmt](in_pkg)
    style = style_args(out_pkg, out_fmt, '', CONFIG_FILE)  # need out_pkg
    if out_fmt in {'jadn', 'jidl', 'xasd', 'md', 'erd', 'atree'}:
        convert_out(fn, out_fmt, out_pkg, style, out_dir)
    else:
        with pytest.raises(NotImplementedError):
            convert_out(fn, out_fmt, out_pkg, style, out_dir)
    return out_pkg
"""

def convert_out(fn: str, out_format: str, out_pkg: 'JADNCore', style: dict, out_dir: str) -> None:
    if out_dir:
        with open(os.path.join(out_dir, style_fname(fn, out_format, style)), 'w', encoding='utf8') as fp:
            out_pkg.schema_dump(fp, style)
    else:
        out_pkg.schema_dump(sys.stdout, style)
