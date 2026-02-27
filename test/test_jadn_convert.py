import glob
import os
import pytest
import sys
from jadn.core import JADNCore
from jadn.convert import JADN, JIDL, XASD, MD, ATREE, ERD
from jadn.config import style_args, style_fname

JADN_SCHEMA_DIR = 'apps/schemas/jadn'
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


def get_jadn_schemas():
    return glob.glob(f'{JADN_SCHEMA_DIR}/*')


@pytest.mark.parametrize('test', ['dump', 'load', 'round_trip'])
@pytest.mark.parametrize('schema_format', JADN_SCHEMA_CLASS)
@pytest.mark.parametrize('schema_path', get_jadn_schemas())
def test_jadn_schema_convert(session_data, schema_path, schema_format, test):
    schema_file  = os.path.split(schema_path)[1]
    fn = os.path.splitext(schema_file)[0]
    if test == 'dump':  # Convert JADN schema to equivalent formats
        in_pkg = JADN_SCHEMA_CLASS['jadn']()
        for out_format in JADN_SCHEMA_CLASS:
            schema_convert(fn, in_pkg, schema_path, out_format, session_data['output_dir'])
    elif test == 'load':    # Convert equivalent schema formats to JADN
        in_pkg = JADN_SCHEMA_CLASS[schema_format]()
        # in_file = os.path.join(fn, )
    elif test == 'round_trip':  # Verify lossless conversion from JADN to other format and back
        pass

    """
    with pytest.raises(NotImplementedError):
        in_pkg.schema_load(fp)
    """


def schema_convert(fn: str, in_pkg: 'JADNCore', in_path: str, out_fmt: str, out_dir: str) -> None:
    with open(in_path, 'r', encoding='utf8') as fp:
        in_pkg.schema_load(fp)
    out_pkg = JADN_SCHEMA_CLASS[out_fmt](in_pkg)
    style = style_args(out_pkg, out_fmt, '', CONFIG_FILE)  # need out_pkg
    if out_fmt in {'jadn', 'jidl', 'xasd', 'md', 'erd', 'atree'}:
        convert_out(fn, out_fmt, out_pkg, style, out_dir)
    else:
        with pytest.raises(NotImplementedError):
            convert_out(fn, out_fmt, out_pkg, style, out_dir)


def convert_out(fn: str, out_format: str, out_pkg: 'JADNCore', style: dict, out_dir: str) -> None:
    if out_dir:
        with open(os.path.join(out_dir, style_fname(fn, out_format, style)), 'w', encoding='utf8') as fp:
            out_pkg.schema_dump(fp, style)
    else:
        out_pkg.schema_dump(sys.stdout, style)
