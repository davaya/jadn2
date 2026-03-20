import argparse
import sys
import os
from jadn.style import style_args, style_fname
from jadn.convert import JADN, JIDL, XASD, MD, ATREE, ERD
from jadn.translate import JSCHEMA, XSD, CDDL, PROTO, XETO

CONFIG = 'jadn_config.json'


def convert_schema(in_path: str, out_dir: str, out_fmt: str, style_cmd: str) -> None:
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

    in_file = os.path.split(in_path)[1]
    if out_dir:
        print(in_file)  # Don't print filename if destination is stdout

    fn, ext = os.path.splitext(in_file)
    ext = ext.lstrip('.')
    if ext in class_ and (in_pkg := class_[ext]()) and 'schema_loads' in dir(in_pkg):     # Input format has a load method
        # Read schema literal into information value
        with open(in_path, 'r') as fp:
            in_pkg.schema_load(fp)

        # Validate JADN information value against JADN metaschema
        in_pkg.schema_validate()

        # Serialize information value to schema literal in output format
        if out_fmt in class_:
            style = style_args(class_[out_fmt](), style_cmd, CONFIG)    # style from format, config, args
            if out_dir:
                with open(os.path.join(out_dir, style_fname(fn, out_fmt, style)), 'w', encoding='utf8') as fp:
                    class_[out_fmt](in_pkg).schema_dump(fp, style)
            else:
                class_[out_fmt](in_pkg).schema_dump(sys.stdout, style)
        else:
            print(f'Unknown output format "{out_fmt}"')
            sys.exit(2)
    else:
        print(f'Unknown input format "{ext}" -- ignored')


def jadn_convert(input: str, out_dir: str, out_fmt: str, style: str, recursive: bool) -> None:
    """
    Convert JADN schema among multiple formats

    Convert to or from equivalent formats
    Convert to presentation formats
    Translate JADN abstract schema to or from concrete schema languages
    """

    # print(f'Installed JADN version: {jadn.__version__}\n')
    if os.path.isdir(input):
        # If input is directory, process all files, including contained directories if recursive=True
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            for in_dir, dirs, files in os.walk(input):
                if not recursive:
                    dirs.clear()
                for in_file in files:
                    convert_schema(os.path.join(in_dir, in_file), out_dir, out_fmt, style)
        else:
            assert False, f'Input {input} is a directory but output directory is not specified'
    else:
        # Otherwise process the named input file
        try:
            convert_schema(input, out_dir, out_fmt, style)
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
        print(args)     # Don't print command line args if output to stdout
    jadn_convert(args.input, args.out_dir, args.f, args.style, args.r)
