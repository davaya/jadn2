import argparse
import jadn
import sys
import os

OUTPUT_DIR = None


def main(input: str, output_dir: str, format: str, recursive: bool) -> None:
    """
    Translate schema between JADN and equivalent formats
    """
    def _dump(schema, fp):
        {
            'jadn': sc.json_dump,
            'jidl': sc.jidl_dump,
            'xasd': sc.xasd_dump,
            # 'md': markdown_dump,
            # 'dot': diagram_dump
        }[format](schema, fp)

    # print(f'Installed JADN version: {jadn.__version__}\n')
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    sc = jadn.JADN()

    def convert(path: str, infile: str):
        if output_dir:
            print(infile)
        fn, ext = os.path.splitext(infile)
        if ext in ('.jadn', '.jidl', '.xasd'):
            with open(os.path.join(path, infile), 'r') as fp:
                schema = {
                    '.jadn': sc.json_load,
                    '.jidl': sc.jidl_load,
                    '.xasd': sc.xasd_load
                }[ext](fp)

            if format in ('jadn', 'jidl', 'xasd', 'md', 'dot'):
                if output_dir:
                    with open(os.path.join(output_dir, f'{fn}.{format}'), 'w', encoding='utf8') as fp:
                        _dump(schema, fp)
                else:
                    _dump(schema, sys.stdout)

    if os.path.isdir(input):
        for path, dirs, files in os.walk(input):
            if not recursive:
                dirs.clear()
            for file in files:
                convert(path, file)
    else:
        path, file = os.path.split(input)
        try:
            convert(path, file)
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Convert JADN schemas to a different format.')
    parser.add_argument('-f', metavar='format', default='jadn',
                        help='output format')
    parser.add_argument('-r', action='store_true', help='recursive directory search')
    parser.add_argument('schema')
    parser.add_argument('output', nargs='?', default=OUTPUT_DIR)
    args = parser.parse_args()
    if args.output:
        print(args)     # Don't print info if output on stdout
    main(args.schema, args.output, args.f, args.r)