import argparse
import os
from jadn.core import JADN
import jadn
from jadn.core import JADN
from jadn.convert import jidl, xasd
from jadn.definitions import TypeName, CoreType, TypeOptions, TypeDesc, Fields
from jadn.definitions import ItemID, ItemValue, ItemDesc
from jadn.definitions import FieldID, FieldName, FieldType, FieldOptions, FieldDesc

OUTPUT_DIR = 'Out'


def main(input: str, output_dir: str, fmt: str, recursive: bool) -> None:
    """
    Translate schema between JADN and equivalent formats
    """
    # print(f'Installed JADN version: {jadn.__version__}\n')
    os.makedirs(output_dir, exist_ok=True)
    sc = JADN()

    def convert(path: str, infile: str):
        fn, ext = os.path.splitext(infile)
        if ext in ('.jadn', '.jidl', '.xasd'):
            with open(os.path.join(path, infile)) as fp:
                schema = {
                    '.jadn': sc.load,
                    '.jidl': jidl_load,
                    '.xasd': xasd_load
                }[ext](fp)

            print(os.path.join(path, infile))
            print('\n'.join([f'{k:>15}: {v}' for k, v in analyze(check(schema)).items()]))

            if fmt in ('jadn', 'jidl', 'xasd', 'md', 'dot'):
                {
                    'jadn': dump,
                    'jidl': jidl_dump,
                    'xasd': xasd_dump,
                    'md': markdown_dump,
                    'dot': diagram_dump
                }[fmt](schema, os.path.join(OUTPUT_DIR, f'{fn}.{fmt}'))

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