import json
from jadn import JADN


def style_args(schema: JADN, format: str, args: str) -> dict:
    style = json.loads('{' + args + '}')
    return style
