import json
import os
from jadn import JADN


def style_args(pkg: JADN, format: str, args: str, config: str = '') -> dict:
    """
    Combine style options from command line options, user defaults file, and format-defined defaults

    :param pkg: JADN schema package instance
    :param format: serialized (lexical) format
    :param args: arguments from command line
    :param config: configuration file name containing default arguments
    """

    _style = {
        'jadn': pkg.json_style,
        'jidl': pkg.jidl_style,
        'xasd': pkg.xasd_style,
        'md': pkg.md_style,
        'erd': pkg.erd_style,
        'jschema': pkg.jschema_style,
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
        cli_opts = {(x := arg.split(':'))[0].strip(): _fixbool(x[1].strip()) for arg in args.split(',')}
    except IndexError:
        assert False, (f'Options for format "{format}"\n' +
            f'Class: {json.dumps(format_opts, indent=2)}\n' +
            (f'Configuration file "{fp.name}": {json.dumps(config_opts, indent=2)}') if config_opts else '')
    assert not (x := set(cli_opts) - set(format_opts)), f'Invalid style options {x}'
    return format_opts | config_opts | cli_opts
