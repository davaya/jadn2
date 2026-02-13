import json
from copy import deepcopy
from jadn.definitions import TypeName, CoreType, TypeOptions, Fields, \
    ItemID, ItemValue, FieldType, FieldOptions
from jadn.core import JADNCore, jadn_schema_loads
from numbers import Number
from typing import Any


# =========================================================
# JADN-format methods
# jadn_schema_loads static function is defined in jadn.core because it is needed
# to load METASCHEMA class variable
# =========================================================
class JADN(JADNCore):
    def style(self) -> dict:
        return {
            'strip': True
        }

    def schema_loads(self, jadn_str: str, source: str=None) -> None:
        schema = jadn_schema_loads(self, jadn_str)
        self.schema = schema
        self.source = source
        self.schema_load_finish()

    def schema_dumps(self, style: dict=None) -> str:
        """
        Return a schema instance as a string containing JADN data in JSON format

        Don't include empty metadata section
        Don't include empty trailing optional columns
        """

        def dump_tagstrings(opts: dict[str, str], ct: str) -> list[str]:
            """
            Serialize TypeOptions and FieldOptions dict as JSON list of tag-strings
            """

            def dictopt(v: dict[str, str]) -> str:
                kv = v.popitem()
                return chr(self.OPT_ID[kv[0]]) + kv[1]

            def strs(k: str, v: Any) -> str:
                v = '' if isinstance(v, bool) else\
                    v.hex() if isinstance(v, bytes) else\
                    dictopt(v) if isinstance(v, dict) else\
                    str(v)
                return chr(self.OPT_ID[k]) + str(v)

            return [strs(k, v) for k, v in sorted(opts.items(),  # Sort options to a canonical order to ease comparison
                                                  key=lambda k: self.OPT_ORDER[k[0]])]

        schema_copy = {'meta': x} if (x := self.schema.get('meta')) else {}
        schema_copy.update({'types': deepcopy(self.schema['types'])})

        for td in schema_copy['types']:
            # Clean up field defs
            for fd in td[Fields]:       # TODO: delete default=1 minOccurs/maxOccurs (until instance validation)
                if td[CoreType] == 'Enumerated':
                    fdef = [None, None, '']
                else:
                    fd[FieldOptions] = dump_tagstrings(fd[FieldOptions], fd[FieldType])
                    fdef = [None, None, None, [], '']
                while fd and fd[-1] == fdef[len(fd) - 1]:
                    fd.pop()
            # Clean up type def
            td[TypeOptions] = dump_tagstrings(td[TypeOptions], td[CoreType])
            tdef = [None, None, [], '', []]
            while td and td[-1] == tdef[len(td) - 1]:
                td.pop()

        return _pprint(schema_copy, strip=style.get('strip', True)) + '\n'


# ========================================================
# Support functions
# ========================================================

def _pprint(val: Any, level: int = 0, indent: int = 2, strip: bool = False) -> str:
    """
    Prettyprint a JSON-serialized JADN schema in compact format

    :param val: JSON string to be formatted
    :param level: Indentation level, default = 0 for external calls
    :param indent: Number of spaces per level, default = 2
    :param strip: Remove empty lines between types, boolean default = False
    :return: Formatted JSON string
    """
    if isinstance(val, (Number, type(''))):
        return json.dumps(val, ensure_ascii=False)

    sp = level * indent * ' '
    sp2 = (level + 1) * indent * ' '
    sep2 = ',\n' if strip else ',\n\n'
    if isinstance(val, dict):
        sep = ',\n' if level > 0 else sep2
        lines = sep.join(f'{sp2}"{k}": {_pprint(val[k], level + 1, indent, strip)}' for k in val)
        return f'{{\n{lines}\n{sp}}}'
    if isinstance(val, list):
        sep = ',\n' if level > 1 else sep2
        nest = val and isinstance(val[0], list)  # Not an empty list
        if nest:
            vals = [f"{sp2}{_pprint(v, level, indent, strip)}" for v in val]
            spn = level * indent * ' '
            return f"[\n{sep.join(vals)}\n{spn}]"
        vals = [f"{_pprint(v, level + 1, indent, strip)}" for v in val]
        return f"[{', '.join(vals)}]"
    return '???'

