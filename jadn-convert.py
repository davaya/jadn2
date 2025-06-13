import argparse
import os
import jadn

OUTPUT_DIR = 'Out'


def main(input: str, output_dir: str, fmt: str, recursive: bool) -> None:
    """
    Translate schema between JADN and equivalent formats
    """
    # print(f'Installed JADN version: {jadn.__version__}\n')
    os.makedirs(output_dir, exist_ok=True)
    sc = jadn.JADN()

    def convert(path: str, infile: str):
        fn, ext = os.path.splitext(infile)
        if ext in ('.jadn', '.jidl', '.xasd'):
            with open(os.path.join(path, infile), 'r') as fp:
                schema = {
                    '.jadn': sc.json_load,
                    '.jidl': sc.jidl_load,
                    '.xasd': sc.xasd_load
                }[ext](fp)

            print(fp.name)

            if fmt in ('jadn', 'jidl', 'xasd', 'md', 'dot'):
                with open(os.path.join(OUTPUT_DIR, f'{fn}.{fmt}'), 'w', encoding='utf8') as fp:
                    {
                        'jadn': sc.json_dump,
                        'jidl': sc.jidl_dump,
                        'xasd': sc.xasd_dump,
                        # 'md': markdown_dump,
                        # 'dot': diagram_dump
                    }[fmt](schema, fp)

    if os.path.isfile(input):
        path, file = os.path.split(input)
        convert(path, file)
    else:
        for path, dirs, files in os.walk(input):
            if not recursive:
                dirs.clear()
            for file in files:
                convert(path, file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Convert JADN schemas to a different format.')
    parser.add_argument('-o', metavar='fmt', default='jadn',
                        help='output format')
    parser.add_argument('-r', action='store_true', help='recursive directory search')
    parser.add_argument('schema_dir')
    parser.add_argument('output_dir', nargs='?', default=OUTPUT_DIR)
    args = parser.parse_args()
    print(args)
    main(args.schema_dir, args.output_dir, args.o, args.r)