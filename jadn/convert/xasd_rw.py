"""
Translate JADN to XML Abstract Schema Definition (XASD)
"""
from typing import TextIO, Union
from lxml import etree as ET
from jadn.definitions import (TypeName, CoreType, TypeOptions, TypeDesc, Fields, ItemID, ItemValue, ItemDesc,
                              FieldID, FieldName, FieldType, FieldDesc, FieldOptions, PYTHON_TYPES, DEFS)

class XASD:
    def xasd_loads(self, fp: TextIO) -> dict[str, dict | list]:
        tree = ET.parse(fp)
        root = tree.getroot()
        assert root.tag == 'Schema'
        meta = {}
        types = []
        for element in root:
            if element.tag == 'Metadata':
                meta = _get_meta(element)
            elif element.tag == 'Types':
                for el in element:
                    types.append(_get_type(el))
        return {'meta': meta, 'types': types}

    def xasd_load(self, fp: TextIO) -> dict:
        return self.xasd_loads(fp)

    def xasd_dumps(self, schema: dict) -> str:
        def aname(k: str) -> str:   # Mangle "format" attribute names to be valid XML
            return k.replace('/', '_')

        xasd = '<?xml version="1.0" encoding="UTF-8"?>\n<Schema>\n'
        if meta := schema['meta']:
            xasd += '  <Metadata\n'
            xasd += '\n'.join([f'{4*" "}{k}="{v}"' for k, v in meta.items() if isinstance(v, str)]) + '>\n'
            for k, v in meta.items():
                if k == 'roots':
                    xasd += f'{4 * " "}<{k.capitalize()}>\n'
                    for v in meta[k]:
                        xasd += f'{6 * " "}<TypeName>{v}</TypeName>\n'
                    xasd += f'{4 * " "}</{k.capitalize()}>\n'
                elif k == 'namespaces':
                    xasd += f'{4 * " "}<{k.capitalize()}>\n'
                    for v in meta[k]:
                        xasd += f'{6 * " "}<PrefixNs prefix="{v[0]}">{v[1]}</PrefixNs>\n'
                    xasd += f'{4 * " "}</{k.capitalize()}>\n'
                elif k == 'config':
                    xasd += f'{4 * " "}<{k.capitalize()}>\n'
                    for k2, v in meta[k].items():
                        xasd += f'{6 * " "}<{k2.strip("$")}>{v}</{k2.strip("$")}>\n'
                    xasd += f'{4 * " "}</{k.capitalize()}>\n'
        xasd += '  </Metadata>\n'
        xasd += '  <Types>\n'
        for td in schema['types']:
            (ln, end) = ('\n', '    ') if td[Fields] else ('', '')
            to = ''.join([f' {aname(k)}="{v}"' for k, v in td[TypeOptions].items()])
            xasd += f'{4*" "}<Type name="{td[TypeName]}" type="{td[CoreType]}"{to}>{td[TypeDesc]}{ln}'
            for fd in td[Fields]:
                if td[CoreType] == 'Enumerated':
                    xasd += f'{6*" "}<Item id="{fd[ItemID]}" value="{fd[ItemValue]}">{fd[ItemDesc]}</Item>\n'
                else:
                    fo = ''.join([f' {aname(k)}="{v}"' for k, v in fd[FieldOptions].items()])
                    xasd += f'{6*" "}<Field id="{fd[FieldID]}" name="{fd[FieldName]}" type="{fd[FieldType]}"{fo}>{fd[FieldDesc]}</Field>\n'
            xasd += f'{end}</Type>\n'
        xasd += '  </Types>\n'
        xasd += '</Schema>\n'
        return xasd

    def xasd_dump(self, schema: dict, fp: TextIO) -> None:
        fp.write(self.xasd_dumps(schema))


# ========================================================
# Support functions
# ========================================================

def _get_meta(el: ET.Element) -> dict:
    meta = {k: v for k, v in el.items()}
    for e in el:
        if e.tag == 'Roots':
            meta['roots'] = [v.text for v in e]
        elif e.tag == 'Namespaces':
            meta['namespaces'] = [[v.get('prefix'), v.text] for v in e]
        elif e.tag == 'Config':
            meta['config'] = {'$' + v.tag: v.text for v in e}
    return meta

def _get_type(e: ET.Element) -> list:
    def aname(k: str) -> str:   # un-mangle XML attribute name to /format
        return k.replace('_', '/')

    def atype(k: str, v: str) -> Union[bool, int, float, str]:
        return PYTHON_TYPES[DEFS.OPTS[DEFS.OPTX[k]][1]](v) if k in DEFS.OPTX else v

    def gettext(el: ET.Element) -> str:
        return el.text.strip() if el.text is not None else ''

    assert e.tag == 'Type'
    at = {aname(k): atype(k, v) for k, v in e.items()}
    fields = []
    for f in e:
        fa = {aname(k): atype(k, v) for k, v in f.items()}
        if f.tag == 'Field':
            fields.append([int(fa.pop('id')), fa.pop('name'), fa.pop('type'), fa, gettext(f)])
        elif f.tag == 'Item':
            fields.append([int(fa.pop('id')), fa.pop('value'), gettext(f)])

    type = [at.pop('name'), at.pop('type'), at, gettext(e), fields]
    return type


# =========================================================
# Diagnostics
# =========================================================
if __name__ == '__main__':
    pass
