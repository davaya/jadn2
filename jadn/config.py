import json
from jadn import JADN


def style_args(pkg: JADN, format: str, args: str) -> dict:
    style = json.loads('{' + args + '}')
    return style
