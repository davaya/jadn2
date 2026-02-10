import os
import sys
from jadn.convert import JADN, JIDL, XASD, MD, ATREE, ERD
from jadn.translate import JSCHEMA, XSD, CDDL, PROTO, XETO
from jadn.config import style_args, style_fname

SCHEMA_DIR = '../apps/schemas'
CONFIG_FILE = '../apps/jadn_config.json'
OUT_DIR = 'Out'
SCHEMA_CLASS = {
    'jadn': JADN,
    'jidl': JIDL,
    'xasd': XASD,
    'md': MD,
    'erd': ERD,
    'atree': ATREE,
    'json': JSCHEMA,
    'xsd': XSD,
    'cddl': CDDL,
    'proto': PROTO,
    'xeto': XETO,
}

def test_schema_convert():
    if OUT_DIR:
        os.makedirs(OUT_DIR, exist_ok=True)

    for schema_file in os.listdir(SCHEMA_DIR):
        fn, ext = os.path.splitext(schema_file)
        ext = ext.lstrip('.')
        if ext in SCHEMA_CLASS:     # Ignore directories and non-schema files
            if (in_pkg := SCHEMA_CLASS[ext]()) and 'schema_loads' in dir(in_pkg):  # Input format has a load method
                with open(os.path.join(SCHEMA_DIR, schema_file), 'r') as fp:
                    in_pkg.schema_load(fp)
            else:
                assert False, f'Input format {ext} not supported.'

            for out_format in SCHEMA_CLASS:
                out_pkg = SCHEMA_CLASS[out_format](in_pkg)
                style = style_args(out_pkg, out_format, '',  CONFIG_FILE)  # need out_pkg
                if OUT_DIR:
                    with open(os.path.join(OUT_DIR, style_fname(fn, out_format, style)), 'w', encoding='utf8') as fp:
                        out_pkg.schema_dump(fp, style)
                else:
                    out_pkg.schema_dump(sys.stdout, style)
        else:
            print(f'Unknown input format "{ext}" -- ignored')

