import argparse
import sys
import os
from jadn import JADN, add_methods
from jadn.config import style_args, style_fname
from jadn.convert import jidl_rw, xasd_rw, md_rw, erd_w
from jadn.translate import jschema_rw, xsd_rw, cddl_rw, proto_rw, xeto_rw

add_methods(jidl_rw)
add_methods(xasd_rw)
add_methods(md_rw)
add_methods(erd_w)
add_methods(jschema_rw)
add_methods(xsd_rw)
add_methods(cddl_rw)
add_methods(proto_rw)
add_methods(xeto_rw)

CONFIG = 'jadn_config.json'


def convert_file(pkg: JADN, format: str, style: str, path: str, infile: str, outdir: str) -> None:

    _load = {
        'jadn': pkg.jadn_load,
        'jidl': pkg.jidl_load,
        'xasd': pkg.xasd_load,
        'md':   pkg.md_load,
        'json': pkg.jschema_load,
        'xsd': pkg.xsd_load,
        'cddl': pkg.cddl_load,
        'proto': pkg.proto_load,
        'xeto': pkg.xeto_load,
    }

    _dump = {
        'jadn': pkg.jadn_dump,
        'jidl': pkg.jidl_dump,
        'xasd': pkg.xasd_dump,
        'md':   pkg.md_dump,
        'erd':  pkg.erd_dump,
        'json': pkg.jschema_dump,
        'xsd':  pkg.xsd_dump,
        'cddl': pkg.cddl_dump,
        'proto': pkg.proto_dump,
        'xeto': pkg.xeto_dump,
    }

    if outdir:
        print(infile)  # Don't print if destination is stdout

    # Read lexical value into information value
    fn, ext = os.path.splitext(infile)
    ext = ext.lstrip('.')
    if ext in (_load):
        with open(os.path.join(path, infile), 'r') as fp:
            _load[ext](fp)

    # Validate information value against IM
    pkg.validate()

    # Serialize information value to lexical value
    style = style_args(pkg, format, style, CONFIG)      # combine style from args with format defaults
    if format in _dump:
        if outdir:
            with open(os.path.join(outdir, style_fname(fn, format, style)), 'w', encoding='utf8') as fp:
                _dump[format](fp, style)
        else:
            _dump[format](sys.stdout, style)
    else:
        print(f'Unknown output format "{format}"')
        sys.exit(2)


def main(input: str, output_dir: str, format: str, style: str, recursive: bool) -> None:
    """
    Convert JADN schema among multiple formats

    Convert to or from equivalent formats
    Convert to presentation formats
    Translate JADN abstract schema to or from concrete schema languages
    """

    # print(f'Installed JADN version: {jadn.__version__}\n')
    pkg = JADN()

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if os.path.isdir(input):
        # If input is directory, process all files, including contained directories if recursive=True
        for path, dirs, files in os.walk(input):
            if not recursive:
                dirs.clear()
            for file in files:
                convert_file(pkg, format, style, path, file, output_dir)
    else:
        # Otherwise process the named input file
        path, file = os.path.split(input)
        try:
            convert_file(pkg, format, style, path, file, output_dir)
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
    parser.add_argument('schema')
    parser.add_argument('output_dir', nargs='?', default=None)
    args = parser.parse_args()
    if args.output_dir:
        print(args)     # Don't print info if output on stdout
    main(args.schema, args.output_dir, args.f, args.style, args.r)