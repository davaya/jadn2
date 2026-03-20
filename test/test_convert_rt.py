import os
import pytest
from jadn.core import JADNCore
from jadn.convert import JADN, JIDL, XASD, MD, ATREE, ERD
from jadn.style import style_args, style_fname
from pathlib import Path

OUT_DIR = 'test/Out'
JADN_SCHEMA_DIR = 'schemas/jadn'
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

def abs_dir(relative_path: str) -> Path:
    p = Path(__file__).parts
    parts = p[:p.index('test')] + Path(relative_path).parts
    return Path(*parts)


def schema_convert(schema_classes: dict, in_path: Path, out_format: str) -> ((str | bytes), JADNCore):
    """
    
    :param schema_classes:
    :type schema_classes:
    :param in_path:
    :type in_path:
    :param out_format:
    :type out_format:
    :return:
    :rtype:
    """
    sclasses = schema_classes | {'jadn': JADN}
    in_fn = os.path.split(in_path)[1]
    in_ext = os.path.splitext(in_fn)[1].lstrip('.')
    assert in_ext in set(sclasses), f'Unsupported file type {in_path}'
    in_pkg = sclasses[in_ext]()
    with open(in_path, 'r', encoding='utf8') as fp:
        in_pkg.schema_load(fp)
    out_path = os.path.join(abs_dir(OUT_DIR), in_fn.replace('.', '_') + f'.{out_format}')
    out_pkg = sclasses[out_format](in_pkg)
    style = style_args(out_pkg,'', str(abs_dir(CONFIG_FILE)))
    with open(out_path, 'w', encoding='utf8') as fp:
        schema_msg = out_pkg.schema_dump(fp, style)
    return schema_msg, in_pkg


@pytest.mark.parametrize('round_trip', ['', 'jadn'])
@pytest.mark.parametrize('out_format', JADN_SCHEMA_CLASS)
@pytest.mark.parametrize('in_path', Path(abs_dir(JADN_SCHEMA_DIR)).glob('*'), ids=lambda p: p.name)
def test_jadn_schema_convert(session_data: dict, in_path: str, out_format: str, round_trip: str):
    """
    Convert native JADN schema to equivalent alternate JADN format
    If round_trip is "jadn", convert alternate format back to native JADN and compare to original
    """
    schema_msg, in_pkg = schema_convert(JADN_SCHEMA_CLASS, in_path, out_format)

    if round_trip == 'jadn':
        check_pkg = JADN_SCHEMA_CLASS[out_format]()
        if out_format in {'erd', 'atree'}:  # Verify that write-only (display) formats raise error on load
            with pytest.raises(NotImplementedError):
                check_pkg.schema_loads(schema_msg)
        else:
            check_pkg.schema_loads(schema_msg)  # Verify lossless conversion to and from test format
            assert check_pkg.schema == in_pkg.schema
