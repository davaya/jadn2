import json
import os
from jadn import JADN


def style_args(pkg: JADN, format: str, args: str, config: str = '') -> dict:
    """
    Combine style options from command line options, user defaults file, and format-defined defaults

    :param pkg: JADN schema package instance
    :param format: name of serialized (lexical) format
    :param args: arguments from command line in a double-quoted string
    :param config: name of JSON configuration file containing default arguments per format
    """

    _style = {
        'jadn': pkg.jadn_style,
        'jidl': pkg.jidl_style,
        'xasd': pkg.xasd_style,
        'md': pkg.md_style,
        'erd': pkg.erd_style,
        'json': pkg.jschema_style,
        'xsd': pkg.xsd_style,
        'cddl': pkg.cddl_style,
        'proto': pkg.proto_style,
        'xeto': pkg.xeto_style,
    }

    def _fixbool(v: str) -> str | bool:
        return False if v.lower() == 'false' else True if v.lower() == 'true' else v

    format_opts = _style[format]()
    config_opts = {}
    if os.path.isfile(config):
        with open(config) as fp:
            config_opts = json.load(fp).get('style', {}).get(format, {})    # get args from "style" section
    assert not (x := set(config_opts) - set(format_opts)), f'Invalid style options {x} from {fp.name}'
    try:
        cli_opts = {(x := arg.split(':'))[0].strip(): _fixbool(x[1].strip()) for arg in args.split(',') if arg}
    except IndexError:
        err  = f'Options for format "{format}"\n'
        err += f'Class: {json.dumps(format_opts, indent=2)}\n'
        err += f'Configuration file "{config}": {json.dumps(config_opts, indent=2)}' if config_opts else ''
        assert False, err
    assert not (x := set(cli_opts) - set(format_opts)), f'Invalid style options {x}'
    return format_opts | config_opts | cli_opts


def style_fname(fname: str, format: str, style: dict) -> str:
    """
    Generate output filename based on style options for output format
    """
    if format == 'erd':
        fname += f'_{style["detail"][0]}{"a" if style["attributes"] else ""}'
        format = {'plantuml': 'puml', 'graphviz': 'dot'}[style['graph']]
    return f'{fname}.{format}'