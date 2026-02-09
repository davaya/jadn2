import argparse
import sys
import os
from jadn.config import style_args, style_fname
from jadn.convert import JADN, JIDL, XASD, MD, ATREE, ERD
from jadn.translate import JSCHEMA, XSD, CDDL, PROTO, XETO

CONFIG = 'jadn_config.json'


def convert_schema(out_format: str, style_cmd: str, path: str, in_file: str, out_dir: str) -> None:
    class_ = {
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

    if out_dir:
        print(in_file)  # Don't print filename if destination is stdout

    fn, ext = os.path.splitext(in_file)
    ext = ext.lstrip('.')
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


def jadn_convert(input: str, out_dir: str, out_format: str, style: str, recursive: bool) -> None:
    """
    Convert JADN schema among multiple formats

    Convert to or from equivalent formats
    Convert to presentation formats
    Translate JADN abstract schema to or from concrete schema languages
    """

    # print(f'Installed JADN version: {jadn.__version__}\n')

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    if os.path.isdir(input):
        # If input is directory, process all files, including contained directories if recursive=True
        for in_path, dirs, files in os.walk(input):
            if not recursive:
                dirs.clear()
            for in_file in files:
                convert_schema(out_format, style, in_path, in_file, out_dir)
    else:
        # Otherwise process the named input file
        in_path, in_file = os.path.split(input)
        try:
            convert_schema(out_format, style, in_path, in_file, out_dir)
        except (FileNotFoundError, AssertionError) as e:
            print(e, file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Convert JADN schemas to a specified format.')
    parser.add_argument('-f', metavar='format', default='jadn',
                        help='output format')
    parser.add_argument('-r', action='store_true', help='recursive directory search')
    parser.add_argument('--style', default='', help='serialization style options')
    parser.add_argument('input', help='input filename or directory')
    parser.add_argument('out_dir', nargs='?', default=None)
    args = parser.parse_args()
    if args.out_dir:
        print(args)     # Don't print command line args if schema output is stdout
    jadn_convert(args.input, args.out_dir, args.f, args.style, args.r)
