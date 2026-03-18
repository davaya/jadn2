import glob
import os
import pytest
import sys
from jadn.core import JADNCore
from jadn.translate import JSCHEMA, XSD, CDDL, PROTO, XETO
from jadn.config import style_args, style_fname

SCHEMA_DIR = 'apps/schemas/concrete'
CONFIG_FILE = 'apps/jadn_config.json'
OUT_DIR = 'Out'
DATA_SCHEMA_CLASS = {
    'json': JSCHEMA,
    'xsd': XSD,
    'cddl': CDDL,
    'proto': PROTO,
    'xeto': XETO,
}


def get_input_files():
    return glob.glob(f'{SCHEMA_DIR}/*')

"""
@pytest.mark.parametrize('test', ['dump', 'load', 'round_trip'])
@pytest.mark.parametrize('schema_format', DATA_SCHEMA_CLASS)
@pytest.mark.parametrize('schema_path', get_input_files())
def test_jadn_schema_convert(schema_path, schema_format, test):
    schema_file  = os.path.split(schema_path)[1]
    fn, ext = os.path.splitext(schema_file)
    ext = ext.lstrip('.')
    if ext in DATA_SCHEMA_CLASS:     # Ignore directories and non-schema files
        if (in_pkg := DATA_SCHEMA_CLASS[ext]()):  # and 'schema_loads' in dir(in_pkg):  # Input format has a load method
            with open(schema_path, 'r') as fp:
                if ext in {'jadn', 'jidl', 'xasd', 'md', 'json'}:
                    in_pkg.schema_load(fp)
                    schema_convert(fn, in_pkg)
                else:
                    with pytest.raises(NotImplementedError):
                        in_pkg.schema_load(fp)
    else:
        print(f'\nUnknown input format "{ext}" -- ignored')
"""

def test_concrete_schema_translate(schema_path, schema_format):
    pass


def schema_convert(fn: str, in_pkg: 'JADNCore') -> None:
    for out_format in DATA_SCHEMA_CLASS:
        out_pkg = DATA_SCHEMA_CLASS[out_format](in_pkg)
        style = style_args(out_pkg, out_format, '', CONFIG_FILE)  # need out_pkg
        if out_format in {'jadn', 'jidl', 'xasd', 'md', 'erd', 'atree'}:
            convert_out(fn, out_format, out_pkg, style)
        else:
            with pytest.raises(NotImplementedError):
                convert_out(fn, out_format, out_pkg, style)


def convert_out(fn: str, out_format: str, out_pkg: 'JADNCore', style: dict) -> None:
    if OUT_DIR:
        with open(os.path.join(OUT_DIR, style_fname(fn, out_format, style)), 'w', encoding='utf8') as fp:
            out_pkg.schema_dump(fp, style)
    else:
        out_pkg.schema_dump(sys.stdout, style)
