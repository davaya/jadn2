import os
import pytest
from jadn.convert import JADN, JIDL, XASD, MD, ATREE, ERD
from jadn.translate import JSCHEMA, XSD, CDDL, PROTO, XETO
from jadn.config import style_args

SCHEMA_DIR = 'apps/schemas'
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
                style = style_args(out_format, '', '', '')  # need out_pkg
                out_pkg = schema_convert(in_pkg, out_format, style)



def convert_schema(self, out_pkg, style: dict=None, out_format: str, style_cmd: str, path: str, in_file: str, out_dir: str) -> None:


    if ext in class_ and (pkg := class_[ext]()) and 'schema_loads' in dir(pkg):     # Input format has a load method
    # if (pkg := class_.get(ext)()) and 'schema_loads' in dir(pkg):   # Input format has a load method
        # Read schema literal into information value
        with open(os.path.join(path, in_file), 'r') as fp:
            pkg.schema_load(fp)

        # Validate JADN information value against JADN metaschema
        pkg.schema_validate()

        # Serialize information value to schema literal in output format
        if out_format in class_:
            style = style_args(class_[out_format](), out_format, style_cmd, CONFIG)    # style from format, config, args
            if out_dir:
                with open(os.path.join(out_dir, style_fname(fn, out_format, style)), 'w', encoding='utf8') as fp:
                    class_[out_format]().schema_dump(fp, pkg, style)
            else:
                class_[out_format]().schema_dump(sys.stdout, pkg, style)
        else:
            print(f'Unknown output format "{out_format}"')
            sys.exit(2)
    else:
        print(f'Unknown input format "{ext}" -- ignored')
